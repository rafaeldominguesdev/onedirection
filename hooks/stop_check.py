#!/usr/bin/env python3
"""Stop hook do onedirection: "pronto" sem prova não passa.

Bloqueia o fim da resposta UMA vez (stop_hook_active evita laço) quando, no turno atual:
  1. houve edição de arquivo que não é Markdown (Edit/Write/MultiEdit/NotebookEdit);
  2. nada foi conferido DEPOIS da última edição: um comando (Bash), a skill verifying-before-done,
     ou Read/Grep que olhe o arquivo editado. Glob não conta: listar arquivos não prova nada;
  3. a resposta final afirma conclusão ("pronto", "feito", "corrigido", "done"...)
     sem admitir que não verificou ("não verifiquei", "não testei"...).

Qualquer erro ou formato inesperado = não bloqueia. Este hook nunca pode travar o usuário.

Limite honesto: é uma heurística. Ele não sabe se a verificação provou o que foi afirmado;
só cobra que ALGUMA conferência tenha acontecido depois da última edição, ou que a resposta
admita que não conferiu. Markdown e .txt ficam de fora de propósito (documentação não pede teste).
"""
import json
import re
import sys

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
RUN_TOOLS = {"Bash"}            # comando: sempre conta como conferência
LOOK_TOOLS = {"Read", "Grep"}   # leitura: só conta se olhar o arquivo editado
CLAIM = re.compile(
    r"\b(pront[oa]s?|feit[oa]s?|conclu[ií]d[oa]s?|finalizad[oa]s?|funcionando|corrigid[oa]s?|"
    r"resolvid[oa]s?|implementad[oa]s?|terminei|corrigi|resolvi|implementei|consertei|arrumei|"
    r"(deve|deveria) funcionar|tudo certo|done|fixed|completed?|all set|it works|should (now )?work)\b",
    re.IGNORECASE,
)
DISCLOSURE = re.compile(
    r"n[ãa]o (foi |foram |cheguei a |consegui )?(verific|verifiq|test|rod|confer|execut|reli|reler|abri|cheq|valid|olhei)\w*|"
    r"nem (verific|verifiq|test|rod|confer|execut|reli|abri|cheq|valid|olhei)\w*|"
    r"sem (verificar|testar|rodar|conferir|abrir)|"
    r"not (yet )?(verified|tested|run|checked)|(didn|haven)'?t (verif|test|run|check)\w*|"
    r"could(n'?t| not) (verify|test|run|check)|untested|unverified",
    re.IGNORECASE,
)


def allow():
    print("{}")
    sys.exit(0)


def blocks(entry):
    msg = entry.get("message")
    content = msg.get("content") if isinstance(msg, dict) else None
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return [b for b in content if isinstance(b, dict)] if isinstance(content, list) else []


def looks_at(name, inp, edited):
    """Read/Grep contam como conferência só se olharem o arquivo editado (ou o projeto inteiro, no Grep)."""
    if name == "Read":
        return str(inp.get("file_path") or "") == edited
    if name == "Grep":
        where = str(inp.get("path") or "")
        return not where or edited == where or edited.startswith(where.rstrip("/") + "/")
    return False


def is_user_prompt(entry):
    if entry.get("type") != "user" or entry.get("isMeta"):
        return False
    bs = blocks(entry)
    has_text = any(b.get("type") == "text" and (b.get("text") or "").strip() for b in bs)
    has_result = any(b.get("type") == "tool_result" for b in bs)
    return has_text and not has_result


def unverified_edit(steps):
    """A regra, num lugar só (o hook e o corretor dos testes usam esta função).

    steps: sequência de ("tool", nome, input) e ("text", texto, None), na ordem do turno.
    Devolve (arquivo da última edição sem conferência depois dela, ou None; textos depois da última ferramenta).
    """
    last_edit, verified, final_text = None, False, []
    for kind, name, inp in steps:
        if kind == "tool":
            inp = inp if isinstance(inp, dict) else {}
            final_text = []
            if name in EDIT_TOOLS:
                path = str(inp.get("file_path") or inp.get("notebook_path") or "")
                if not path.lower().endswith((".md", ".markdown", ".txt")):
                    last_edit, verified = path, False
            elif last_edit is not None and (
                name in RUN_TOOLS
                or (name in LOOK_TOOLS and looks_at(name, inp, last_edit))
                or (name == "Skill" and "verifying-before-done" in str(inp.get("skill", "")))
            ):
                verified = True
        elif kind == "text":
            final_text.append(name or "")
    return (None if verified else last_edit), final_text


def claims_done_without_admitting(text):
    return bool(CLAIM.search(text)) and not DISCLOSURE.search(text)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        allow()
    if not isinstance(data, dict) or data.get("stop_hook_active"):
        allow()

    entries = []
    try:
        with open(data.get("transcript_path") or "", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(e, dict):
                    entries.append(e)
    except (OSError, TypeError, ValueError):
        allow()

    start = 0
    for i, e in enumerate(entries):
        if is_user_prompt(e):
            start = i + 1

    steps = []
    for e in entries[start:]:
        if e.get("type") != "assistant":
            continue
        for b in blocks(e):
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use":
                steps.append(("tool", b.get("name", ""), b.get("input")))
            elif b.get("type") == "text":
                steps.append(("text", b.get("text") or "", None))

    edited, final_parts = unverified_edit(steps)
    final_text = data.get("last_assistant_message") or "\n".join(final_parts)
    if edited is None or not isinstance(final_text, str) or not claims_done_without_admitting(final_text):
        allow()

    short = edited.rsplit("/", 1)[-1] or "o arquivo"
    print(json.dumps({
        "decision": "block",
        "reason": (
            f"[onedirection] Você afirmou que terminou, mas nada foi conferido depois da última edição ({short}). "
            "Antes de encerrar, use onedirection:verifying-before-done: rode a verificação e mostre a prova. "
            "Se não der pra verificar, diga explicitamente: \"Não verifiquei: <o quê> — porque <motivo>\"."
        ),
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:  # formato inesperado: este hook nunca pode travar o usuário
        print("{}")
