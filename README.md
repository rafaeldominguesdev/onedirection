# onedirection

Plugin do Claude Code que não deixa o projeto perder a ideia original.

A ideia fica escrita num `NORTE.md` na raiz do projeto. Um hook coloca esse arquivo no contexto no início de toda sessão e depois de cada compactação, e as skills conferem cada mudança de escopo contra ele.

## Como funciona

1. **Projeto novo** → `capturing-the-vision`: entrevista curta (problema, público, promessa, v1, **não-objetivos**, restrições, critério de pronto) e grava o `NORTE.md`. Nada de código antes da aprovação.
2. **Projeto em andamento** → `mapping-existing-project`: lê docs, história do git e código, reconstrói a ideia, aponta onde o projeto já fugiu dela e grava o `NORTE.md` confirmado.
3. **Dia a dia** → `guarding-the-direction`: quando um pedido foge do norte, para antes de codar e oferece 3 saídas — mudar o norte (com registro em "Decisões"), anotar em "Depois" ou deixar pra lá.
4. **Onde estamos?** → `checking-progress`: compara cada item do v1 com o que o código realmente faz.

`using-onedirection` é a porta de entrada: o hook a injeta em toda sessão e ela decide qual skill usar.

## Instalação

Dentro do Claude Code:

```
/plugin marketplace add rafaeldominguesdev/onedirection
/plugin install onedirection@onedirection
```

Reinicie o Claude depois de instalar.

Pra desenvolver localmente: `claude plugin marketplace add ~/onedirection`.

## Uso

- Automático: abra o Claude num projeto e comece a pedir coisas.
- Manual: `/onedirection:checking-progress`, `/onedirection:capturing-the-vision` etc.

## Estrutura

```
.claude-plugin/       plugin.json + marketplace.json
hooks/                hooks.json, session-start, user-prompt-submit
skills/
  using-onedirection/        porta de entrada (injetada pelo hook)
  capturing-the-vision/      projeto novo + norte-template.md
  mapping-existing-project/  projeto em andamento
  guarding-the-direction/    guarda de escopo
  checking-progress/         status contra o norte
tests/hooks/          teste dos hooks
```

## Testes

```bash
bash tests/hooks/test-hooks.sh
```
