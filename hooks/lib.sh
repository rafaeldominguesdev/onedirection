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

# od_validate_norte ARQUIVO: imprime um problema por linha (nada = arquivo ok).
# Compatível com bash 3.2 (macOS): sem arrays associativos.
od_validate_norte() {
  local file="$1" line key="" total=0
  local n_promessa=0 n_problema=0 n_v1=0 n_nao=0 n_pronto=0 n_foco=0 n_estado=0 n_decisoes=0 n_depois=0
  local s_promessa=0 s_problema=0 s_v1=0 s_nao=0 s_pronto=0 s_foco=0 s_estado=0 s_decisoes=0 s_depois=0
  local placeholders=0

  if [ ! -r "$file" ]; then echo "não foi possível ler $file"; return 0; fi

  while IFS= read -r line || [ -n "$line" ]; do
    total=$((total + 1))
    case "$line" in
      "## A promessa"*|"## Promessa"*) key=promessa; s_promessa=1; continue ;;
      "## Problema"*) key=problema; s_problema=1; continue ;;
      "## v1"*|"## V1"*) key=v1; s_v1=1; continue ;;
      "## NÃO é"*|"## Não é"*|"## NAO"*|"## Não-objetivos"*|"## Não objetivos"*) key=nao; s_nao=1; continue ;;
      "## Pronto quando"*) key=pronto; s_pronto=1; continue ;;
      "## Foco agora"*) key=foco; s_foco=1; continue ;;
      "## Estado"*) key=estado; s_estado=1; continue ;;
      "## Decisões"*|"## Decisoes"*) key=decisoes; s_decisoes=1; continue ;;
      "## Depois"*) key=depois; s_depois=1; continue ;;
      "## "*) key=outro; continue ;;
      "# "*) continue ;;
    esac
    case "$line" in
      *"<uma frase"*|*"<nome do projeto>"*|*"<decisão>"*|*"<a única coisa"*|"- ..."|"- [ ] ..."|"- Problema: ..."|"- Pra quem: ..."|"- Stack: ..."|"- Não é ..."|"- Não vai ter ...")
        placeholders=$((placeholders + 1)); continue ;;
    esac
    [ -z "$line" ] && continue
    case "$key" in
      promessa) n_promessa=$((n_promessa + 1)) ;;
      problema) n_problema=$((n_problema + 1)) ;;
      v1) case "$line" in "- [ ]"*|"- [x]"*|"- [X]"*) n_v1=$((n_v1 + 1)) ;; esac ;;
      nao) case "$line" in "- "*) n_nao=$((n_nao + 1)) ;; esac ;;
      pronto) case "$line" in "<"*) ;; *) n_pronto=$((n_pronto + 1)) ;; esac ;;
      foco) n_foco=$((n_foco + 1)) ;;
      estado) case "$line" in "<"*) ;; *) n_estado=$((n_estado + 1)) ;; esac ;;
      decisoes) n_decisoes=$((n_decisoes + 1)) ;;
      depois) n_depois=$((n_depois + 1)) ;;
    esac
  done < "$file"

  [ "$s_promessa" = 1 ] || echo "falta a seção \"## A promessa\""
  [ "$s_promessa" = 1 ] && [ "$n_promessa" = 0 ] && echo "a promessa está vazia"
  [ "$s_problema" = 1 ] || echo "falta a seção \"## Problema e público\""
  [ "$s_v1" = 1 ] || echo "falta a seção \"## v1 obrigatório\""
  [ "$s_v1" = 1 ] && [ "$n_v1" = 0 ] && echo "o v1 não tem nenhum item com checkbox (- [ ] ...)"
  [ "$s_nao" = 1 ] || echo "falta a seção \"## NÃO é\" (não-objetivos): é ela que segura a direção"
  [ "$s_nao" = 1 ] && [ "$n_nao" = 0 ] && echo "não há nenhum não-objetivo escrito"
  [ "$s_pronto" = 1 ] || echo "falta a seção \"## Pronto quando\""
  [ "$s_pronto" = 1 ] && [ "$n_pronto" = 0 ] && echo "\"Pronto quando\" está vazio: sem critério verificável não há como saber que acabou"
  [ "$s_foco" = 1 ] || echo "falta a seção \"## Foco agora\": é ela que traz o trabalho de volta depois de uma compactação"
  [ "$s_estado" = 1 ] || echo "falta a seção \"## Estado\""
  [ "$s_decisoes" = 1 ] || echo "falta a seção \"## Decisões\""
  [ "$placeholders" -gt 0 ] && echo "ainda há ${placeholders} linha(s) do modelo sem preencher (\"...\", \"<...>\")"
  [ "$total" -gt 120 ] && echo "o arquivo tem ${total} linhas (o ideal é até ~80): ele é lido em toda sessão"
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
