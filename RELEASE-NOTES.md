# Release notes

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
