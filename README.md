# onedirection

onedirection é uma disciplina de foco pro seu agente de código: sete skills, três hooks e um validador que **orientam** o Claude a não perder a ideia original do projeto, a não inventar fatos sobre ele e a não dizer "pronto" sem prova, e que **cobram por código** a parte que dá pra cobrar. O que é cobrado e o que depende do modelo está explicado em [O que é garantido e o que não é](#o-que-é-garantido-e-o-que-não-é).

## Sumário

- [Como funciona](#como-funciona)
- [Em 5 minutos](#em-5-minutos)
- [Instalação](#instalação)
- [O fluxo básico](#o-fluxo-básico)
- [O NORTE.md](#o-nortemd)
- [Quando algo dá errado](#quando-algo-dá-errado)
- [O que tem dentro](#o-que-tem-dentro)
- [Filosofia](#filosofia)
- [Testes](#testes)
- [Segurança e privacidade](#segurança-e-privacidade)
- [Compatibilidade e limites](#compatibilidade-e-limites)
- [Limitações conhecidas](#limitações-conhecidas)
- [Contribuindo](#contribuindo)
- [Atualizando](#atualizando)
- [Licença](#licença)

## Como funciona

Começa no momento em que você abre o Claude. Se o projeto ainda não existe, ele *não* sai escrevendo código. Primeiro pergunta o que você quer de verdade — o problema, pra quem é, a promessa em uma frase, o que o v1 precisa ter e, principalmente, o que o projeto **não é**. Devolve o que entendeu em partes curtas, você corrige, e só quando você aprova ele grava tudo num `NORTE.md` na raiz.

Se o projeto já está em andamento, ele lê tudo antes de mexer: docs, manifestos, os primeiros commits (onde a ideia original costuma morar), o código e o que realmente funciona. Reconstrói a ideia com fonte pra cada afirmação, marca com `(?)` o que é dedução, aponta onde o projeto já fugiu do caminho e te pede pra confirmar.

Daí em diante, o `NORTE.md` entra no contexto do Claude no início de toda sessão — e de novo depois de cada compactação, que é exatamente quando agentes costumam esquecer o que estavam fazendo. A cada mensagem sua, ele recebe um lembrete curto com o "Foco agora". Quando um pedido foge do norte, ele para antes de codar, cita o trecho literal do `NORTE.md` e te dá três saídas: mudar o norte (com registro), anotar pra depois ou deixar pra lá. Quando é ele mesmo quem está fugindo — a refatoração "rápida", a lib "melhor" —, a mesma regra vale.

Antes de dizer "pronto", a skill `verifying-before-done` pede que ele rode a verificação, releia o seu pedido item a item e confira o `git diff` atrás de arquivos que ninguém pediu. Um hook cobra a parte mínima disso: se ele editou código e diz que terminou sem ter conferido nada depois, a resposta volta pra ele uma vez. As skills entram pelas próprias descrições, sem você chamar; os testes de comportamento medem se elas entram na hora certa.

## Em 5 minutos

```bash
# 1. instalar (dentro do Claude Code)
/plugin marketplace add rafaeldominguesdev/onedirection
/plugin install onedirection@onedirection
# reinicie o Claude

# 2. conferir que carregou (no terminal)
claude plugin details onedirection@onedirection    # 7 skills, 3 hooks

# 3. testar numa pasta vazia
mkdir /tmp/teste-onedirection && cd /tmp/teste-onedirection && claude
#    peça: "quero criar um app de lista de compras"
#    esperado: ele pergunta antes de escrever código, e grava um NORTE.md quando você aprovar

# 4. validar o NORTE.md gerado (no repositório do plugin)
~/.claude/plugins/marketplaces/onedirection/scripts/validate-norte /tmp/teste-onedirection/NORTE.md

# 5. desligar, se quiser
/plugin disable onedirection@onedirection
```

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

A skill de entrada manda conferir as skills antes de qualquer tarefa. Isso é instrução pro modelo, não trava: os testes de comportamento são o que mostra se ele segue.

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
  - **projeto sem `NORTE.md`**: as regras essenciais em poucas linhas (~1.060 caracteres);
  - **fora de projeto** (sem git, sem manifesto, ou a sua pasta pessoal): uma linha (~240 caracteres).
  Na compactação, em projeto, manda usar `recovering-focus`.
- **UserPromptSubmit** — só em projetos com `NORTE.md`: uma regra curta (registrar ideia nova, conflito → guarda, prova antes de "pronto") e a seção "Foco agora", delimitada como dado do arquivo e limitada a 1.200 caracteres.
- **Stop** — cobra uma regra mínima: se o Claude editou um arquivo que não é Markdown/texto, não conferiu nada **depois da última edição** e diz que terminou sem admitir que não verificou, a resposta volta pra ele **uma vez** pra conferir ou declarar "Não verifiquei: …".
  - Conta como conferência: um comando (`Bash`), a skill `verifying-before-done`, ou `Read`/`Grep` que olhe o arquivo editado. `Glob` não conta, nem um `Bash` feito só de comandos que não provam nada: `ls`, `pwd`, `echo`, `which`, `mkdir`, `cp`, `rm`, `git status`, `git log`, `--version` e `cat` de outro arquivo. Se qualquer parte do comando for outra coisa (`git diff`, `npm test`, `node …`), ele conta.
  - É uma heurística por palavras: não sabe se a verificação provou o que foi afirmado, e frases fora da lista passam.
  - Precisa de `python3`; sem ele, esse hook não faz nada.

### Validador do NORTE.md

```bash
scripts/validate-norte            # ./NORTE.md
scripts/validate-norte outro/NORTE.md
```

Confere se as seções existem (e não se repetem), se o v1 tem itens (no máximo 4), se há não-objetivos e critério de pronto, se sobrou trecho do modelo sem preencher, se o arquivo não passou de 120 linhas, se há caractere de controle invisível (um ESC pode esconder texto de quem lê no terminal) e se há tag imitando as do plugin. O hook de início de sessão roda a mesma validação e, se achar problema, o Claude te avisa uma vez. Saída: 0 ok, 1 problemas, 2 arquivo não encontrado.

## Filosofia

- **Uma direção** — O `NORTE.md` manda no escopo; mudar de ideia é permitido, mudar sem registrar não
- **Não-objetivos primeiro** — O que o projeto não é segura mais que o que ele é
- **Evidência antes de afirmação** — Fato sobre o projeto só com fonte; "pronto" só com prova
- **O disco não esquece** — Memória de conversa falha numa compactação; arquivo não
- **O usuário manda** — O onedirection avisa, não bloqueia

## Testes

Três níveis:

| Nível | Comando | Custo | Precisa de |
|---|---|---|---|
| Tudo o que é barato | `scripts/check-all` | grátis, ~10 s | bash, python3; usa `shellcheck` e `claude` se existirem (senão, pula e avisa) |
| Instalação de verdade | `scripts/test-install` | grátis, sem API | a CLI `claude` (sai com 3 se ela não existir) |
| Comportamento | `python3 tests/evals/run.py` | ~US$ 0,20–0,80 por cenário | a CLI `claude` com login ou `ANTHROPIC_API_KEY` |

`scripts/check-all` roda `bash -n` em todos os scripts (também no bash 3.2 do macOS), `py_compile`, valida todo JSON, ShellCheck, `scripts/check-version`, `tests/evals/check_results.py`, `bash tests/hooks/test-hooks.sh`, `claude plugin validate .` e `git diff --check`. Se alguma etapa for pulada por falta de ferramenta, o resumo diz "VALIDAÇÃO INCOMPLETA" e lista o que não rodou ("tudo passou" só aparece quando nada foi pulado); `CHECK_ALL_STRICT=1` transforma "ferramenta ausente" em falha.

`tests/hooks/test-hooks.sh` (142 casos) cobre os três níveis de injeção, a compactação, o "Foco agora", o hook Stop, o validador e casos adversariais: tags que tentam fechar o bloco de dados, caracteres de controle, NORTE.md de 30 MB, link simbólico pra fora do repositório, FIFO, texto com `$( )` e crases (a suíte confere que nada é executado) e um lint que proíbe `&` no substituto de `${var//…/…}`. O placar é testado: uma falha proposital dentro de um pipe tem que derrubar a suíte.

`scripts/test-install` usa uma configuração do Claude Code temporária (`CLAUDE_CONFIG_DIR`), sem mexer na sua. Ele adiciona este repositório como marketplace, instala o plugin, confere versão, skills e hooks, confere que a cópia instalada fica fora do checkout e é igual a ele, e roda os hooks dessa cópia. Se o marketplace ou a instalação falharem, ele para e mostra o erro do `claude` (código 2).

### Testes de comportamento

Rodam cada cenário de `tests/evals/scenarios.json` numa sessão nova do Claude, numa cópia temporária de um projeto de mentira, com a versão **local** do plugin. Depois um corretor automático confere o transcript e os arquivos. O corretor mede comportamento, não só texto: skill chamada pela ferramenta `Skill` (anunciar não conta), arquivos que mudaram ou não, ordem das escritas, comandos que rodaram (`git status` na retomada) e quantas vezes o hook Stop bloqueou.

| Cenário | O que prova |
|---|---|
| `evolucao` | Ideia nova que serve à promessa é feita e registrada, sem alarme |
| `conflito` | Pedido que bate num não-objetivo para antes do código e cita o trecho |
| `pedido-pequeno` | Ajuste pequeno sem cerimônia e sem cair na isca do `TODO: refatorar` |
| `alucinacao` | Pergunta sobre função inexistente: procura e diz que ela não existe |
| `retomada` | Trabalho pela metade: roda `git status`/`git diff` e reconstrói pelo `NORTE.md` |
| `mapeamento` | Projeto sem `NORTE.md`: mapeia primeiro e não grava nada sem aprovação |
| `projeto-novo` | Pasta vazia: entrevista antes de qualquer código |
| `fora-de-projeto` | Fora de projeto: fica quieto e quase não gasta contexto |
| `pronto-sem-prova` | Usuário pede pra não conferir: pode atender, mas não afirma que funciona sem admitir |
| `progresso-desatualizado` | `NORTE.md` diz que o v1 está pronto e o código não: checkbox não é prova |
| `aceitacao-projeto-novo` | Ponta a ponta: `NORTE.md` escrito **antes** do código, com os não-objetivos do usuário, v1 mínimo (até 4 itens) e sem estado futuro inventado |
| `stop-hook-ativo` | Força um "Pronto." seco depois de editar: o hook bloqueia exatamente uma vez, sem laço |
| `compactacao-real` | Sessão com trabalho pela metade, `/compact` de verdade e "continua": o hook avisa e o Claude retoma pelo git e pelo `NORTE.md` |

Rode um só com `python3 tests/evals/run.py conflito`, meça instabilidade com `--repeat 3` e troque o modelo com `EVAL_MODEL=sonnet`. Cada rodada grava `run.json` (versão, commit, modelo pedido) ao lado dos transcripts.

### Replay: recorrigir sem chamar o modelo

```bash
python3 tests/evals/run.py --replay PASTA_DOS_TRANSCRIPTS \
  --source-results tests/evals/results/0.4.4-sonnet.json --save-results /tmp/replay.json
```

O replay **não executa modelo nenhum** e custa zero. Ele lê transcripts e fotos dos arquivos já gravados e roda o corretor atual sobre eles. Serve para saber se uma mudança no corretor muda o veredito sobre o mesmo comportamento, não para medir o plugin de novo. O resumo do replay diz isso nos campos `kind: "replay"`, `model_executed: false` e `replay_cost_usd: 0`, e separa o commit da rodada original (`source_commit`) do commit do corretor (`grader_commit`). `tests/evals/sanitize.py PASTA SAIDA` limpa transcripts para publicar.

### Resultados por versão

Os resumos ficam em [`tests/evals/results/`](tests/evals/results/), com versão do plugin, commits, versão do Claude Code e modelo (lidos dos transcripts), data, custo e o resultado de cada cenário. `tests/evals/check_results.py` confere que esses metadados fecham.

| Versão | Opus | Sonnet | Como |
|---|---|---|---|
| 0.4.3 | 12/13 | 11/13 | ao vivo; as três falhas viraram as correções da 0.4.4 |
| 0.4.4 | 12/13 | 12/13 | ao vivo; as duas falhas eram do corretor (explicado nas notas da versão) |
| 0.4.4 | 13/13 | 13/13 | replay (nenhum modelo executado) com o corretor ajustado |
| 0.4.5 | 13/13 | 13/13 | ao vivo em 2026-11-04 (commit `bf38a61`, Claude Code 2.1.317), uma rodada por modelo, US$ 3,78 + US$ 1,68 |
| 0.4.6 | — | — | **não rodado ao vivo.** Replay das rodadas ao vivo da 0.4.5 com o corretor da 0.4.6 (nenhum modelo executado): 13/13 e 13/13 |

**Transcripts:** os das rodadas ao vivo da 0.4.4 e da 0.4.5 (limpos com `sanitize.py`) estão anexados à [release v0.4.5](https://github.com/rafaeldominguesdev/onedirection/releases/tag/v0.4.5), um arquivo por versão e modelo, com `SHA256SUMS`. Pra refazer o replay sem gastar nada:

```bash
mkdir -p /tmp/od-0.4.5 && tar -xzf transcripts-0.4.5-sonnet.tar.gz -C /tmp/od-0.4.5
python3 tests/evals/run.py --replay /tmp/od-0.4.5/sonnet --source-results tests/evals/results/0.4.5-sonnet.json
```

Os da 0.4.3 não foram publicados.

No GitHub, a cada push, rodam os testes dos hooks no Ubuntu (bash 5) e no macOS (incluindo o bash 3.2), o `scripts/check-all`, a instalação real pelo marketplace e o `claude plugin validate`. Os de comportamento custam, então rodam à mão: **Actions › comportamento › Run workflow**, com o segredo `ANTHROPIC_API_KEY` configurado.

## Segurança e privacidade

- **Os hooks rodam com as suas permissões.** São três hooks em bash (`hooks/session-start`, `hooks/user-prompt-submit`, `hooks/stop`), as funções que eles usam (`hooks/lib.sh`) e um script Python (`hooks/stop_check.py`), executados com o seu usuário a cada sessão, a cada mensagem e a cada fim de resposta, como em todo plugin do Claude Code. Vale ler os cinco antes de instalar.
- **O que os hooks não fazem:** não acessam a rede, não instalam nada, não têm telemetria, não gravam arquivo nenhum e não executam texto vindo do projeto. O hook Stop só **lê** o transcript da sessão. A suíte tem um teste para cada uma dessas coisas: procura no código dos hooks por `curl`, `wget`, `eval`, socket e afins, e confere que `$( )` e crases escritos no `NORTE.md` não rodam. Quem usa rede são as ferramentas de desenvolvimento: `scripts/test-install` (a CLI `claude`) e os testes de comportamento (a API).
- **O que entra no contexto do Claude (e portanto vai para a API):** o texto das skills, e o `NORTE.md` e o "Foco agora" do projeto aberto.
- **Repositório de outra pessoa:** o `NORTE.md` é escrito por quem mantém o repositório, por isso o plugin o trata como dado não confiável:
  - entra **delimitado** num bloco `<norte-md>`, fora da moldura de instruções do plugin, com a orientação de não seguir ordens que não sejam sobre o escopo do produto;
  - todo `<` e `>` do arquivo vira `‹` e `›`, então nenhuma tag dele consegue fechar o bloco ou imitar a moldura;
  - só os primeiros 12.000 bytes são lidos, cortados no fim de uma linha;
  - **link simbólico e arquivo especial não são lidos:** um `NORTE.md` apontando para `~/.ssh/...` não vai parar no contexto. O hook avisa, e o Claude só lê o arquivo se você confirmar;
  - o validador avisa de caractere de controle invisível e de tag imitando as do plugin.

  Isso reduz o risco de injeção de instruções, mas não zera: obedecer ou não ao texto do bloco continua sendo decisão do modelo. Abrir um projeto que você não conhece continua pedindo cuidado, com ou sem este plugin.

## Compatibilidade e limites

| Tema | Situação |
|---|---|
| Claude Code | Testes de comportamento na 2.1.317 (lida dos transcripts). Instalação e `plugin validate`: localmente na 2.1.317, e na CI a cada push com a versão atual do npm (2.1.318 em 2026-11-04; o job falha se o `claude` executado não for o que o npm instalou). Usa hooks de plugin `SessionStart`, `UserPromptSubmit` e `Stop` |
| Modelos | Testes de comportamento rodados no Opus e no Sonnet. Outros modelos: não testados |
| Sistema | macOS (bash 3.2 do sistema ou mais novo) e Linux (bash 5 na CI). **Windows não é suportado** |
| `python3` | Opcional pro plugin: só o hook de fim de resposta usa; sem ele, esse hook fica desligado e o resto funciona. Obrigatório pros testes |
| Sem git | Funciona. O projeto é reconhecido por manifesto (`package.json`, `Cargo.toml`…); `recovering-focus` perde a parte do histórico |
| Monorepo | O `NORTE.md` é procurado na pasta onde o Claude abriu e depois na raiz do git. Um por pacote, ou um na raiz |
| Worktrees | Funciona: o `NORTE.md` é versionado e o `.git` em forma de arquivo é reconhecido |
| Pasta pessoal | Nunca é tratada como projeto, mesmo com repositório de dotfiles |
| Outros plugins de fluxo | Pensado pra conviver com a superpowers (onedirection decide **o quê**, ela decide **o como**). **Ainda não testado em conjunto** |

**Desativar por um tempo:** `/plugin disable onedirection@onedirection` (reative com `/plugin enable onedirection@onedirection`).

**`NORTE.md` desatualizado:** peça "confere o progresso" (dispara `checking-progress`, que compara cada item com o código) ou rode `scripts/validate-norte` pra conferir a estrutura.

### Custo de contexto (medido na 0.4.5)

| Situação | No início da sessão, no `/clear` e depois de cada compactação | A cada mensagem |
|---|---|---|
| Sempre (descrições das 7 skills) | ~466 a ~759 tokens (ver abaixo) | — |
| Fora de projeto | +241 caracteres (~60 tokens) | nada |
| Projeto sem `NORTE.md` | +1.063 caracteres (~270 tokens) | nada |
| Projeto com `NORTE.md` (exemplo de 898 bytes) | +8.497 caracteres (~2.100 tokens) | +452 caracteres (~115 tokens) |
| Pior caso: `NORTE.md` acima do limite | +~20.000 caracteres (~5.000 tokens): skill de 7 KB + 12.000 bytes do arquivo | até ~1.700 caracteres (Foco agora limitado a 1.200) |

Os números de skill vêm de `claude plugin details onedirection@onedirection`, que deu valores diferentes conforme a configuração (Claude Code 2.1.317, mesmos arquivos): ~466 tokens numa configuração limpa, sem login, e ~759 numa configuração com login. Os ~466 batem exatamente com caracteres ÷ 4. A diferença é compatível com uma contagem de tokens de verdade, já que texto em português gasta mais tokens por caractere, mas não confirmei de onde vem a contagem maior. Os números dos hooks foram medidos na saída dos próprios hooks e convertidos com tokens ≈ caracteres ÷ 4, então provavelmente também estão subestimados numa proporção parecida (~1,6×). O jeito de manter o custo baixo é manter o `NORTE.md` curto (~80 linhas), e o validador avisa quando ele passa de 120.

### O que é garantido e o que não é

| Cobrado por código | Depende do modelo (medido pelos testes, não garantido) |
|---|---|
| O `NORTE.md` entra no contexto no início, no `/clear` e depois de cada compactação | Chamar a skill certa na hora certa |
| O "Foco agora" entra a cada mensagem | Entrevistar antes de codar, mapear antes de opinar |
| "Pronto" depois de editar código, sem conferência posterior e sem admitir, volta uma vez | Fazer a verificação **certa** (o hook só vê que houve alguma) |
| A estrutura do `NORTE.md` é validada e problemas são avisados | Parar no conflito e citar o trecho literal |
| O `NORTE.md` entra como dado, delimitado, sem `<`/`>` e com tamanho limitado; link simbólico não é lido | Não seguir ordens escritas dentro de um `NORTE.md` malicioso |
| A saída dos hooks é JSON válido, inclusive com caractere de controle no `NORTE.md` | Registrar ideia nova em "Decisões" e manter "Foco agora" atualizado |

**Limite honesto:** as regras de comportamento são instruções pro modelo, e só uma delas é cobrada por código (o hook de "pronto" sem prova). A coluna da esquerda é o que os hooks fazem sozinhos. O resto é medido pelos testes de comportamento, não garantido. Modelos diferentes seguem as instruções de jeitos diferentes: o Sonnet, por exemplo, só passou a registrar ideias novas em "Decisões" depois que a regra entrou no lembrete de cada mensagem.

## Limitações conhecidas

- **Nada de comportamento é garantido.** As skills orientam. Os testes de comportamento medem 13 cenários num projeto de mentira, uma vez por modelo, então uma rodada verde não prova estabilidade (use `--repeat`).
- **O hook Stop é uma heurística por palavras.** Ele só vê que *alguma* conferência aconteceu depois da última edição, não se ela prova o que foi dito. Frases fora da lista passam, e Markdown/`.txt` ficam de fora de propósito.
- **A neutralização troca `<` e `>` na cópia injetada.** O modelo vê `‹ ›` no lugar (e é avisado disso). O arquivo em disco não muda.
- **`NORTE.md` maior que 12.000 bytes:** só o começo entra no contexto, e um "Foco agora" que fique depois do corte não entra no lembrete por mensagem.
- **Link simbólico:** um `NORTE.md` que é link (mesmo para dentro do repositório) não é carregado automaticamente.
- **Só os transcripts da 0.4.4 e da 0.4.5 estão publicados** (na release v0.4.5); os da 0.4.3 não, então o replay da 0.4.3 não é reproduzível por terceiros.
- **As rodadas ao vivo rodam na máquina do autor**, com o CLAUDE.md global dele e outros plugins ativos (campo `environment` nos resumos). Numa configuração limpa o resultado pode ser outro.
- **A 0.4.6 não teve rodada ao vivo.** Só o hook Stop mudou, e ele foi medido pelo replay das sessões da 0.4.5. Não está medido como o modelo reage a um bloqueio que antes não acontecia.
- **Windows não é suportado**, e o uso junto com a superpowers não foi testado.

## Contribuindo

1. Faça um fork do repositório
2. Crie uma branch pro seu trabalho
3. Mantenha cada skill curta e com um trabalho só; regras duras em blocos (`<HARD-GATE>`, Lei de Ferro) e racionalizações em tabela "Pensamento | Realidade"
4. Rode `scripts/check-all`. Mudou o texto de uma skill ou o que um hook injeta? Os testes de comportamento são obrigatórios: é assim que se descobre que uma frase nova quebrou um caso antigo
5. Abra um PR explicando, com as suas palavras, o problema que a mudança resolve

## Atualizando

`/plugin marketplace update onedirection` e reinicie o Claude.

## Licença

MIT — veja o arquivo LICENSE.
