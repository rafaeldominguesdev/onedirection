# Release notes

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
