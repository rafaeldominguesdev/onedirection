# onedirection

onedirection é uma disciplina de foco pro seu agente de código: um conjunto de skills e um hook de início de sessão que garantem que o Claude nunca perca a ideia original do projeto, não invente fatos sobre ele e não diga "pronto" sem prova.

## Sumário

- [Como funciona](#como-funciona)
- [Instalação](#instalação)
- [O fluxo básico](#o-fluxo-básico)
- [O NORTE.md](#o-nortemd)
- [Quando algo dá errado](#quando-algo-dá-errado)
- [O que tem dentro](#o-que-tem-dentro)
- [Filosofia](#filosofia)
- [Contribuindo](#contribuindo)
- [Atualizando](#atualizando)
- [Licença](#licença)

## Como funciona

Começa no momento em que você abre o Claude. Se o projeto ainda não existe, ele *não* sai escrevendo código. Primeiro pergunta o que você quer de verdade — o problema, pra quem é, a promessa em uma frase, o que o v1 precisa ter e, principalmente, o que o projeto **não é**. Devolve o que entendeu em partes curtas, você corrige, e só quando você aprova ele grava tudo num `NORTE.md` na raiz.

Se o projeto já está em andamento, ele lê tudo antes de mexer: docs, manifestos, os primeiros commits (onde a ideia original costuma morar), o código e o que realmente funciona. Reconstrói a ideia com fonte pra cada afirmação, marca com `(?)` o que é dedução, aponta onde o projeto já fugiu do caminho e te pede pra confirmar.

Daí em diante, o `NORTE.md` entra no contexto do Claude no início de toda sessão — e de novo depois de cada compactação, que é exatamente quando agentes costumam esquecer o que estavam fazendo. A cada mensagem sua, ele recebe um lembrete curto com o "Foco agora". Quando um pedido foge do norte, ele para antes de codar, cita o trecho literal do `NORTE.md` e te dá três saídas: mudar o norte (com registro), anotar pra depois ou deixar pra lá. Quando é ele mesmo quem está fugindo — a refatoração "rápida", a lib "melhor" —, a mesma regra vale.

E antes de dizer "pronto", ele roda a verificação, relê o seu pedido item a item e confere o `git diff` atrás de arquivos que ninguém pediu. Como as skills disparam sozinhas, você não precisa fazer nada de especial.

## Instalação

### Claude Code

Pelo marketplace do onedirection:

```bash
/plugin marketplace add rafaeldominguesdev/onedirection
/plugin install onedirection@onedirection
```

Reinicie o Claude depois de instalar.

Pra desenvolver localmente, a partir de um clone:

```bash
claude plugin marketplace add ~/onedirection
claude plugin install onedirection@onedirection
```

## O fluxo básico

1. **capturing-the-vision** — Ativa antes de construir qualquer coisa num projeto novo. Entrevista uma pergunta por vez, devolve o que entendeu em partes, separa o que você disse do que ele propôs e grava o `NORTE.md`. Nada de código antes da sua aprovação.
2. **mapping-existing-project** — Ativa num projeto com código e sem `NORTE.md`. Lê docs, história do git e código; toda afirmação tem fonte; o que é dedução fica `(?)`; aponta os desvios e confirma com você.
3. **guarding-the-direction** — Ativa quando um pedido (seu ou dele) pode mexer em escopo. Cabe no norte: faz. Foge: para, cita o trecho do `NORTE.md` e oferece as 3 saídas. Mantém um foco por vez.
4. **verifying-before-done** — Ativa antes de qualquer "pronto", "funciona", "corrigi" ou commit. Prova nova, pedido relido item a item, `git diff` conferido contra o pedido.
5. **recovering-focus** — Ativa depois de uma compactação ou retomada. Reconstrói o ponto exato pelo `NORTE.md` e pelo git, não pela memória, e declara onde está antes de continuar.
6. **checking-progress** — Ativa em "onde estamos?" ou no fim de uma etapa. Verifica cada item do v1 no código, com evidência, e aponta o próximo passo.

**O agente confere as skills antes de qualquer tarefa.** São fluxos obrigatórios, não sugestões.

## O NORTE.md

Um arquivo curto (até ~80 linhas) na raiz do projeto. É a fonte da verdade da **intenção** — o código é a fonte da verdade da implementação.

```markdown
# NORTE — <projeto>
## A promessa            uma frase: X ajuda Y a fazer Z
## Problema e público
## v1 obrigatório        checkboxes
## NÃO é                 não-objetivos — o que segura a direção
## Restrições
## Pronto quando         critérios verificáveis
## Foco agora            o que está sendo feito + próximo passo
## Estado
## Decisões              AAAA-MM-DD — decisão — porque motivo
## Depois                backlog fora do v1
```

Você é dono do arquivo: o Claude só muda promessa, v1, não-objetivos e decisões com a sua escolha explícita. "Foco agora" e "Estado" são o caderno de bordo dele e ficam sempre atualizados.

## Quando algo dá errado

Se o Claude parecer perdido — repetindo trabalho, inventando nome de arquivo, esquecendo o que estava fazendo — diga "você perdeu o foco" ou "onde a gente tava?". Isso dispara **recovering-focus**, que reconstrói o ponto exato a partir do `NORTE.md` e do git. Se o problema for o próprio norte (desatualizado ou longo demais), peça "confere o progresso" pra disparar **checking-progress**.

## O que tem dentro

### Biblioteca de skills

**Visão**
- **capturing-the-vision** — Entrevista e grava a ideia original (inclui `norte-template.md`)
- **mapping-existing-project** — Reconstrói a ideia de um projeto em andamento, com evidência

**Foco**
- **guarding-the-direction** — Guarda de escopo, inclusive contra a fuga do próprio agente
- **recovering-focus** — Retomada depois de compactação, pelas fontes e não pela memória

**Verificação**
- **verifying-before-done** — Prova antes de afirmação; pedido e diff conferidos
- **checking-progress** — O v1 conferido no código, item a item

**Meta**
- **using-onedirection** — Introdução ao sistema, injetada em toda sessão

### Hooks

- **SessionStart** (`startup`, `clear`, `compact`) — injeta `using-onedirection` e o `NORTE.md`; na compactação, manda usar `recovering-focus`.
- **UserPromptSubmit** — em projetos com `NORTE.md`, um lembrete de uma linha e a seção "Foco agora".

## Filosofia

- **Uma direção** — O `NORTE.md` manda no escopo; mudar de ideia é permitido, mudar sem registrar não
- **Não-objetivos primeiro** — O que o projeto não é segura mais que o que ele é
- **Evidência antes de afirmação** — Fato sobre o projeto só com fonte; "pronto" só com prova
- **O disco não esquece** — Memória de conversa falha numa compactação; arquivo não
- **O usuário manda** — O onedirection avisa, não bloqueia

## Contribuindo

1. Faça um fork do repositório
2. Crie uma branch pro seu trabalho
3. Mantenha cada skill curta e com um trabalho só; regras duras em blocos (`<HARD-GATE>`, Lei de Ferro) e racionalizações em tabela "Pensamento | Realidade"
4. Rode os testes: `bash tests/hooks/test-hooks.sh` e `claude plugin validate .`
5. Abra um PR explicando, com as suas palavras, o problema que a mudança resolve

## Atualizando

`/plugin marketplace update onedirection` e reinicie o Claude.

## Licença

MIT — veja o arquivo LICENSE.
