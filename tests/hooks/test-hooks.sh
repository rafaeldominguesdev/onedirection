#!/usr/bin/env bash
# Testa os hooks do onedirection: JSON válido, com e sem NORTE.md.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fail=0

check() { # nome, condição em python sobre o JSON lido de stdin
  if python3 -c "import json,sys; d=json.load(sys.stdin); assert $2, d" 2>/dev/null; then
    echo "ok   $1"
  else
    echo "FAIL $1"; fail=1
  fi
}

run() { echo '{}' | CLAUDE_PLUGIN_ROOT="$ROOT" CLAUDE_PROJECT_DIR="$TMP" "$ROOT/hooks/$1"; }

# Sem NORTE.md
run session-start | check "session-start sem NORTE injeta using-onedirection" \
  "'using-onedirection' in d['hookSpecificOutput']['additionalContext'] and 'ainda não tem NORTE.md' in d['hookSpecificOutput']['additionalContext']"
run user-prompt-submit | check "user-prompt-submit sem NORTE fica quieto" "d == {}"

# Com NORTE.md (aspas, barra e tab pra testar o escape)
printf '# NORTE — teste\n\n## A promessa\n"X" ajuda Y\\Z\tagora\n' > "$TMP/NORTE.md"
run session-start | check "session-start com NORTE injeta o arquivo" \
  "'\"X\" ajuda Y\\\\Z\tagora' in d['hookSpecificOutput']['additionalContext']"
run user-prompt-submit | check "user-prompt-submit com NORTE lembra" \
  "d['hookSpecificOutput']['hookEventName'] == 'UserPromptSubmit'"

# Manifestos válidos
for f in .claude-plugin/plugin.json .claude-plugin/marketplace.json hooks/hooks.json; do
  check "$f é JSON válido" "True" < "$ROOT/$f"
done

exit $fail
