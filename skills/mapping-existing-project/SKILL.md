---
name: mapping-existing-project
description: Use ao entrar num projeto que já tem código mas não tem NORTE.md - lê o projeto inteiro, reconstrói a ideia original com evidência, aponta onde já fugiu dela e grava o NORTE.md aprovado
---

# Mapear um projeto em andamento

O risco aqui é inventar. Um projeto em andamento parece contar uma história, e é fácil preencher as lacunas com o que "faz sentido". Esta skill obriga cada afirmação sobre o projeto a ter fonte.

**Anuncie:** "Usando onedirection:mapping-existing-project pra entender o projeto antes de mexer."

<HARD-GATE>
Não mude código antes de o NORTE.md existir e o usuário aprovar. Ler pode; editar não.
</HARD-GATE>

## A Lei da Evidência

```
TODA AFIRMAÇÃO SOBRE O PROJETO TEM FONTE: arquivo:linha, comando com saída, ou fala do usuário.
SEM FONTE = (?)
```

## Checklist

Crie uma tarefa por item:

1. **Documentos** — `README*`, `CLAUDE.md`, `AGENTS.md`, `HANDOFF.md`, `docs/`, `*.md` de planejamento. Manifestos: `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, `Package.swift`, `tauri.conf.json`.
2. **História** — o começo e o agora:
   ```bash
   git log --reverse --format='%h %ad %s' --date=short | head -30   # a ideia original mora no começo
   git log --format='%h %ad %s' --date=short -40                    # pra onde está indo
   git status --short                                               # trabalho pela metade
   ```
3. **Código** — estrutura, pontos de entrada (rotas, telas, comandos, `main`). Projeto grande: despache o agente Explore pedindo **a lista de funcionalidades que existem de verdade, com arquivo de cada uma**.
4. **Verificar o que funciona** — se for barato, rode build/testes. Um item só conta como feito se você viu funcionar ou viu o código completo dele.
5. **Rascunho do NORTE.md** com `../capturing-the-vision/norte-template.md`.
6. **Desvios** — liste.
7. **Confirmar** com o usuário e gravar.

## Regras do rascunho

- Promessa, público e não-objetivos quase nunca estão no código. Se não estiverem escritos em algum doc, são `(?)` — pergunte, não deduza.
- "v1 obrigatório": `[x]` só pro que você verificou no passo 4. README prometendo não é evidência.
- Ao lado de cada item, a fonte entre parênteses na versão que você mostra ao usuário: `- [x] login com e-mail (src/auth/login.ts:12)`. Na versão gravada, pode tirar.
- "Foco agora": se `git status` mostra trabalho pela metade, é isso. Senão, `(?)`.

## Desvios

Tópicos curtos, cada um com fonte:
- Funcionalidade órfã (existe mas não serve à promessa).
- Coisa pela metade.
- Duas direções brigando no mesmo código.
- Promessa do README que o código não cumpre.

## Confirmar

"Entendi que a ideia é esta. Confere?" Pergunte só o que está `(?)`, uma dúvida por mensagem, a mais importante primeiro. Grave o NORTE.md aprovado na raiz, sem as marcas.

## Sinais de alerta

| Pensamento | Realidade |
|---|---|
| "O nome do projeto deixa claro o objetivo" | Nome não é promessa. `(?)` e pergunte. |
| "Essa pasta deve ser a parte de pagamentos" | "Deve ser" = você não abriu. Abra. |
| "O README diz que tem, então tem" | README envelhece. Verifique no código. |
| "Li os arquivos principais, já entendi" | Entendeu o que leu. O resto é `(?)`. |
| "Vou perguntar qual é a stack" | O manifesto responde. Nunca pergunte o que o código responde. |
