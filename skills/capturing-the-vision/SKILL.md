---
name: capturing-the-vision
description: Use antes de escrever qualquer código num projeto novo - entrevista o usuário e grava a ideia original no NORTE.md, que vira a fonte da verdade do escopo
---

# Capturar a ideia

**Anuncie no início:** "Usando onedirection:capturing-the-vision pra registrar a ideia antes do código."

<HARD-GATE>
Não escreva código, não crie scaffold, não instale dependência antes de o NORTE.md existir e o usuário aprovar.
</HARD-GATE>

## Checklist

Crie uma tarefa pra cada item:

1. **Entrevistar** — uma pergunta por vez, curta. Prefira múltipla escolha quando der.
2. **Escrever o NORTE.md** na raiz do projeto, usando `norte-template.md` desta pasta.
3. **Mostrar e pedir aprovação** — ajustar até o usuário dizer que está certo.
4. **Liberar a construção** — só agora o trabalho começa.

## O que perguntar

Pare assim que tiver o suficiente. Não interrogue à toa.

| Tema | Pergunta |
|---|---|
| Problema | Que dor isso resolve? |
| Público | Pra quem, exatamente? ("todo mundo" não vale; peça uma pessoa real) |
| Promessa | Em uma frase: "X ajuda Y a fazer Z" |
| v1 | Qual o mínimo pra a ideia existir? |
| **Não-objetivos** | O que isso **não** é? O que não vai ter? |
| Restrições | Stack, prazo, orçamento, plataforma, estilo visual |
| Pronto | Como você vai saber que o v1 está pronto? |

**Não-objetivos é o item mais importante.** É ele que segura a direção depois. Se o usuário não souber responder, sugira 3 tentações óbvias pro tipo de projeto ("não vai ter login social", "não é app mobile") e pergunte quais valem.

## Regras

- O NORTE.md tem que ser curto (até ~80 linhas). Ele é injetado em toda sessão.
- Use as palavras do usuário na promessa, não as suas.
- v1 é lista de checkboxes; o que não for v1 vai pra "Depois".
- Registre a data de hoje na primeira entrada de "Decisões": "AAAA-MM-DD — projeto criado".
