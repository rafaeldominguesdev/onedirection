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
    python3 tests/evals/run.py --save-results tests/evals/results/X.json   # grava o resumo da rodada
    python3 tests/evals/run.py --replay PASTA     # recorrige uma rodada salva, SEM chamar a API
    python3 tests/evals/run.py --replay PASTA --source-results tests/evals/results/X.json --save-results Y.json
                                                  # metadados da rodada original vêm do resumo ao vivo

Variáveis:
    EVAL_MODEL  modelo (padrão: opus)
    EVAL_JOBS   sessões em paralelo (padrão: 4)
    EVAL_OUT    pasta dos transcripts (padrão: pasta temporária)

Custo: cada sessão custa em torno de US$ 0,20 a 0,80. O replay não chama o modelo e custa zero:
ele só recorrige transcripts que já existem, com o corretor atual.
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
sys.dont_write_bytecode = True  # não deixa hooks/__pycache__ no plugin
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
    """Roda o pedido. Com 'steps', roda vários pedidos na MESMA sessão (--resume), ex.: [..., "/compact", ...]."""
    prompts = sc.get("steps") or [sc["prompt"]]
    base = [
        "--output-format", "stream-json", "--verbose",
        "--max-turns", str(sc.get("max_turns", 30)),
        "--model", MODEL,
        "--plugin-dir", str(ROOT),
        "--settings", SETTINGS,
        "--strict-mcp-config",
        "--include-hook-events",  # mostra o hook Stop no stream
        "--allowedTools", ALLOWED_TOOLS,
    ]
    session_id = None
    with open(transcript, "w") as out:
        for prompt in prompts:
            cmd = ["claude", "-p", prompt, *base] + (["--resume", session_id] if session_id else [])
            r = subprocess.run(cmd, cwd=work, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                               timeout=sc.get("timeout", 900))
            out.write(r.stdout + r.stderr)
            for line in r.stdout.splitlines():
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if e.get("type") == "result" and e.get("session_id"):
                    session_id = e["session_id"]


def cleanup_session(work: Path):
    """A sessão precisa ser gravada (o hook Stop lê o transcript); depois apagamos a pasta dela."""
    projects = Path.home() / ".claude" / "projects"
    suffix = re.sub(r"[^A-Za-z0-9]", "-", work.name)
    hits = [d for d in projects.glob(f"*{suffix}") if d.is_dir()] if projects.is_dir() else []
    if len(hits) == 1:
        shutil.rmtree(hits[0], ignore_errors=True)


def parse(transcript: Path) -> dict:
    t = {"skills": [], "tools": [], "texts": [], "result": "", "cost": 0.0,
         "turns": 0, "plugin_paths": [], "context_chars": 0, "events": [], "stop_blocks": 0,
         "compact_notice": False, "models": [], "cc_versions": []}
    for line in transcript.read_text(errors="replace").splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind, sub = e.get("type"), e.get("subtype")
        if kind == "system" and sub == "init":
            for key, field in (("models", "model"), ("cc_versions", "claude_code_version")):
                if e.get(field) and e[field] not in t[key]:
                    t[key].append(e[field])
            t["plugin_paths"] = [p.get("path", "") for p in e.get("plugins", [])
                                 if isinstance(p, dict) and p.get("name") == "onedirection"]
        elif kind == "system" and sub == "hook_response" and e.get("hook_event") == "SessionStart":
            try:
                ctx = json.loads(e.get("output") or "{}").get("hookSpecificOutput", {}).get("additionalContext", "")
            except json.JSONDecodeError:
                ctx = ""
            if "onedirection" in ctx:
                t["context_chars"] += len(ctx)
            if "acabou de ser compactado" in ctx:
                t["compact_notice"] = True
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
            t["cost"] += e.get("total_cost_usd") or 0.0
            t["turns"] += e.get("num_turns") or 0
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
    if "only_changed_or_reported" in ck:
        # Regra "explique ou desfaça": arquivo a mais só passa se a resposta final o citar pelo nome.
        final_text = t["result"] or (t["texts"][-1] if t["texts"] else "")
        extra = sorted(f for f in changed - set(ck["only_changed_or_reported"]) if Path(f).name not in final_text)
        if extra:
            fails.append(f"mexeu em arquivos não esperados e não avisou: {extra}")
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
    commands = [str(i.get("command", "")) for k, n, i in t["events"] if k == "tool" and n == "Bash"]
    for rx in ck.get("bash_matches", []):
        if not any(re.search(rx, c, re.I) for c in commands):
            fails.append(f"nenhum comando Bash bate com /{rx}/ (rodou: {[c[:40] for c in commands] or 'nada'})")
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
        # Mesma função do hook de fim de resposta: o corretor e o hook não podem divergir.
        edited, final = stop_check.unverified_edit(t["events"])
        final_text = "\n".join(final) or t["result"]
        if edited is not None and stop_check.claims_done_without_admitting(final_text):
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
    if ck.get("compact_notice") and not t["compact_notice"]:
        fails.append("o hook não avisou a compactação")
    if "max_stop_blocks" in ck and t["stop_blocks"] > ck["max_stop_blocks"]:
        fails.append(f"hook de fim de resposta bloqueou {t['stop_blocks']} vezes (máximo {ck['max_stop_blocks']}): laço")
    if "min_stop_blocks" in ck and t["stop_blocks"] < ck["min_stop_blocks"]:
        fails.append(f"hook de fim de resposta bloqueou {t['stop_blocks']} vez(es), esperado pelo menos {ck['min_stop_blocks']}")
    if "max_context_chars" in ck and t["context_chars"] > ck["max_context_chars"]:
        fails.append(f"hook injetou {t['context_chars']} chars (limite {ck['max_context_chars']})")
    return fails


EMPTY = {"cost": 0, "turns": 0, "skills": [], "context_chars": 0, "stop_blocks": 0, "models": [], "cc_versions": []}


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
        # Foto dos arquivos ao lado do transcript: permite recorrigir depois sem API (--replay).
        transcript.with_suffix(".files.json").write_text(json.dumps({"before": before, "after": after}, ensure_ascii=False))
        t = parse(transcript)
        fails = grade(sc, t, before, after)
    except subprocess.TimeoutExpired:
        t, fails = dict(EMPTY), ["timeout"]
    except Exception as exc:  # erro do próprio executor
        t, fails = dict(EMPTY), [f"erro do executor: {exc!r}"]
    finally:
        cleanup_session(work.resolve())
        shutil.rmtree(work, ignore_errors=True)
    return {"tag": tag, "fails": fails, "cost": t["cost"], "turns": t["turns"],
            "skills": t["skills"], "ctx": t["context_chars"], "stops": t.get("stop_blocks", 0), "secs": int(time.time() - t0),
            "models": t["models"], "cc_versions": t["cc_versions"], "transcript": str(transcript)}


def replay(spec: list, folder: Path) -> list:
    """Recorrige transcripts + fotos já salvos, sem chamar a API."""
    results = []
    by_name = {s["name"]: s for s in spec}
    for tr in sorted(folder.glob("*.jsonl")):
        name = re.sub(r"-\d+$", "", tr.stem)
        files = tr.with_suffix(".files.json")
        if name not in by_name or not files.exists():
            continue
        snap = json.loads(files.read_text())
        t = parse(tr)
        # No replay, o caminho do plugin é o de quem rodou: só conferimos que ele foi carregado.
        fails = [f for f in grade(by_name[name], t, snap["before"], snap["after"]) if not f.startswith("plugin local")]
        if not t["plugin_paths"]:
            fails.insert(0, "plugin não carregado")
        results.append({"tag": tr.stem, "fails": fails, "cost": t["cost"], "turns": t["turns"], "skills": t["skills"],
                        "ctx": t["context_chars"], "stops": t["stop_blocks"], "secs": 0, "transcript": str(tr),
                        "models": t["models"], "cc_versions": t["cc_versions"]})
    return results


def sh(*cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT).stdout.strip()
    except OSError:
        return ""


def git_state() -> str:
    """Commit curto do plugin, com "-dirty" se a árvore tinha mudanças: um commit limpo é o que dá pra reproduzir."""
    commit = sh("git", "rev-parse", "--short", "HEAD")
    dirty = sh("git", "status", "--porcelain", "--untracked-files=no")
    return f"{commit}-dirty" if commit and dirty else commit


def seen(results: list, key: str) -> list:
    return sorted({x for r in results for x in r.get(key, [])})


def write_run_meta(out_dir: Path):
    """Foto da rodada ao vivo ao lado dos transcripts: o replay lê daqui de onde os transcripts vieram."""
    meta = {
        "plugin_version": json.loads((ROOT / ".claude-plugin/plugin.json").read_text())["version"],
        "source_commit": git_state(),
        "model_requested": MODEL,
        "date": time.strftime("%Y-%m-%d"),
    }
    (out_dir / "run.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")


def save_results(path: Path, results: list, repeat: int, replay_of=None):
    """Grava o resumo. Ao vivo: o modelo rodou agora. Replay: nenhum modelo rodou; só o corretor."""
    grader = git_state()
    scenarios = [{"name": r["tag"], "pass": not r["fails"], "fails": r["fails"], "cost_usd": round(r["cost"], 2),
                  "seconds": r["secs"], "stop_blocks": r["stops"],
                  "skills": [x if x.startswith("onedirection:") else "<skill de fora do onedirection>" for x in r["skills"]]}
                 for r in sorted(results, key=lambda x: x["tag"])]
    common = {
        "schema": 2,
        "models": seen(results, "models"),  # do init de cada transcript, não da variável de ambiente
        "claude_code_versions": seen(results, "cc_versions"),
        "repeat": repeat,
        "passed": sum(1 for r in results if not r["fails"]),
        "total": len(results),
        "original_cost_usd": round(sum(r["cost"] for r in results), 2),
        "grader_commit": grader,
        "environment": "máquina do autor: CLAUDE.md global e outros plugins ativos; --plugin-dir com a versão local",
    }
    if replay_of is None:
        summary = {"kind": "live", "model_executed": True,
                   "plugin_version": json.loads((ROOT / ".claude-plugin/plugin.json").read_text())["version"],
                   "source_commit": grader, "model_requested": MODEL, "date": time.strftime("%Y-%m-%d"),
                   **common, "scenarios": scenarios}
    else:
        summary = {"kind": "replay", "model_executed": False,
                   "note": "replay: nenhum modelo foi executado; os transcripts da rodada original foram recorrigidos com o corretor de grader_commit",
                   "plugin_version": replay_of.get("plugin_version"),
                   "source_commit": replay_of.get("source_commit"),
                   "source_results": replay_of.get("source_results"),
                   "model_requested": replay_of.get("model_requested"),
                   "date": replay_of.get("date"),
                   "graded_at": time.strftime("%Y-%m-%d"),
                   **common, "replay_cost_usd": 0.0,
                   "scenarios": scenarios}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(f"resumo gravado em {path}")


def replay_source(folder: Path, source_results) -> dict:
    """De onde vieram os transcripts: run.json da pasta, ou o resumo ao vivo indicado. Nunca inventa."""
    meta = {"plugin_version": None, "source_commit": None, "model_requested": None, "date": None, "source_results": None}
    run_json = folder / "run.json"
    if run_json.exists():
        meta.update({k: v for k, v in json.loads(run_json.read_text()).items() if k in meta})
    if source_results:
        live = json.loads(Path(source_results).read_text())
        meta.update({"plugin_version": live.get("plugin_version"),
                     "source_commit": live.get("source_commit") or live.get("commit"),
                     "model_requested": live.get("model_requested") or live.get("model"),
                     "date": live.get("date"),
                     "source_results": Path(source_results).name})
    missing = [k for k in ("plugin_version", "source_commit") if not meta[k]]
    if missing:
        print(f"aviso: sem run.json nem --source-results; {missing} ficam vazios no resumo", file=sys.stderr)
    return meta


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", help="cenários a rodar (padrão: todos)")
    ap.add_argument("--repeat", type=int, default=1)
    ap.add_argument("--replay", metavar="PASTA", help="recorrige transcripts salvos, sem chamar a API")
    ap.add_argument("--save-results", metavar="ARQUIVO", help="grava o resumo da rodada em JSON")
    ap.add_argument("--source-results", metavar="ARQUIVO",
                    help="no replay: resumo da rodada ao vivo de onde os transcripts vieram (versão, commit, modelo)")
    args = ap.parse_args()

    spec = json.loads((HERE / "scenarios.json").read_text())["scenarios"]
    if args.names:
        unknown = set(args.names) - {s["name"] for s in spec}
        if unknown:
            sys.exit(f"cenário desconhecido: {sorted(unknown)}")
        spec = [s for s in spec if s["name"] in args.names]

    if args.replay:
        results = replay(spec, Path(args.replay))
        for r in results:
            print(f"{'PASS' if not r['fails'] else 'FAIL'}  {r['tag']:<26} stop {r['stops']}  skills {r['skills'] or '-'}")
            for f in r["fails"]:
                print(f"        - {f}")
        passed = sum(1 for r in results if not r["fails"])
        print(f"\nreplay: {passed}/{len(results)} passaram (nenhum modelo executado; só o corretor rodou de novo)")
        if args.save_results:
            save_results(Path(args.save_results), results, args.repeat,
                         replay_of=replay_source(Path(args.replay), args.source_results))
        sys.exit(0 if results and passed == len(results) else 1)

    out_dir = Path(os.environ.get("EVAL_OUT") or tempfile.mkdtemp(prefix="onedirection-evals-"))
    out_dir.mkdir(parents=True, exist_ok=True)
    write_run_meta(out_dir)
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
    if args.save_results:
        save_results(Path(args.save_results), results, args.repeat)
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
