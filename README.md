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
- [Testes](#testes)
- [Compatibilidade e limites](#compatibilidade-e-limites)
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

A cerimônia é proporcional ao risco: **rápido** pra bug e ajuste (faz direto), **normal** pra funcionalidade nova (faz e registra), **rigoroso** pra arquitetura, segurança ou conflito com o norte, e **projeto novo** com entrevista. A matriz completa de quando cada skill entra está em [`docs/gatilhos.md`](docs/gatilhos.md), e um exemplo do começo ao fim em [`docs/exemplo-completo.md`](docs/exemplo-completo.md).


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

- **SessionStart** (`startup`, `clear`, `compact`) — injeta só o necessário, em três níveis:
  - **com `NORTE.md`**: a skill `using-onedirection` inteira + o `NORTE.md` (achado na pasta ou na raiz do git, se você abrir o Claude numa subpasta);
  - **projeto sem `NORTE.md`**: as regras essenciais em poucas linhas (~1.000 caracteres);
  - **fora de projeto** (sem git, sem manifesto, ou a sua pasta pessoal): uma linha (~150 caracteres).
  Na compactação, em projeto, manda usar `recovering-focus`.
- **UserPromptSubmit** — só em projetos com `NORTE.md`: sempre a seção "Foco agora"; a linha de regras só quando o pedido fala de escopo, implementação ou conclusão.
- **Stop** — "pronto" sem prova não passa. Se o Claude editou código, não conferiu nada depois da última edição e diz que terminou sem admitir que não verificou, a resposta volta pra ele **uma vez** pra conferir ou declarar "Não verifiquei: …". Precisa de `python3`; sem ele, esse hook não faz nada.

### Validador do NORTE.md

```bash
scripts/validate-norte            # ./NORTE.md
scripts/validate-norte outro/NORTE.md
```

Confere se as seções existem, se o v1 tem itens, se há não-objetivos e critério de pronto, se sobrou trecho do modelo sem preencher e se o arquivo não passou de 120 linhas. O hook de início de sessão roda a mesma validação e, se achar problema, o Claude te avisa uma vez.

## Filosofia

- **Uma direção** — O `NORTE.md` manda no escopo; mudar de ideia é permitido, mudar sem registrar não
- **Não-objetivos primeiro** — O que o projeto não é segura mais que o que ele é
- **Evidência antes de afirmação** — Fato sobre o projeto só com fonte; "pronto" só com prova
- **O disco não esquece** — Memória de conversa falha numa compactação; arquivo não
- **O usuário manda** — O onedirection avisa, não bloqueia

## Testes

Dois níveis:

- **Hooks e estrutura** (rápido, grátis): `bash tests/hooks/test-hooks.sh`
- **Comportamento** (sessões reais do Claude, ~US$ 0,20–0,80 cada): `python3 tests/evals/run.py`

Os testes de comportamento rodam cada cenário de `tests/evals/scenarios.json` numa sessão nova do Claude, numa cópia temporária de um projeto de mentira, com a versão **local** do plugin. Depois corrigem automaticamente o transcript e os arquivos:

| Cenário | O que prova |
|---|---|
| `evolucao` | Ideia nova que serve à promessa é feita e registrada, sem alarme |
| `conflito` | Pedido que bate num não-objetivo para antes do código e cita o trecho |
| `pedido-pequeno` | Ajuste pequeno sem cerimônia e sem cair na isca do `TODO: refatorar` |
| `alucinacao` | Pergunta sobre função inexistente: procura e diz que não existe |
| `retomada` | Trabalho pela metade: reconstrói pelo `NORTE.md` e pelo git |
| `mapeamento` | Projeto sem `NORTE.md`: mapeia primeiro e não grava nada sem aprovação |
| `projeto-novo` | Pasta vazia: entrevista antes de qualquer código |
| `fora-de-projeto` | Fora de projeto: fica quieto e quase não gasta contexto |
| `pronto-sem-prova` | Usuário pede pra não conferir: pode atender, mas não afirma que funciona sem admitir |
| `progresso-desatualizado` | `NORTE.md` diz que o v1 está pronto e o código não: checkbox não é prova |
| `aceitacao-projeto-novo` | Ponta a ponta: `NORTE.md` escrito **antes** do código, com os não-objetivos do usuário, v1 mínimo (até 4 itens) e sem estado futuro inventado |
| `stop-hook-ativo` | Força um "Pronto." seco depois de editar: o hook devolve a resposta uma vez e o fim fica honesto |
| `compactacao-real` | Sessão com trabalho pela metade, `/compact` de verdade e "continua": o hook avisa e o Claude retoma pelo `NORTE.md` e pelo git |

Rode um só com `python3 tests/evals/run.py conflito`, meça instabilidade com `--repeat 3` e troque o modelo com `EVAL_MODEL=sonnet`.

No GitHub, os testes dos hooks rodam a cada push (Ubuntu e macOS, incluindo o bash 3.2 do macOS) junto com `claude plugin validate`. Os de comportamento custam, então rodam à mão: **Actions › comportamento › Run workflow**, com o segredo `ANTHROPIC_API_KEY` configurado.

## Compatibilidade e limites

| Tema | Situação |
|---|---|
| Claude Code | Testado na 2.1.316. Usa hooks de plugin `SessionStart`, `UserPromptSubmit` e `Stop` |
| Modelos | Testes de comportamento rodados no Opus e no Sonnet. Outros modelos: não testados |
| Sistema | macOS (bash 3.2 do sistema ou mais novo) e Linux. **Windows não é suportado** |
| `python3` | Opcional. Só o hook de fim de resposta usa; sem ele, esse hook fica desligado e o resto funciona |
| Sem git | Funciona. O projeto é reconhecido por manifesto (`package.json`, `Cargo.toml`…); `recovering-focus` perde a parte do histórico |
| Monorepo | O `NORTE.md` é procurado na pasta onde o Claude abriu e depois na raiz do git. Um por pacote, ou um na raiz |
| Worktrees | Funciona: o `NORTE.md` é versionado e o `.git` em forma de arquivo é reconhecido |
| Pasta pessoal | Nunca é tratada como projeto, mesmo com repositório de dotfiles |
| Outros plugins de fluxo | Pensado pra conviver com a superpowers (onedirection decide **o quê**, ela decide **o como**). **Ainda não testado em conjunto** |
| Contexto gasto | Fora de projeto ~150 caracteres; projeto sem `NORTE.md` ~900; com `NORTE.md`, a skill de entrada inteira + o arquivo |

**Desativar por um tempo:** `/plugin disable onedirection@onedirection` (reative com `/plugin enable onedirection@onedirection`).

**`NORTE.md` desatualizado:** peça "confere o progresso" (dispara `checking-progress`, que compara cada item com o código) ou rode `scripts/validate-norte` pra conferir a estrutura.

**Limite honesto:** as regras são instruções pro modelo, e só uma delas é cobrada por código (o hook de "pronto" sem prova). O resto é medido pelos testes de comportamento, não garantido. Modelos diferentes seguem as instruções de jeitos diferentes: o Sonnet, por exemplo, só passou a registrar ideias novas em "Decisões" depois que a regra entrou no lembrete de cada mensagem.

## Contribuindo

1. Faça um fork do repositório
2. Crie uma branch pro seu trabalho
3. Mantenha cada skill curta e com um trabalho só; regras duras em blocos (`<HARD-GATE>`, Lei de Ferro) e racionalizações em tabela "Pensamento | Realidade"
4. Rode os dois níveis de teste. Mudou o texto de uma skill? Os testes de comportamento são obrigatórios: é assim que se descobre que uma frase nova quebrou um caso antigo
5. Abra um PR explicando, com as suas palavras, o problema que a mudança resolve

## Atualizando

`/plugin marketplace update onedirection` e reinicie o Claude.

## Licença

MIT — veja o arquivo LICENSE.
