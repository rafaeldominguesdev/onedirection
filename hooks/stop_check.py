#!/usr/bin/env python3
"""Stop hook do onedirection: "pronto" sem prova não passa.

Bloqueia o fim da resposta UMA vez (stop_hook_active evita laço) quando, no turno atual:
  1. houve edição de arquivo que não é Markdown (Edit/Write/MultiEdit/NotebookEdit);
  2. nada foi conferido DEPOIS da última edição (Bash, Read, Grep, Glob ou a skill verifying-before-done);
  3. a resposta final afirma conclusão ("pronto", "feito", "corrigido", "done"...)
     sem admitir que não verificou ("não verifiquei", "não testei"...).

Qualquer erro ou formato inesperado = não bloqueia. Este hook nunca pode travar o usuário.
"""
import json
import re
import sys

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
CHECK_TOOLS = {"Bash", "Read", "Grep", "Glob"}
CLAIM = re.compile(
    r"\b(pront[oa]s?|feit[oa]s?|conclu[ií]d[oa]s?|finalizad[oa]s?|funcionando|corrigid[oa]s?|"
    r"resolvid[oa]s?|implementad[oa]s?|terminei|tudo certo|done|fixed|completed?|all set|it works)\b",
    re.IGNORECASE,
)
DISCLOSURE = re.compile(
    r"n[ãa]o (verifiquei|testei|rodei|conferi|executei|consegui (verificar|testar|rodar|conferir))|"
    r"sem (verificar|testar)|not (verified|tested)|didn'?t (verify|test|run)|could(n'?t| not) (verify|test)",
    re.IGNORECASE,
)


def allow():
    print("{}")
    sys.exit(0)


def blocks(entry):
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return content if isinstance(content, list) else []


def is_user_prompt(entry):
    if entry.get("type") != "user" or entry.get("isMeta"):
        return False
    bs = blocks(entry)
    has_text = any(b.get("type") == "text" and (b.get("text") or "").strip() for b in bs)
    has_result = any(b.get("type") == "tool_result" for b in bs)
    return has_text and not has_result


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        allow()
    if data.get("stop_hook_active"):
        allow()

    entries = []
    try:
        with open(data.get("transcript_path") or "", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except OSError:
        allow()

    start = 0
    for i, e in enumerate(entries):
        if is_user_prompt(e):
            start = i + 1
    turn = entries[start:]

    last_edit, last_edit_file, verified_after = None, "", False
    final_text_parts = []
    pos = 0
    for e in turn:
        if e.get("type") != "assistant":
            continue
        for b in blocks(e):
            pos += 1
            if b.get("type") == "tool_use":
                name = b.get("name", "")
                inp = b.get("input") or {}
                final_text_parts = []
                if name in EDIT_TOOLS:
                    path = str(inp.get("file_path") or inp.get("notebook_path") or "")
                    if not path.lower().endswith((".md", ".markdown", ".txt")):
                        last_edit, last_edit_file, verified_after = pos, path, False
                elif last_edit is not None and (
                    name in CHECK_TOOLS
                    or (name == "Skill" and "verifying-before-done" in str(inp.get("skill", "")))
                ):
                    verified_after = True
            elif b.get("type") == "text":
                final_text_parts.append(b.get("text") or "")

    final_text = data.get("last_assistant_message") or "\n".join(final_text_parts)
    if last_edit is None or verified_after:
        allow()
    if not CLAIM.search(final_text) or DISCLOSURE.search(final_text):
        allow()

    short = last_edit_file.rsplit("/", 1)[-1] or "o arquivo"
    print(json.dumps({
        "decision": "block",
        "reason": (
            f"[onedirection] Você afirmou que terminou, mas nada foi conferido depois da última edição ({short}). "
            "Antes de encerrar, use onedirection:verifying-before-done: rode a verificação e mostre a prova. "
            "Se não der pra verificar, diga explicitamente: \"Não verifiquei: <o quê> — porque <motivo>\"."
        ),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
