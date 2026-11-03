#!/usr/bin/env bash
# Funções compartilhadas pelos hooks do onedirection.
# Sem dependência de binários externos (dirname, git, cat): o PATH pode vir quebrado no startup.

# od_resolve: descobre onde está o projeto e o NORTE.md.
# Define:
#   OD_PROJECT_DIR  pasta onde o Claude foi aberto
#   OD_ROOT         raiz do projeto (pasta do NORTE.md, raiz do git, ou a própria pasta)
#   OD_NORTE        caminho do NORTE.md, ou vazio
#   OD_IS_PROJECT   1 se parece projeto (NORTE.md, git ou manifesto), 0 se não
od_resolve() {
  local dir="${CLAUDE_PROJECT_DIR:-$PWD}"
  local home="${HOME:-}"
  OD_PROJECT_DIR="$dir"
  OD_ROOT="$dir"
  OD_NORTE=""
  OD_IS_PROJECT=0

  # Sobe até achar um .git. Um repositório na própria $HOME (dotfiles) não conta como projeto.
  local d="$dir" git_root=""
  while [ -n "$d" ]; do
    if [ -e "$d/.git" ] && [ "$d" != "$home" ]; then git_root="$d"; break; fi
    [ "$d" = "/" ] && break
    d="${d%/*}"
    [ -z "$d" ] && d="/"
  done

  if [ -r "$dir/NORTE.md" ]; then
    OD_NORTE="$dir/NORTE.md"; OD_ROOT="$dir"; OD_IS_PROJECT=1; return 0
  fi
  if [ -n "$git_root" ] && [ -r "$git_root/NORTE.md" ]; then
    OD_NORTE="$git_root/NORTE.md"; OD_ROOT="$git_root"; OD_IS_PROJECT=1; return 0
  fi

  # A pasta pessoal nunca é projeto, a menos que tenha NORTE.md (tratado acima).
  if [ "$dir" = "$home" ]; then return 0; fi

  if [ -n "$git_root" ]; then OD_ROOT="$git_root"; OD_IS_PROJECT=1; return 0; fi

  local m
  for m in package.json Cargo.toml pyproject.toml go.mod Package.swift requirements.txt \
           Gemfile composer.json pom.xml build.gradle build.gradle.kts deno.json \
           pubspec.yaml mix.exs CMakeLists.txt Makefile; do
    if [ -e "$dir/$m" ]; then OD_IS_PROJECT=1; return 0; fi
  done
  return 0
}

# Lê o stdin do hook inteiro, sem cat.
od_read_stdin() {
  local line out=""
  while IFS= read -r line 2>/dev/null || [ -n "$line" ]; do out="${out}${line}"; line=""; done || :
  printf '%s' "$out"
}

escape_for_json() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"
  s="${s//$'\r'/\\r}"
  s="${s//$'\t'/\\t}"
  printf '%s' "$s"
}

# od_emit EVENTO CONTEXTO: imprime o JSON do hook. Contexto vazio = {}.
od_emit() {
  if [ -z "$2" ]; then printf '{}\n'; return 0; fi
  printf '{\n  "hookSpecificOutput": {\n    "hookEventName": "%s",\n    "additionalContext": "%s"\n  }\n}\n' "$1" "$(escape_for_json "$2")"
}
