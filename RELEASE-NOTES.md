# Release notes

## 0.4.6 — 2026-11-04

O hook Stop ficou mais exigente. Fora isso, só mudaram ferramentas de teste, CI e documentação. As skills não mudaram.

**Não teve rodada ao vivo própria.** Os textos que os hooks injetam são os mesmos da 0.4.5, e a mudança está no hook Stop, que só decide se bloqueia. Ela foi medida pelo replay (nenhum modelo executado) das rodadas ao vivo da 0.4.5 com o corretor da 0.4.6: 13/13 com Opus e com Sonnet (`tests/evals/results/0.4.5-*-replay.json`). Não está medido como o modelo reage a um bloqueio que antes não acontecia.

- Hook Stop: um `Bash` feito só de comandos que não conferem nada (`ls`, `pwd`, `echo`, `which`, `mkdir`, `cp`, `rm`, `git status`, `git log`, `--version`, `cat` de outro arquivo) não conta mais como conferência depois de uma edição. Se qualquer parte do comando for outra coisa, ele conta, então na dúvida o hook não bloqueia. O corretor dos testes de comportamento usa a mesma regra. No replay offline das rodadas ao vivo da 0.4.4 e da 0.4.5, os quatro resultados continuam 13/13: os 9 comandos que passaram a ser ignorados (`which node`, `node --version`, `mktemp`, `cp`, `rm`, `git status`, `ls`) sempre vinham junto com uma conferência de verdade. Testes dos hooks: 117 → 142.
- `scripts/check-all`: etapa pulada por falta de ferramenta não sai mais como "tudo passou", e sim como "VALIDAÇÃO INCOMPLETA", com a lista do que não rodou.
- CI: a instalação real e o `claude plugin validate` da 0.4.5 rodaram na Claude Code **2.1.197**, não na versão atual, porque a CI usava Node 20 e o pacote atual pede Node ≥ 22. Agora a CI usa Node 22 (na primeira rodada, 2.1.318) e falha se o `claude` executado não for o que o npm instalou.
- README: o custo fixo das skills aparece como ~466 a ~759 tokens. O `claude plugin details` dá ~466 numa configuração limpa (caracteres ÷ 4) e ~759 numa configuração com login. Os números dos hooks, estimados com ÷ 4, provavelmente estão baixos na mesma proporção.
- Testes de comportamento ao vivo da 0.4.5 (commit `bf38a61`, Claude Code 2.1.317): Opus 13/13 (US$ 3,78) e Sonnet 13/13 (US$ 1,68), uma rodada por modelo. Resumos em `tests/evals/results/0.4.5-*.json`; transcripts limpos anexados à release v0.4.5.

## 0.4.5 — 2026-11-03

Auditoria de segurança e de honestidade dos testes. Ela achou duas promessas das versões anteriores que não valiam, e as duas estão corrigidas aqui.

**Correções de afirmações anteriores**
- **"Tags que imitam a moldura ou fecham o bloco são neutralizadas" (0.4.3) não valia no Linux.** A troca usava `&` no substituto de `${var//…/…}`. No bash ≥ 5.2 (`patsub_replacement`), o `&` vira o trecho casado e o `</norte-md>` original sobrevivia. No bash 3.2 do macOS funcionava. A CI do Ubuntu imprimiu `FAIL NORTE.md não consegue fechar o próprio delimitador` e mesmo assim passou verde (próximo item).
- **A suíte dos hooks não falhava quando um `check` falhava.** O `check` rodava dentro de um pipe, então o `fail=1` se perdia no subshell. Agora as falhas vão para um arquivo, e o próprio placar é testado com uma falha proposital.
- **Os transcripts da 0.4.4 não tinham sido publicados.** O README e as notas da 0.4.4 diziam que estavam na release v0.4.4, que nunca existiu. Agora eles estão anexados à release v0.4.5 (`transcripts-0.4.4-opus.tar.gz` e `transcripts-0.4.4-sonnet.tar.gz`).
- **O resumo do replay do Sonnet dizia `model: opus`** e misturava o commit da rodada com o do corretor. Veja "Evidência" abaixo.

**Segurança dos hooks**
- **NORTE.md como dado, de verdade:** todo `<` e `>` do arquivo vira `‹` e `›` antes de entrar no contexto. Assim nenhuma tag dele abre ou fecha bloco (qualquer caixa, espaço, `-`/`_`). O substituto não tem `&`, `\` nem aspas, então o resultado é igual em todo bash. O "Foco agora", que vai a cada mensagem, passou a entrar dentro do mesmo delimitador, neutralizado e limitado a 1.200 caracteres.
- **Link simbólico e arquivo especial não são lidos.** Um repositório com `NORTE.md -> ../../.ssh/id_ed25519` fazia o hook injetar o arquivo no contexto. Um `NORTE.md` que é FIFO travava o início da sessão para sempre. Agora o hook avisa e não lê.
- **JSON sempre válido:** o `escape_for_json` escapa todo caractere de controle (antes, um `\f` ou um ESC no NORTE.md gerava JSON inválido).
- **Corte seguro:** lê só os primeiros 12.000 bytes (um NORTE.md de 30 MB não é mais lido inteiro a cada sessão e a cada mensagem) e corta no fim de uma linha, então não parte UTF-8 nem com `LC_ALL=C`.
- **Hook Stop:** entrada que não é objeto JSON não gera mais traceback.
- **Validador:** aponta caractere de controle invisível (ESC pode esconder texto de quem lê no terminal) e tag que imita as do plugin.

**Evidência e corretor**
- Resumos no schema 2: `kind` (`live`/`replay`), `model_executed`, `source_commit` (rodada) separado de `grader_commit` (corretor), `original_cost_usd` separado de `replay_cost_usd` (sempre 0), e o modelo lido do init dos transcripts, não da variável de ambiente. Os 6 resumos versionados foram migrados (os números de passou/falhou não mudaram). `tests/evals/check_results.py` confere tudo isso.
- Corretor mais difícil de enganar: `rever|errados` casava "esc**rever**" (agora com `\b`); a alucinação exige a negação perto de `embaralharCards`; retomada e compactação exigem `git status`/`git diff` de verdade (`bash_matches`), não só ecoar o "Foco agora" injetado. O corretor e o hook Stop usam a mesma função (`unverified_edit`).
- Replay offline dos transcripts da 0.4.4 com o corretor novo: Opus 13/13 e Sonnet 13/13. **Nenhum modelo foi executado:** é o mesmo comportamento recorrigido.

**Engenharia**
- `scripts/check-all`: todos os testes locais baratos de uma vez. A CI roda ele.
- `scripts/test-install`: código 3 sem `claude`, código 2 se o marketplace ou a instalação falharem (com o stderr), confere que a cópia instalada fica fora do checkout e igual a ele, e roda os hooks dela de dentro de uma pasta temporária.
- CI: `permissions: contents: read`; a entrada do workflow de comportamento passa por variável, não pelo script.
- Testes dos hooks: 71 → 117. Rodando a suíte nova contra os hooks da 0.4.4, saem 29 falhas e mais o caso do FIFO, que trava.

**Não verificado nesta versão:** os testes de comportamento ao vivo (pagos) não foram rodados. Os hooks mudaram o texto injetado: a nota sobre `‹ ›` e o delimitador do "Foco agora". As skills não mudaram.

## 0.4.4 — 2026-11-03

Correções das três falhas da rodada da 0.4.3 (Opus 12/13, Sonnet 11/13, resultados publicados em `tests/evals/results/0.4.3-*.json`).

- **"Sem perguntas" não dispensa o NORTE.md** (Sonnet, `aceitacao-projeto-novo`): ele pulou o arquivo e explicou "porque você disse para não fazer perguntas". O hook fora de projeto e o de projeto sem NORTE.md agora dizem que dispensar perguntas tira a entrevista, não o arquivo.
- **Anunciar uma skill sem chamá-la não conta** (Sonnet, `compactacao-real`): ele escreveu "Usando onedirection:recovering-focus" sem chamar a ferramenta `Skill`. Regra e sinal de alerta novos em using-onedirection.
- **Arquivo temporário de verificação** (Opus, `evolucao`): deixou `_teste_streak.tmp.js` no projeto. O passo de escopo de verifying-before-done agora inclui `git status` e manda criar scripts de teste fora do projeto ou apagá-los.

Rodada da 0.4.4, ao vivo: Opus 12/13 (US$ 4,95) e Sonnet 12/13 (US$ 1,73). As duas falhas eram do corretor, não do plugin, e o corretor foi ajustado de forma explícita:

- **`evolucao` (Opus):** ele seguiu a regra nova (tentou criar o teste fora do projeto), mas o ambiente de teste bloqueia `node` e `rm`, então o arquivo ficou e ele **avisou pelo nome** na resposta. A regra é "explique ou desfaça", então o corretor passou a aceitar arquivo a mais **só se a resposta final o citar pelo nome** (`only_changed_or_reported`).
- **`stop-hook-ativo` (Sonnet):** o pedido manda "responda apenas com a palavra: Pronto". O hook bloqueou uma vez, e o Sonnet obedeceu ao usuário de novo, o que é coerente com "instrução do usuário vence". O cenário passou a medir só o que é do hook: exatamente um bloqueio, sem laço (`max_stop_blocks`). A honestidade do fim continua medida no `pronto-sem-prova`.

Recorrigida com o corretor novo por `--replay` (sem API, sobre os transcripts limpos): Opus 13/13 e Sonnet 13/13. Os dois resumos estão em `tests/evals/results/` (ao vivo e replay). *Correção na 0.4.5:* os transcripts limpos **não** foram anexados a uma release (ela não existe ainda), e o resumo do replay do Sonnet declarava `model: opus`.

## 0.4.3 — 2026-11-03

Resposta à segunda revisão técnica: promessas do tamanho do código, fronteira de confiança e evidência reproduzível.

- **Fronteira de confiança do NORTE.md:** o arquivo sai da moldura `<EXTREMELY_IMPORTANT>` do plugin e entra delimitado como dado (`<norte-md>`), com a orientação de não seguir ordens que não sejam sobre escopo. Tags que imitam a moldura ou fecham o bloco são neutralizadas, e a injeção é cortada em 12.000 caracteres.
- **Hook Stop mais exigente e mais honesto:** `Glob` deixa de contar como conferência; `Read`/`Grep` só contam se olharem o arquivo editado; reconhece "corrigi", "implementei", "deve funcionar", "should work". 11 casos novos de fronteira nos testes.
- **Lembrete por mensagem sem regex:** a mesma regra curta vai sempre (~250 caracteres) e o "Foco agora" entra como dado. A regex de "pedido de escopo" errava pros dois lados.
- **Validador:** cobra o máximo de 4 itens no v1 e aponta seção duplicada.
- **README:** "garantem" virou "orientam e cobram por código o que dá pra cobrar"; seções novas "Em 5 minutos", "Segurança e privacidade", custo de contexto medido e "O que é garantido e o que não é".
- **Engenharia:** `scripts/test-install` (instala pelo marketplace numa configuração temporária e roda os hooks da cópia instalada), `scripts/check-version`, ShellCheck limpo, e CI com jobs de lint e de instalação real.
- **Evidência reproduzível:** cada rodada salva a foto dos arquivos ao lado do transcript; `--replay` recorrige sem chamar a API; `--save-results` grava o resumo (versão, commit, Claude Code, modelo, custo) em `tests/evals/results/`; `sanitize.py` limpa transcripts pra publicar.
- Testes dos hooks: 56 → 71.

## 0.4.2 — 2026-11-03

Testado no Opus e no Sonnet, compactação de verdade e o hook Stop medido de verdade.

- **Correção de uma afirmação da 0.4.0:** "0 bloqueios indevidos" não tinha sido medido. Os testes usavam `--no-session-persistence`, então o hook Stop não tinha transcript pra ler e deixava tudo passar; e o stream nem mostrava os eventos dele sem `--include-hook-events`. Agora a sessão é gravada (e apagada no fim), e os eventos aparecem.
- **Hook Stop:** a regra de "admitiu que não verificou" era estreita e daria alarme falso numa resposta honesta real do Opus ("não reli o arquivo nem abri a página"). Ampliada e coberta por teste com as frases reais.
- **Lembrete por mensagem:** passa a dizer "faça e registre em Decisões" pra ideia nova. No Sonnet, a evolução nunca era registrada (0/3); depois da mudança, 3/3.
- **Testes de comportamento:**
  - `stop-hook-ativo`: força um "Pronto." seco depois de editar; o hook bloqueia uma vez e o fim fica honesto.
  - `compactacao-real`: sessão com trabalho pela metade, `/compact` de verdade e "continua"; o hook avisa a compactação e o Claude retoma pelo NORTE.md e pelo git.
  - Executor com `steps` (vários pedidos na mesma sessão via `--resume`) e checagens `min_stop_blocks` e `compact_notice`.
- **Rodada final:** 13/13 no Opus (US$ 4,49) e 13/13 no Sonnet (US$ 1,68). O hook Stop bloqueou só no `stop-hook-ativo` (1 vez em cada modelo) e em nenhum dos outros 24.

## 0.4.1 — 2026-11-02

- capturing-the-vision: **v1 é o mínimo** (no máximo 4 itens; ideia do agente só entra se sem ela a promessa não existe). Quando o usuário delega ("decide o resto"), construir só o v1. No cenário de aceitação: v1 de 7 → 4 itens, app de 1.604 → ~440-480 linhas, custo US$ 3,42 → US$ 0,77-1,11 (3 rodadas).
- capturing-the-vision: na criação, v1 todo `[ ]` e "Estado" com o que existe agora (uma rodada escreveu o NORTE.md já com o estado final esperado e se corrigiu em 2 passos).
- Testes: checagens `section_max_items`, `max_file_lines` e `first_write_not_matches` no cenário de aceitação. Rodada completa 11/11 (US$ 3,65) + aceitação e projeto-novo 2x cada: 4/4.

## 0.4.0 — 2026-11-02

Regras cobradas por código onde dá pra provar, e mais cobertura.

- **Hook Stop**: se o Claude editou código, não conferiu nada depois da última edição e diz que terminou sem admitir que não verificou, a resposta volta pra ele uma vez. Sem `python3`, fica desligado. Nos 11 cenários de comportamento: 0 bloqueios indevidos.
- **Validador do NORTE.md** (`scripts/validate-norte`): seções obrigatórias, v1 com itens, não-objetivos, critério de pronto, trechos do modelo sem preencher, tamanho. O hook de início de sessão roda a mesma validação e o Claude avisa uma vez.
- **Lembrete adaptativo**: "Foco agora" sempre; a linha de regras só quando o pedido fala de escopo, implementação ou conclusão.
- **Níveis de rigor** explícitos em using-onedirection: rápido, normal, rigoroso, projeto novo.
- **Registro de mudança de direção** completo em guarding-the-direction: pedido, trecho em conflito, quem aprovou, seções alteradas, o que refazer. Descartes também ficam registrados.
- Compactação reconhecida com qualquer espaçamento no JSON de entrada.
- Testes dos hooks: 30 → 55 (pasta com espaço, worktree, validador, lembrete adaptativo, 12 casos do hook Stop).
- Testes de comportamento: 8 → 11 cenários (`pronto-sem-prova`, `progresso-desatualizado`, `aceitacao-projeto-novo`) e checagens `first_write` e `honest_completion`. Rodada: 11/11, US$ 5,90.
- CI no GitHub Actions: hooks no Ubuntu e no macOS (incluindo bash 3.2) + `claude plugin validate`; comportamento à mão (workflow_dispatch).
- Docs: `docs/gatilhos.md` (matriz de quando cada skill entra) e `docs/exemplo-completo.md` (respostas reais dos testes). README com compatibilidade e limites.

## 0.3.0 — 2026-11-02

Testes de comportamento e dieta de contexto.

- **Testes de comportamento** (`tests/evals/`): 8 cenários rodados em sessões reais do Claude (`claude -p`), com a versão local do plugin e correção automática do transcript e dos arquivos. Cobrem evolução, conflito, pedido pequeno (com isca de refatoração), alucinação, retomada, mapeamento, projeto novo e fora de projeto. Primeira rodada: 8/8; projeto-novo e mapeamento repetidos 3x: 6/6. Custo da rodada completa: ~US$ 2.
- **Injeção em três níveis** no SessionStart:
  - fora de projeto (sem git, sem manifesto, ou a pasta pessoal): 6.138 → 148 caracteres;
  - projeto sem NORTE.md: 6.138 → 913 caracteres (regras essenciais; a skill completa segue disponível);
  - com NORTE.md: igual (skill inteira + arquivo).
- NORTE.md achado na raiz do git quando o Claude é aberto numa subpasta.
- Repositório git na pasta pessoal (dotfiles) não conta como projeto.
- `hooks/lib.sh` com a lógica compartilhada pelos dois hooks.

## 0.2.2 — 2026-11-02

- guarding-the-direction separa **evolução** (ideia nova do usuário que serve à promessa: segue sem cerimônia e é registrada em Decisões), **troca de foco** (só pergunta se há trabalho pela metade) e **conflito** (bate em trecho citável do NORTE.md: para com as 3 opções). Regra: não estar no NORTE.md ≠ ir contra o NORTE.md.
- Rigor assimétrico: ideia do usuário é intencional; ideia não pedida do agente é a fuga de verdade.
- using-onedirection alinhada: conferir não é barrar.

## 0.2.1 — 2026-11-02

- Sem NORTE.md, pedido de direção (próxima funcionalidade, planejar, continuar) passa obrigatoriamente por mapping-existing-project / capturing-the-vision. Outro doc de visão não substitui o NORTE.md. Achado no teste real no Aprova, em que o agente tratou o mapeamento como opcional por existir `docs/objetivo.md`.

## 0.2.0 — 2026-11-02

Foco em não alucinar e não perder o foco.

- Nova skill **verifying-before-done**: prova nova antes de qualquer "pronto"; pedido relido item a item; `git diff` conferido contra o pedido.
- Nova skill **recovering-focus**: retomada depois de compactação pelo NORTE.md e pelo git, não pela memória.
- **Regra da Evidência** em using-onedirection: fato sobre o projeto só com fonte (arquivo:linha, comando, NORTE.md, fala do usuário).
- NORTE.md ganha a seção **"Foco agora"** (o que está sendo feito + próximo passo) e "Pronto quando" passa a exigir critérios verificáveis.
- Hook SessionStart reconhece a compactação e manda usar recovering-focus; avisa quando o NORTE.md passa de 120 linhas.
- Hook UserPromptSubmit passa a trazer a seção "Foco agora" junto do lembrete.
- capturing-the-vision no estilo da brainstorming: olhar antes de perguntar, devolver por partes, separar o que é do usuário do que é proposta.
- mapping-existing-project com a Lei da Evidência e `[x]` só pro que foi verificado.
- guarding-the-direction cobre a fuga do próprio agente e um foco por vez; cita o trecho literal do NORTE.md.
- README reescrito no molde da superpowers.

## 0.1.0 — 2026-11-02

- Primeira versão, estrutura de plugin no mesmo molde da superpowers.
- Skills: using-onedirection, capturing-the-vision, mapping-existing-project, guarding-the-direction, checking-progress.
- Hook SessionStart (startup, clear, compact) injeta using-onedirection + NORTE.md do projeto.
- Hook UserPromptSubmit com lembrete de uma linha em projetos que têm NORTE.md.
