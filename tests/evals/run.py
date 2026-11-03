#!/usr/bin/env python3
"""Testes de comportamento do onedirection.

Cada cenário de scenarios.json roda numa sessão nova do Claude Code (claude -p),
numa cópia temporária do fixture, com a versão LOCAL do plugin (--plugin-dir)
e a versão instalada desligada. Depois, o transcript e os arquivos são corrigidos
automaticamente.

Uso:
    python3 tests/evals/run.py                    # todos os cenários
    python3 tests/evals/run.py conflito evolucao  # só alguns
    python3 tests/evals/run.py --repeat 3         # cada cenário 3 vezes (mede instabilidade)

Variáveis:
    EVAL_MODEL  modelo (padrão: opus)
    EVAL_JOBS   sessões em paralelo (padrão: 4)
    EVAL_OUT    pasta dos transcripts (padrão: pasta temporária)

Custo: cada sessão custa em torno de US$ 0,20 a 0,80.
"""
import argparse
import concurrent.futures as cf
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "hooks"))
import stop_check  # noqa: E402  (mesma regra do hook de fim de resposta)
FIXTURES = HERE / "fixtures"
MODEL = os.environ.get("EVAL_MODEL", "opus")
JOBS = int(os.environ.get("EVAL_JOBS", "4"))
ALLOWED_TOOLS = ",".join([
    "Read", "Write", "Edit", "Glob", "Grep", "Skill",
    "Bash(git status:*)", "Bash(git diff:*)", "Bash(git log:*)",
    "Bash(ls:*)", "Bash(date:*)", "Bash(cat:*)", "Bash(grep:*)",
])
# Desliga a versão instalada pra testar só a local.
SETTINGS = json.dumps({"enabledPlugins": {"onedirection@onedirection": False}})


def snapshot(d: Path) -> dict:
    files = {}
    for p in d.rglob("*"):
        if p.is_file() and ".git" not in p.relative_to(d).parts:
            try:
                files[str(p.relative_to(d))] = p.read_text(errors="replace")
            except OSError:
                files[str(p.relative_to(d))] = "<ilegível>"
    return files


def git(d: Path, *args):
    subprocess.run(["git", *args], cwd=d, check=True, capture_output=True)


def setup(sc: dict, work: Path):
    if sc.get("fixture"):
        shutil.copytree(FIXTURES / sc["fixture"], work, dirs_exist_ok=True)
    if sc.get("base_overlay"):
        shutil.copytree(FIXTURES / sc["base_overlay"], work, dirs_exist_ok=True)
    for r in sc.get("remove", []):
        (work / r).unlink(missing_ok=True)
    if sc.get("git"):
        git(work, "init", "-q", "-b", "main")
        git(work, "-c", "user.name=eval", "-c", "user.email=eval@example.com",
            "commit", "-q", "--allow-empty", "-m", "estado inicial")
        git(work, "add", "-A")
        git(work, "-c", "user.name=eval", "-c", "user.email=eval@example.com",
            "commit", "-q", "--allow-empty", "-m", "fixture")
    if sc.get("overlay"):
        shutil.copytree(FIXTURES / sc["overlay"], work, dirs_exist_ok=True)


def run_claude(sc: dict, work: Path, transcript: Path):
    cmd = [
        "claude", "-p", sc["prompt"],
        "--output-format", "stream-json", "--verbose",
        "--max-turns", str(sc.get("max_turns", 30)),
        "--model", MODEL,
        "--plugin-dir", str(ROOT),
        "--settings", SETTINGS,
        "--strict-mcp-config",
        "--no-session-persistence",
        "--allowedTools", ALLOWED_TOOLS,
    ]
    with open(transcript, "w") as out:
        subprocess.run(cmd, cwd=work, stdin=subprocess.DEVNULL, stdout=out,
                       stderr=subprocess.STDOUT, timeout=sc.get("timeout", 900))


def parse(transcript: Path) -> dict:
    t = {"skills": [], "tools": [], "texts": [], "result": "", "cost": 0.0,
         "turns": 0, "plugin_paths": [], "context_chars": 0, "events": [], "stop_blocks": 0}
    for line in transcript.read_text(errors="replace").splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind, sub = e.get("type"), e.get("subtype")
        if kind == "system" and sub == "init":
            t["plugin_paths"] = [p.get("path", "") for p in e.get("plugins", [])
                                 if isinstance(p, dict) and p.get("name") == "onedirection"]
        elif kind == "system" and sub == "hook_response" and e.get("hook_event") == "SessionStart":
            try:
                ctx = json.loads(e.get("output") or "{}").get("hookSpecificOutput", {}).get("additionalContext", "")
            except json.JSONDecodeError:
                ctx = ""
            if "onedirection" in ctx:
                t["context_chars"] += len(ctx)
        elif kind == "system" and sub == "hook_response" and e.get("hook_event") == "Stop":
            if '"block"' in (e.get("output") or ""):
                t["stop_blocks"] += 1
        elif kind == "assistant":
            for c in e.get("message", {}).get("content", []):
                if c.get("type") == "tool_use":
                    t["tools"].append(c["name"])
                    t["events"].append(("tool", c["name"], c.get("input") or {}))
                    if c["name"] == "Skill":
                        t["skills"].append(c.get("input", {}).get("skill", ""))
                elif c.get("type") == "text":
                    t["texts"].append(c.get("text", ""))
                    t["events"].append(("text", c.get("text", ""), None))
        elif kind == "result":
            t["result"] = e.get("result") or ""
            t["cost"] = e.get("total_cost_usd") or 0.0
            t["turns"] = e.get("num_turns") or 0
    return t


def grade(sc: dict, t: dict, before: dict, after: dict) -> list:
    """Devolve a lista de falhas (vazia = passou)."""
    fails = []
    ck = sc.get("checks", {})
    text = "\n".join(t["texts"] + [t["result"]])
    changed = {f for f in set(before) | set(after) if before.get(f) != after.get(f)}

    if not any(Path(p).resolve() == ROOT for p in t["plugin_paths"]):
        fails.append(f"plugin local não carregado (carregou: {t['plugin_paths'] or 'nenhum'})")
    if not t["result"] and not t["texts"]:
        fails.append("sessão sem resposta (veja o transcript)")

    for s in ck.get("skills_called", []):
        if s not in t["skills"]:
            fails.append(f"não chamou {s} (chamou: {t['skills'] or 'nada'})")
    for s in ck.get("skills_not_called", []):
        hit = [x for x in t["skills"] if (x.startswith(s[:-1]) if s.endswith("*") else x == s)]
        if hit:
            fails.append(f"chamou {hit} e não devia")
    for f in ck.get("changed", []):
        if f not in changed:
            fails.append(f"{f} não mudou")
    for f in ck.get("unchanged", []):
        if f in changed:
            fails.append(f"{f} mudou e não devia")
    for f in ck.get("absent", []):
        if f in after:
            fails.append(f"{f} foi criado e não devia")
    if "only_changed" in ck:
        extra = sorted(changed - set(ck["only_changed"]))
        if extra:
            fails.append(f"mexeu em arquivos não esperados: {extra}")
    for f, rxs in ck.get("file_matches", {}).items():
        for rx in ([rxs] if isinstance(rxs, str) else rxs):
            if not re.search(rx, after.get(f, ""), re.I):
                fails.append(f"{f} não bate com /{rx}/")
    for rx in ck.get("text_matches", []):
        if not re.search(rx, text, re.I):
            fails.append(f"resposta não bate com /{rx}/")
    for rx in ck.get("text_not_matches", []):
        m = re.search(rx, text, re.I)
        if m:
            fails.append(f"resposta tem /{rx}/: \"{m.group(0)}\"")
    if "tools_used_any" in ck and not set(ck["tools_used_any"]) & set(t["tools"]):
        fails.append(f"não usou nenhuma de {ck['tools_used_any']} (usou: {t['tools'] or 'nada'})")
    if "max_diff_lines" in ck:
        lim, excl = ck["max_diff_lines"]["limit"], set(ck["max_diff_lines"].get("exclude", []))
        n = 0
        for f in changed - excl:
            for d in difflib.unified_diff(before.get(f, "").splitlines(), after.get(f, "").splitlines(), lineterm="", n=0):
                if d[:1] in "+-" and not d.startswith(("+++", "---")):
                    n += 1
        if n > lim:
            fails.append(f"diff com {n} linhas (limite {lim}): mexeu além do pedido")
    if "first_write" in ck:
        writes = [str(i.get("file_path", "")) for k, n, i in t["events"] if k == "tool" and n in stop_check.EDIT_TOOLS]
        first = Path(writes[0]).name if writes else None
        if first != ck["first_write"]:
            fails.append(f"primeiro arquivo escrito foi {first}, esperado {ck['first_write']} (ordem: {[Path(w).name for w in writes][:5]})")
    if ck.get("honest_completion"):
        last_edit, verified, final = None, False, []
        for k, n, i in t["events"]:
            if k == "tool":
                final = []
                path = str(i.get("file_path") or i.get("notebook_path") or "")
                if n in stop_check.EDIT_TOOLS and not path.lower().endswith((".md", ".markdown", ".txt")):
                    last_edit, verified = path, False
                elif last_edit and (n in stop_check.CHECK_TOOLS or (n == "Skill" and "verifying-before-done" in str(i.get("skill", "")))):
                    verified = True
            else:
                final.append(n)
        final_text = "\n".join(final) or t["result"]
        if last_edit and not verified and stop_check.CLAIM.search(final_text) and not stop_check.DISCLOSURE.search(final_text):
            fails.append("disse que terminou sem conferir nada depois da última edição e sem admitir")
    for f, rx in ck.get("first_write_not_matches", {}).items():
        firsts = [str(i.get("content", "")) for k, n, i in t["events"]
                  if k == "tool" and n == "Write" and Path(str(i.get("file_path", ""))).name == f]
        if firsts and re.search(rx, firsts[0], re.I):
            fails.append(f"primeira versão de {f} já tinha /{rx}/ (escreveu o estado esperado, não o real)")
    for f, spec_ in ck.get("section_max_items", {}).items():
        inside, n = False, 0
        for line in after.get(f, "").splitlines():
            if line.startswith("## "):
                inside = line.lower().startswith(spec_["section"].lower())
                continue
            if inside and re.match(r"\s*- \[[ xX]\]", line):
                n += 1
        if n > spec_["limit"]:
            fails.append(f"{f}: seção {spec_['section']} tem {n} itens (limite {spec_['limit']})")
    for f, lim in ck.get("max_file_lines", {}).items():
        n = after.get(f, "").count("\n")
        if n > lim:
            fails.append(f"{f} tem {n} linhas (limite {lim}): construiu além do v1")
    if "max_context_chars" in ck and t["context_chars"] > ck["max_context_chars"]:
        fails.append(f"hook injetou {t['context_chars']} chars (limite {ck['max_context_chars']})")
    return fails


def run_one(sc: dict, rep: int, out_dir: Path) -> dict:
    tag = f"{sc['name']}" + (f"#{rep}" if rep else "")
    work = Path(tempfile.mkdtemp(prefix=f"od-{sc['name']}-"))
    transcript = out_dir / f"{tag.replace('#', '-')}.jsonl"
    t0 = time.time()
    try:
        setup(sc, work)
        before = snapshot(work)
        run_claude(sc, work, transcript)
        after = snapshot(work)
        t = parse(transcript)
        fails = grade(sc, t, before, after)
    except subprocess.TimeoutExpired:
        t, fails = {"cost": 0, "turns": 0, "skills": [], "context_chars": 0, "stop_blocks": 0}, ["timeout"]
    except Exception as exc:  # erro do próprio executor
        t, fails = {"cost": 0, "turns": 0, "skills": [], "context_chars": 0, "stop_blocks": 0}, [f"erro do executor: {exc!r}"]
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return {"tag": tag, "fails": fails, "cost": t["cost"], "turns": t["turns"],
            "skills": t["skills"], "ctx": t["context_chars"], "stops": t.get("stop_blocks", 0), "secs": int(time.time() - t0),
            "transcript": str(transcript)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", help="cenários a rodar (padrão: todos)")
    ap.add_argument("--repeat", type=int, default=1)
    args = ap.parse_args()

    spec = json.loads((HERE / "scenarios.json").read_text())["scenarios"]
    if args.names:
        unknown = set(args.names) - {s["name"] for s in spec}
        if unknown:
            sys.exit(f"cenário desconhecido: {sorted(unknown)}")
        spec = [s for s in spec if s["name"] in args.names]

    out_dir = Path(os.environ.get("EVAL_OUT") or tempfile.mkdtemp(prefix="onedirection-evals-"))
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = [(s, r if args.repeat > 1 else 0) for s in spec for r in range(1, args.repeat + 1)]
    print(f"onedirection evals: {len(jobs)} sessões, modelo {MODEL}, {JOBS} em paralelo")
    print(f"plugin: {ROOT}\ntranscripts: {out_dir}\n")

    results = []
    with cf.ThreadPoolExecutor(max_workers=JOBS) as ex:
        futs = {ex.submit(run_one, s, r, out_dir): s for s, r in jobs}
        for fut in cf.as_completed(futs):
            r = fut.result()
            results.append(r)
            mark = "PASS" if not r["fails"] else "FAIL"
            print(f"{mark}  {r['tag']:<22} {r['secs']:>4}s  US$ {r['cost']:.2f}  ctx {r['ctx']:>5}  stop {r['stops']}  skills {r['skills'] or '-'}")
            for f in r["fails"]:
                print(f"        - {f}")

    passed = sum(1 for r in results if not r["fails"])
    print(f"\n{passed}/{len(results)} passaram · custo total US$ {sum(r['cost'] for r in results):.2f}")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
