#!/usr/bin/env bash
# Funções compartilhadas pelos hooks do onedirection.
# shellcheck disable=SC2034  # as variáveis OD_* são saídas de od_resolve, lidas por quem dá source neste arquivo
# Sem dependência de binários externos (dirname, git, cat): o PATH pode vir quebrado no startup.
#
# Regra de portabilidade: nenhum ${var//padrão/substituto} deste plugin pode ter "&" no substituto.
# No bash >= 5.2 (shopt patsub_replacement, ligado por padrão) um "&" ali vira o trecho casado,
# e no bash 3.2 do macOS vira um "&" literal: o mesmo código faz coisas diferentes. Os testes conferem isso.

# Limites do que entra no contexto vindo do NORTE.md.
OD_NORTE_MAX_BYTES=12000
OD_FOCO_MAX_CHARS=1200

# od_norte_ok CAMINHO: 0 se o arquivo pode ser lido como NORTE.md.
# Só arquivo regular e que não seja link simbólico: um repositório de terceiros pode trazer
# NORTE.md -> ../../.ssh/id_ed25519, e o conteúdo iria parar no contexto (e na API).
od_norte_ok() {
  [ -f "$1" ] && [ ! -L "$1" ] && [ -r "$1" ]
}

# od_resolve: descobre onde está o projeto e o NORTE.md.
# Define:
#   OD_PROJECT_DIR  pasta onde o Claude foi aberto
#   OD_ROOT         raiz do projeto (pasta do NORTE.md, raiz do git, ou a própria pasta)
#   OD_NORTE        caminho do NORTE.md, ou vazio
#   OD_NORTE_REFUSED caminho de um NORTE.md recusado (link simbólico ou não regular), ou vazio
#   OD_IS_PROJECT   1 se parece projeto (NORTE.md, git ou manifesto), 0 se não
od_resolve() {
  local dir="${CLAUDE_PROJECT_DIR:-$PWD}"
  local home="${HOME:-}"
  OD_PROJECT_DIR="$dir"
  OD_ROOT="$dir"
  OD_NORTE=""
  OD_NORTE_REFUSED=""
  OD_IS_PROJECT=0

  # Sobe até achar um .git. Um repositório na própria $HOME (dotfiles) não conta como projeto.
  local d="$dir" git_root=""
  while [ -n "$d" ]; do
    if [ -e "$d/.git" ] && [ "$d" != "$home" ]; then git_root="$d"; break; fi
    [ "$d" = "/" ] && break
    d="${d%/*}"
    [ -z "$d" ] && d="/"
  done

  local cand
  for cand in "$dir" "$git_root"; do
    [ -n "$cand" ] || continue
    if [ -e "$cand/NORTE.md" ] || [ -L "$cand/NORTE.md" ]; then
      OD_ROOT="$cand"; OD_IS_PROJECT=1
      if od_norte_ok "$cand/NORTE.md"; then OD_NORTE="$cand/NORTE.md"; else OD_NORTE_REFUSED="$cand/NORTE.md"; fi
      return 0
    fi
  done

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
od_validate_norte() {
  if [ ! -r "$1" ]; then echo "não foi possível ler $1"; return 0; fi
  od_validate_text < "$1"
}

# Nomes de tag que o plugin usa como moldura ou delimitador, em qualquer caixa, com - ou _.
OD_TAG_NORTE='[Nn][Oo][Rr][Tt][Ee][-_][Mm][Dd]'
OD_TAG_IMPORTANT='[Ee][Xx][Tt][Rr][Ee][Mm][Ee][Ll][Yy][-_][Ii][Mm][Pp][Oo][Rr][Tt][Aa][Nn][Tt]'

# od_validate_text: valida um NORTE.md lido do stdin. Mesma saída de od_validate_norte.
# Compatível com bash 3.2 (macOS): sem arrays associativos.
od_validate_text() {
  local line key="" total=0 plain
  local n_promessa=0 n_problema=0 n_v1=0 n_nao=0 n_pronto=0 n_foco=0 n_estado=0 n_decisoes=0 n_depois=0
  local s_promessa=0 s_problema=0 s_v1=0 s_nao=0 s_pronto=0 s_foco=0 s_estado=0 s_decisoes=0 s_depois=0
  local placeholders=0 ctl_line=0 tag_line=0

  while IFS= read -r line || [ -n "$line" ]; do
    total=$((total + 1))
    # Caractere de controle (fora tab e o \r do fim de linha do Windows): sequência ESC pode esconder texto de quem lê no terminal.
    plain="${line%$'\r'}"; plain="${plain//$'\t'/}"
    case "$plain" in *[[:cntrl:]]*) [ "$ctl_line" = 0 ] && ctl_line=$total ;; esac
    case "$line" in *"<"*$OD_TAG_NORTE*|*"<"*$OD_TAG_IMPORTANT*) [ "$tag_line" = 0 ] && tag_line=$total ;; esac
    case "$line" in
      "## A promessa"*|"## Promessa"*) key=promessa; s_promessa=$((s_promessa + 1)); continue ;;
      "## Problema"*) key=problema; s_problema=$((s_problema + 1)); continue ;;
      "## v1"*|"## V1"*) key=v1; s_v1=$((s_v1 + 1)); continue ;;
      "## NÃO é"*|"## Não é"*|"## NAO"*|"## Não-objetivos"*|"## Não objetivos"*) key=nao; s_nao=$((s_nao + 1)); continue ;;
      "## Pronto quando"*) key=pronto; s_pronto=$((s_pronto + 1)); continue ;;
      "## Foco agora"*) key=foco; s_foco=$((s_foco + 1)); continue ;;
      "## Estado"*) key=estado; s_estado=$((s_estado + 1)); continue ;;
      "## Decisões"*|"## Decisoes"*) key=decisoes; s_decisoes=$((s_decisoes + 1)); continue ;;
      "## Depois"*) key=depois; s_depois=$((s_depois + 1)); continue ;;
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
  done

  local k label
  for k in promessa problema v1 nao pronto foco estado decisoes; do
    case "$k" in
      promessa) label="## A promessa" ;;
      problema) label="## Problema e público" ;;
      v1) label="## v1 obrigatório" ;;
      nao) label="## NÃO é" ;;
      pronto) label="## Pronto quando" ;;
      foco) label="## Foco agora" ;;
      estado) label="## Estado" ;;
      decisoes) label="## Decisões" ;;
    esac
    local seen=0
    case "$k" in
      promessa) seen=$s_promessa ;; problema) seen=$s_problema ;; v1) seen=$s_v1 ;; nao) seen=$s_nao ;;
      pronto) seen=$s_pronto ;; foco) seen=$s_foco ;; estado) seen=$s_estado ;; decisoes) seen=$s_decisoes ;;
    esac
    if [ "$seen" = 0 ]; then
      case "$k" in
        nao) echo "falta a seção \"$label\" (não-objetivos): é ela que segura a direção" ;;
        foco) echo "falta a seção \"$label\": é ela que traz o trabalho de volta depois de uma compactação" ;;
        *) echo "falta a seção \"$label\"" ;;
      esac
    elif [ "$seen" -gt 1 ]; then
      echo "a seção \"$label\" aparece ${seen} vezes: deixe uma só"
    fi
  done
  [ "$s_depois" -gt 1 ] && echo "a seção \"## Depois\" aparece ${s_depois} vezes: deixe uma só"
  [ "$s_promessa" -gt 0 ] && [ "$n_promessa" = 0 ] && echo "a promessa está vazia"
  [ "$s_v1" -gt 0 ] && [ "$n_v1" = 0 ] && echo "o v1 não tem nenhum item com checkbox (- [ ] ...)"
  [ "$n_v1" -gt 4 ] && echo "o v1 tem ${n_v1} itens (máximo 4): o que não é indispensável pra promessa vai pra \"Depois\""
  [ "$s_nao" -gt 0 ] && [ "$n_nao" = 0 ] && echo "não há nenhum não-objetivo escrito"
  [ "$s_pronto" -gt 0 ] && [ "$n_pronto" = 0 ] && echo "\"Pronto quando\" está vazio: sem critério verificável não há como saber que acabou"
  [ "$placeholders" -gt 0 ] && echo "ainda há ${placeholders} linha(s) do modelo sem preencher (\"...\", \"<...>\")"
  [ "$total" -gt 120 ] && echo "o arquivo tem ${total} linhas (o ideal é até ~80): ele é lido em toda sessão"
  [ "$ctl_line" != 0 ] && echo "a linha ${ctl_line} tem caractere de controle invisível (ex.: ESC): ele pode esconder texto de quem lê o arquivo no terminal"
  [ "$tag_line" != 0 ] && echo "a linha ${tag_line} tem uma tag que imita as do plugin (norte-md ou EXTREMELY_IMPORTANT entre sinais de menor e maior): ela é neutralizada na injeção, mas confira quem a escreveu"
  return 0
}

# od_read_head ARQUIVO MAX_BYTES: lê no máximo MAX_BYTES bytes, sem ler o resto do arquivo.
# Define OD_HEAD (sem as quebras de linha do fim) e OD_HEAD_CUT (1 se o arquivo passava do limite).
# Roda em LC_ALL=C num subshell: aí "read -n" e "${#var}" contam bytes nos dois (no bash 3.2 com
# UTF-8, read -n conta bytes e ${#var} conta caracteres, e o corte não disparava). O corte cai no
# fim de uma linha, então nunca parte um caractere UTF-8 no meio. Conteúdo depois de um NUL não é lido.
od_read_head() {
  local out
  out="$(_od_read_head_c "$1" "$2")"
  OD_HEAD_CUT="${out:0:1}"
  OD_HEAD="${out:1}"
}
# Função separada (e não o corpo direto dentro de $( )): o bash 3.2 não sabe ler "case ... in x)" ali dentro.
_od_read_head_c() (
  LC_ALL=C
  max="$2" buf="" cut=0
  IFS= read -r -d '' -n $((max + 1)) buf < "$1" || :
  if [ "${#buf}" -gt "$max" ]; then
    cut=1
    buf="${buf:0:$max}"
    case "$buf" in
      *$'\n'*) buf="${buf%$'\n'*}" ;;
      *) buf="" ;;  # uma linha só, maior que o limite: melhor não injetar nada do que um pedaço partido
    esac
  fi
  printf '%s%s' "$cut" "$buf"
)

# od_neutralize TEXTO: troca todo "<" por "‹" e todo ">" por "›".
# Assim nada vindo do NORTE.md consegue abrir ou fechar tag nenhuma (nem </norte-md>, nem
# <EXTREMELY_IMPORTANT>, em qualquer caixa ou espaçamento). O substituto não tem "&", "\" nem
# aspas, então o resultado é igual em todo bash (veja a regra de portabilidade no topo).
# Em LC_ALL=C (subshell): "<" e ">" são ASCII e nunca aparecem dentro de um caractere UTF-8, e a troca
# byte a byte é bem mais rápida que a do bash 3.2 em UTF-8.
od_neutralize() (
  LC_ALL=C
  s="$1"
  s="${s//</‹}"
  s="${s//>/›}"
  printf '%s' "$s"
)

# Lê o stdin do hook inteiro, sem cat.
od_read_stdin() {
  local line out=""
  while IFS= read -r line 2>/dev/null || [ -n "$line" ]; do out="${out}${line}"; line=""; done || :
  printf '%s' "$out"
}

# escape_for_json TEXTO: escapa pra dentro de uma string JSON (RFC 8259: barra, aspas e todo U+0000-U+001F).
# NUL não chega aqui: o bash não guarda NUL em variável.
# Em LC_ALL=C (subshell): todos os caracteres escapados são ASCII, que nunca aparecem dentro de um
# caractere UTF-8, então trocar byte a byte é correto; e [[:cntrl:]] fica só em 0x00-0x1F e 0x7F.
escape_for_json() (
  LC_ALL=C
  s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"
  s="${s//$'\r'/\\r}"
  s="${s//$'\t'/\\t}"
  s="${s//$'\b'/\\b}"
  s="${s//$'\f'/\\f}"
  case "$s" in
    *[[:cntrl:]]*)
      for i in 1 2 3 4 5 6 7 11 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31; do
        printf -v hex '%02x' "$i"
        # shellcheck disable=SC2059  # o formato \xHH é montado de propósito: gera o byte de controle
        printf -v c "\\x${hex}"
        case "$s" in *"$c"*) s="${s//"$c"/\\u00${hex}}" ;; esac
      done ;;
  esac
  printf '%s' "$s"
)

# od_emit EVENTO CONTEXTO: imprime o JSON do hook. Contexto vazio = {}.
od_emit() {
  if [ -z "$2" ]; then printf '{}\n'; return 0; fi
  printf '{\n  "hookSpecificOutput": {\n    "hookEventName": "%s",\n    "additionalContext": "%s"\n  }\n}\n' "$1" "$(escape_for_json "$2")"
}
