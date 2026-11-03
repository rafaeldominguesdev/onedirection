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
