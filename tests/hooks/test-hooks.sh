#!/usr/bin/env bash
# Testa os hooks do onedirection: JSON válido, com e sem NORTE.md, compactação e "Foco agora".
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fail=0

check() { # nome, condição em python sobre o JSON lido de stdin (ctx = additionalContext)
  if python3 -c "
import json,sys
d=json.load(sys.stdin)
ctx=d.get('hookSpecificOutput',{}).get('additionalContext','')
assert $2, d" 2>/dev/null; then
    echo "ok   $1"
  else
    echo "FAIL $1"; fail=1
  fi
}

run() { # hook, stdin
  local stdin_json="${2-}"
  [ -n "$stdin_json" ] || stdin_json='{}'
  printf '%s' "$stdin_json" | CLAUDE_PLUGIN_ROOT="$ROOT" CLAUDE_PROJECT_DIR="$TMP" "$ROOT/hooks/$1"
}

# Sem NORTE.md
run session-start '{"source":"startup"}' | check "session-start sem NORTE injeta using-onedirection" \
  "'using-onedirection' in ctx and 'ainda não tem NORTE.md' in ctx"
run session-start '{"source":"startup"}' | check "startup não manda recovering-focus" \
  "'acabou de ser compactado' not in ctx"
run user-prompt-submit | check "user-prompt-submit sem NORTE fica quieto" "d == {}"

# Com NORTE.md (aspas, barra e tab pra testar o escape)
cat > "$TMP/NORTE.md" <<'EOF'
# NORTE — teste

## A promessa
"X" ajuda Y\Z	agora

## Foco agora
- Fazendo: tela de login
- Próximo passo: validar e-mail

## Estado
começando
EOF
run session-start '{"source":"startup"}' | check "session-start com NORTE injeta o arquivo (escape ok)" \
  "'\"X\" ajuda Y\\\\Z\tagora' in ctx"
run session-start '{"hook_event_name":"SessionStart","source":"compact"}' | check "compact manda usar recovering-focus" \
  "'acabou de ser compactado' in ctx and 'recovering-focus' in ctx"
run user-prompt-submit | check "user-prompt-submit traz o Foco agora" \
  "'Fazendo: tela de login' in ctx and 'validar e-mail' in ctx and 'começando' not in ctx"

# NORTE.md grande demais gera aviso
for i in $(seq 1 130); do echo "- linha $i"; done >> "$TMP/NORTE.md"
run session-start '{"source":"startup"}' | check "NORTE.md com mais de 120 linhas gera aviso" \
  "'o ideal é até ~80' in ctx"

# Toda skill tem frontmatter com name igual à pasta e description
for dir in "$ROOT"/skills/*/; do
  name="$(basename "$dir")"
  if head -4 "$dir/SKILL.md" | grep -q "^name: ${name}$" && head -4 "$dir/SKILL.md" | grep -q "^description: "; then
    echo "ok   skill $name tem frontmatter"
  else
    echo "FAIL skill $name tem frontmatter"; fail=1
  fi
done

# Manifestos válidos
for f in .claude-plugin/plugin.json .claude-plugin/marketplace.json hooks/hooks.json; do
  check "$f é JSON válido" "True" < "$ROOT/$f"
done

exit $fail
