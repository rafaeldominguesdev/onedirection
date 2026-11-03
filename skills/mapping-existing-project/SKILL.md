---
name: mapping-existing-project
description: Use ao entrar num projeto que já tem código mas não tem NORTE.md - lê o projeto inteiro, reconstrói a ideia original, aponta onde já fugiu dela e grava o NORTE.md aprovado
---

# Mapear um projeto em andamento

**Anuncie no início:** "Usando onedirection:mapping-existing-project pra entender o projeto antes de mexer."

<HARD-GATE>
Não mude código antes de o NORTE.md existir e o usuário aprovar. Ler pode; editar não.
</HARD-GATE>

## Checklist

Crie uma tarefa pra cada item:

1. **Ler os documentos**
2. **Ler a história**
3. **Ler o código**
4. **Rascunhar o NORTE.md** com as inferências marcadas
5. **Apontar os desvios**
6. **Confirmar com o usuário** e gravar

## 1. Documentos

`README*`, `CLAUDE.md`, `AGENTS.md`, `HANDOFF.md`, `docs/`, qualquer `*.md` de planejamento na raiz. Manifestos: `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, `Package.swift`, `tauri.conf.json`. Nome, descrição e dependências dizem muito.

## 2. História

```bash
git log --reverse --format='%h %ad %s' --date=short | head -30   # a ideia original mora no começo
git log --format='%h %ad %s' --date=short -40                    # pra onde o projeto está indo agora
```

Compare o começo com o agora. A diferença entre os dois é onde a direção pode ter se perdido.

## 3. Código

Estrutura de pastas e pontos de entrada: rotas, telas, comandos, `main`. Projeto grande: despache o agente Explore pra varrer em vez de ler arquivo por arquivo; peça a lista de funcionalidades que existem de verdade.

## 4. Rascunho

Use `../capturing-the-vision/norte-template.md`. Regras:

- Só escreva o que **está no código ou nos docs**.
- Marque com `(?)` tudo que foi inferido.
- Em "v1 obrigatório", marque `[x]` o que o código mostra que funciona, não o que o README promete.
- Em "Estado", diga onde o projeto realmente está.

## 5. Desvios

Liste em tópicos curtos:
- Funcionalidades órfãs (existem mas não servem à promessa).
- Coisas pela metade.
- Duas direções brigando no mesmo código.
- Promessas do README que o código não cumpre.

## 6. Confirmar

Mostre ao usuário: "Entendi que a ideia é esta. Confere?" Pergunte só o que está marcado com `(?)`, uma dúvida por vez. Grave o NORTE.md aprovado na raiz, sem as marcas `(?)`.
