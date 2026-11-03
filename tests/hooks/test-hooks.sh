#!/usr/bin/env bash
# Testa os hooks do onedirection: JSON válido, os três níveis de injeção, compactação,
# "Foco agora", NORTE.md achado a partir de subpasta e limites de tamanho.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fail=0

check() { # nome, condição em python (d = JSON, ctx = additionalContext)
  if python3 -c "
import json,sys
d=json.load(sys.stdin)
ctx=d.get('hookSpecificOutput',{}).get('additionalContext','')
assert $2, (len(ctx), ctx[:200])" 2>/dev/null; then
    echo "ok   $1"
  else
    echo "FAIL $1"; fail=1
  fi
}

run() { # hook, pasta do projeto, stdin
  local stdin_json="${3-}"
  [ -n "$stdin_json" ] || stdin_json='{}'
  printf '%s' "$stdin_json" | CLAUDE_PLUGIN_ROOT="$ROOT" CLAUDE_PROJECT_DIR="$2" "$ROOT/hooks/$1"
}

START='{"source":"startup"}'
COMPACT='{"hook_event_name":"SessionStart","source":"compact"}'

# --- Fora de projeto: uma linha só
LOOSE="$TMP/solta"; mkdir -p "$LOOSE"; echo "nota" > "$LOOSE/notas.txt"
run session-start "$LOOSE" "$START" | check "fora de projeto: só uma linha (<300 chars)" \
  "'fora de projeto' in ctx and 'capturing-the-vision' in ctx and len(ctx) < 300"
run session-start "$LOOSE" "$COMPACT" | check "fora de projeto: compactação não injeta nada a mais" \
  "'compactado' not in ctx"
run user-prompt-submit "$LOOSE" | check "fora de projeto: user-prompt-submit fica quieto" "d == {}"

# --- Pasta pessoal com git (dotfiles) não conta como projeto
FAKEHOME="$TMP/home"; mkdir -p "$FAKEHOME/.git"
HOME="$FAKEHOME" run session-start "$FAKEHOME" "$START" | check "pasta pessoal com .git: tratada como fora de projeto" \
  "'fora de projeto' in ctx"
mkdir -p "$FAKEHOME/Downloads"
HOME="$FAKEHOME" run session-start "$FAKEHOME/Downloads" "$START" | check "subpasta da pessoal com .git na pessoal: fora de projeto" \
  "'fora de projeto' in ctx"

# --- Projeto sem NORTE.md (git): bloco curto
PROJ="$TMP/proj"; mkdir -p "$PROJ/.git" "$PROJ/src"
run session-start "$PROJ" "$START" | check "projeto sem NORTE: bloco curto com mapeamento obrigatório (<1500 chars)" \
  "'ainda NÃO tem NORTE.md' in ctx and 'mapping-existing-project' in ctx and 'verifying-before-done' in ctx and len(ctx) < 1500"
run session-start "$PROJ" "$START" | check "projeto sem NORTE: não injeta a skill inteira" \
  "'## A Regra da Evidência' not in ctx"
run session-start "$PROJ" "$COMPACT" | check "projeto sem NORTE: compactação manda recovering-focus" \
  "'recovering-focus' in ctx and 'compactado' in ctx"
run user-prompt-submit "$PROJ" | check "projeto sem NORTE: user-prompt-submit fica quieto" "d == {}"

# --- Projeto sem git, só com manifesto
MAN="$TMP/manifesto"; mkdir -p "$MAN"; echo '{}' > "$MAN/package.json"
run session-start "$MAN" "$START" | check "pasta com package.json conta como projeto" \
  "'ainda NÃO tem NORTE.md' in ctx"

# --- Com NORTE.md (aspas, barra e tab pra testar o escape)
cat > "$PROJ/NORTE.md" <<'EOF'
# NORTE — teste

## A promessa
"X" ajuda Y\Z	agora

## Foco agora
- Fazendo: tela de login
- Próximo passo: validar e-mail

## Estado
começando
EOF
run session-start "$PROJ" "$START" | check "com NORTE: injeta a skill inteira" \
  "'## A Regra da Evidência' in ctx and 'using-onedirection' in ctx"
run session-start "$PROJ" "$START" | check "com NORTE: injeta o arquivo (escape ok)" \
  "'\"X\" ajuda Y\\\\Z\tagora' in ctx"
run session-start "$PROJ" "$START" | check "startup não manda recovering-focus" \
  "'acabou de ser compactado' not in ctx"
run session-start "$PROJ" "$COMPACT" | check "compact manda usar recovering-focus" \
  "'acabou de ser compactado' in ctx and 'recovering-focus' in ctx"
run user-prompt-submit "$PROJ" | check "user-prompt-submit traz o Foco agora" \
  "'Fazendo: tela de login' in ctx and 'validar e-mail' in ctx and 'começando' not in ctx"
run user-prompt-submit "$PROJ" | check "user-prompt-submit é curto (<600 chars)" "len(ctx) < 600"

# --- Claude aberto numa subpasta: acha o NORTE.md na raiz do git
run session-start "$PROJ/src" "$START" | check "subpasta: acha o NORTE.md na raiz do git" \
  "'tela de login' in ctx"
run user-prompt-submit "$PROJ/src" | check "subpasta: user-prompt-submit traz o Foco agora" \
  "'Fazendo: tela de login' in ctx"

# --- NORTE.md grande demais gera aviso
for i in $(seq 1 130); do echo "- linha $i"; done >> "$PROJ/NORTE.md"
run session-start "$PROJ" "$START" | check "NORTE.md com mais de 120 linhas gera aviso" \
  "'o ideal é até ~80' in ctx"

# --- Worktree: .git é um arquivo, não uma pasta
WT="$TMP/worktree"; mkdir -p "$WT/src"; echo "gitdir: /outro/lugar/.git/worktrees/wt" > "$WT/.git"
cp "$ROOT/tests/evals/fixtures/estudai/NORTE.md" "$WT/NORTE.md"
run session-start "$WT/src" "$START" | check "worktree (.git arquivo): acha o NORTE.md na raiz" \
  "'Estudaí ajuda vestibulandos' in ctx"

# --- Compactação com espaços no JSON de entrada
run session-start "$PROJ" '{ "source" : "compact" }' | check "compact com espaços no JSON também é reconhecido" \
  "'acabou de ser compactado' in ctx"

# --- Pasta com espaços no nome
SPACED="$TMP/meu projeto com espaço"; mkdir -p "$SPACED/.git" "$SPACED/sub pasta"
cp "$ROOT/tests/evals/fixtures/estudai/NORTE.md" "$SPACED/NORTE.md"
run session-start "$SPACED/sub pasta" "$START" | check "pasta com espaço no nome: acha o NORTE.md" \
  "'Estudaí ajuda vestibulandos' in ctx"
run user-prompt-submit "$SPACED" | check "pasta com espaço no nome: user-prompt-submit funciona" \
  "'Próximo passo: botões acertei/errei' in ctx"

# --- Validação do NORTE.md
VALIDATE="$ROOT/scripts/validate-norte"
if "$VALIDATE" "$ROOT/tests/evals/fixtures/estudai/NORTE.md" >/dev/null; then
  echo "ok   validate-norte: NORTE.md completo passa"
else
  echo "FAIL validate-norte: NORTE.md completo passa"; fail=1
fi
out="$("$VALIDATE" "$ROOT/skills/capturing-the-vision/norte-template.md" || true)"
if echo "$out" | grep -q "linha(s) do modelo sem preencher" && echo "$out" | grep -q "v1 não tem nenhum item"; then
  echo "ok   validate-norte: modelo sem preencher é apontado"
else
  echo "FAIL validate-norte: modelo sem preencher é apontado"; echo "$out"; fail=1
fi
BAD="$TMP/ruim"; mkdir -p "$BAD/.git"
printf '# NORTE — ruim\n\n## A promessa\nAjuda alguém.\n\n## v1 obrigatório\n- [ ] algo\n' > "$BAD/NORTE.md"
out="$("$VALIDATE" "$BAD/NORTE.md" || true)"
if echo "$out" | grep -q "NÃO é" && echo "$out" | grep -q "Pronto quando" && echo "$out" | grep -q "Foco agora"; then
  echo "ok   validate-norte: seções faltando são listadas"
else
  echo "FAIL validate-norte: seções faltando são listadas"; echo "$out"; fail=1
fi
set +e; "$VALIDATE" "$TMP/nao-existe.md" >/dev/null 2>&1; code=$?; set -e
if [ "$code" = 2 ]; then echo "ok   validate-norte: arquivo inexistente sai com 2"; else echo "FAIL validate-norte: arquivo inexistente sai com 2 (saiu $code)"; fail=1; fi
run session-start "$BAD" "$START" | check "session-start avisa quando o NORTE.md está malformado" \
  "'o NORTE.md tem problemas' in ctx and 'NÃO é' in ctx"
run session-start "$SPACED" "$START" | check "session-start não avisa quando o NORTE.md está ok" \
  "'o NORTE.md tem problemas' not in ctx"

# --- Lembrete adaptativo
run user-prompt-submit "$SPACED" '{"prompt":"adiciona um botão de embaralhar"}' | check "pedido de escopo: lembrete de regras + Foco agora" \
  "'guarding-the-direction' in ctx and 'registre em 1 linha' in ctx and 'Foco agora' in ctx"
run user-prompt-submit "$SPACED" '{"prompt":"o que essa função faz?"}' | check "pergunta comum: só o Foco agora, sem repetir as regras" \
  "'guarding-the-direction' not in ctx and 'Foco agora' in ctx"
printf '# NORTE\n\n## A promessa\nX\n' > "$BAD/NORTE.md"
run user-prompt-submit "$BAD" '{"prompt":"o que essa função faz?"}' | check "sem Foco agora e pergunta comum: não injeta nada" "d == {}"

# --- Stop hook: "pronto" sem prova
stop_case() { # nome, esperado (block|allow), stdin extra (json), linhas do transcript...
  local name="$1" want="$2" extra="$3"; shift 3
  local tr="$TMP/transcript-$RANDOM.jsonl"
  printf '%s\n' "$@" > "$tr"
  local got
  got="$(printf '{"hook_event_name":"Stop","transcript_path":"%s"%s}' "$tr" "$extra" | "$ROOT/hooks/stop")"
  if { [ "$want" = block ] && echo "$got" | grep -q '"decision": "block"'; } || { [ "$want" = allow ] && [ "$got" = "{}" ]; }; then
    echo "ok   stop: $name"
  else
    echo "FAIL stop: $name (esperado $want, veio: $got)"; fail=1
  fi
}
U='{"type":"user","message":{"role":"user","content":"muda o botão"}}'
EDIT='{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Edit","input":{"file_path":"/p/index.html"}}]}}'
EDITMD='{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Edit","input":{"file_path":"/p/NORTE.md"}}]}}'
RES='{"type":"user","message":{"content":[{"type":"tool_result","content":"ok"}]}}'
READ='{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Read","input":{"file_path":"/p/index.html"}}]}}'
BASH='{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Bash","input":{"command":"npm test"}}]}}'
VSKILL='{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Skill","input":{"skill":"onedirection:verifying-before-done"}}]}}'
DONE='{"type":"assistant","message":{"content":[{"type":"text","text":"Pronto, mudei o botão."}]}}'
HONEST='{"type":"assistant","message":{"content":[{"type":"text","text":"Pronto. Não verifiquei no navegador porque não tenho acesso."}]}}'
ASK='{"type":"assistant","message":{"content":[{"type":"text","text":"Mudei metade. Qual cor você prefere?"}]}}'
stop_case "edição + 'pronto' sem conferir: bloqueia" block "" "$U" "$EDIT" "$RES" "$DONE"
stop_case "edição + Bash depois + 'pronto': passa" allow "" "$U" "$EDIT" "$RES" "$BASH" "$RES" "$DONE"
stop_case "edição + releitura depois + 'pronto': passa" allow "" "$U" "$EDIT" "$RES" "$READ" "$RES" "$DONE"
stop_case "edição + skill verifying depois + 'pronto': passa" allow "" "$U" "$EDIT" "$RES" "$VSKILL" "$RES" "$DONE"
stop_case "releitura só ANTES da edição: bloqueia" block "" "$U" "$READ" "$RES" "$EDIT" "$RES" "$DONE"
stop_case "'pronto' + 'não verifiquei': passa" allow "" "$U" "$EDIT" "$RES" "$HONEST"
OPUSREAL='{"type":"assistant","message":{"content":[{"type":"text","text":"Pronto: o botão agora diz Próximo card. Como você pediu, não reli o arquivo nem abri a página no navegador."}]}}'
stop_case "frase real do Opus ('não reli... nem abri'): passa" allow "" "$U" "$EDIT" "$RES" "$OPUSREAL"
stop_case "edição sem afirmar conclusão: passa" allow "" "$U" "$EDIT" "$RES" "$ASK"
stop_case "só Markdown editado: passa" allow "" "$U" "$EDITMD" "$RES" "$DONE"
stop_case "edição em turno ANTERIOR não conta: passa" allow "" "$U" "$EDIT" "$RES" "$DONE" "$U" "$DONE"
stop_case "stop_hook_active (já voltou uma vez): passa" allow ',"stop_hook_active":true' "$U" "$EDIT" "$RES" "$DONE"
got="$(printf '{"transcript_path":"/nao/existe.jsonl"}' | "$ROOT/hooks/stop")"
[ "$got" = "{}" ] && echo "ok   stop: transcript inexistente não bloqueia" || { echo "FAIL stop: transcript inexistente não bloqueia ($got)"; fail=1; }
got="$(printf 'isso não é json' | "$ROOT/hooks/stop")"
[ "$got" = "{}" ] && echo "ok   stop: entrada inválida não bloqueia" || { echo "FAIL stop: entrada inválida não bloqueia ($got)"; fail=1; }

# --- Toda skill tem frontmatter com name igual à pasta e description
for dir in "$ROOT"/skills/*/; do
  name="$(basename "$dir")"
  if head -4 "$dir/SKILL.md" | grep -q "^name: ${name}$" && head -4 "$dir/SKILL.md" | grep -q "^description: "; then
    echo "ok   skill $name tem frontmatter"
  else
    echo "FAIL skill $name tem frontmatter"; fail=1
  fi
done

# --- Manifestos e cenários válidos
for f in .claude-plugin/plugin.json .claude-plugin/marketplace.json hooks/hooks.json tests/evals/scenarios.json; do
  [ -f "$ROOT/$f" ] || continue
  check "$f é JSON válido" "True" < "$ROOT/$f"
done

exit $fail
