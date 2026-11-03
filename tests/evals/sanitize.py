#!/usr/bin/env python3
"""Limpa transcripts dos testes de comportamento pra publicar.

    python3 tests/evals/sanitize.py PASTA_DOS_TRANSCRIPTS PASTA_DE_SAIDA

Tira o que é da máquina de quem rodou: caminhos pessoais e temporários, eventos de cota da conta,
a lista de plugins/skills/MCP do init (fica só modelo, versão e o onedirection), assinaturas de
raciocínio, e o conteúdo de skills que não são do onedirection. Mantém o resto, pra o --replay
continuar funcionando.
"""
import json
import re
import sys
from pathlib import Path

HOME = str(Path.home())
TMP_RE = re.compile(r"/(private/)?var/folders/[^\s\"']+?/T/(od-[A-Za-z0-9_-]+)")


def clean_str(s: str) -> str:
    s = TMP_RE.sub(r"<tmp>/\2", s)
    return s.replace(HOME, "~")


def clean(obj):
    if isinstance(obj, str):
        return clean_str(obj)
    if isinstance(obj, list):
        return [clean(x) for x in obj]
    if isinstance(obj, dict):
        return {k: clean(v) for k, v in obj.items() if k != "signature"}
    return obj


def sanitize_transcript(src: Path, dst: Path):
    foreign_skill_ids = set()
    out = []
    for line in src.read_text(errors="replace").splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") == "rate_limit_event":
            continue
        if e.get("type") == "system" and e.get("subtype") == "init":
            e = {"type": "system", "subtype": "init", "model": e.get("model"),
                 "claude_code_version": e.get("claude_code_version"),
                 "plugins": [p for p in e.get("plugins", []) if isinstance(p, dict) and p.get("name") == "onedirection"]}
        msg = e.get("message") if isinstance(e.get("message"), dict) else None
        if msg and isinstance(msg.get("content"), list):
            for c in msg["content"]:
                if c.get("type") == "tool_use" and c.get("name") == "Skill" and not str(c.get("input", {}).get("skill", "")).startswith("onedirection:"):
                    foreign_skill_ids.add(c.get("id"))
                if c.get("type") == "tool_result" and c.get("tool_use_id") in foreign_skill_ids:
                    c["content"] = "<conteúdo de skill pessoal removido>"
        out.append(json.dumps(clean(e), ensure_ascii=False))
    dst.write_text("\n".join(out) + "\n")


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    dst.mkdir(parents=True, exist_ok=True)
    n = 0
    for tr in sorted(src.glob("*.jsonl")):
        sanitize_transcript(tr, dst / tr.name)
        files = tr.with_suffix(".files.json")
        if files.exists():
            (dst / files.name).write_text(json.dumps(clean(json.loads(files.read_text())), ensure_ascii=False))
        n += 1
    print(f"{n} transcripts limpos em {dst}")


if __name__ == "__main__":
    main()
