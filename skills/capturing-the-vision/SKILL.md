---
name: capturing-the-vision
description: "Use ANTES de escrever qualquer código num projeto novo ou pasta vazia - entrevista o usuário e grava a ideia original no NORTE.md, que vira a fonte da verdade do escopo"
---

# Capturar a ideia

Você constrói bem. Você constrói o que *acha* que o usuário quer, e esse "acha" costuma ser mais fino do que parece. Esta skill existe pra descobrir o que ele quer de verdade, e por quê, antes de qualquer linha de código — e deixar isso escrito, porque a sua memória da conversa não sobrevive a uma compactação. O NORTE.md sobrevive.

**Anuncie:** "Usando onedirection:capturing-the-vision pra registrar a ideia antes do código."

<HARD-GATE>
Nada é construído antes de o NORTE.md existir e o usuário aprovar.
Construir inclui: código de produto, scaffold, instalar dependência, criar projeto (`npm create`, `cargo new`…), chamar skill de implementação.
Ler e explorar pode.

Exceção: o usuário disse "não quero perguntas, só faz" ou "decide o resto". Então grave o NORTE.md com o que ele disse, marque as lacunas como proposta sua, e construa **só o v1** — veja "O v1 é o mínimo" abaixo. Delegar as decisões não é pedir mais coisa: é confiar que você vai escolher o menor caminho.
</HARD-GATE>

## O v1 é o mínimo

```
V1 = O MENOR CONJUNTO QUE ENTREGA A PROMESSA. NO MÁXIMO 4 ITENS.
```

Pra cada item candidato, pergunte: **sem isto, a promessa deixa de existir?**
- Sim → v1.
- Não → "Depois". Mesmo que seja bom, mesmo que seja rápido, mesmo que "todo app desse tipo tenha".

Ideia sua (que o usuário não pediu) entra no v1 só se passar nesse teste. O resto vai pra "Depois", onde ele pode puxar quando quiser. Construa só o que está no v1.

| Pedido: "controle de gastos pessoais" | Onde vai |
|---|---|
| Registrar gasto com valor e data | v1 — sem isso não há controle de gastos |
| Ver o total do mês | v1 — é o que "controlar" quer dizer |
| Categorias | v1, se o usuário falou em categorias; senão "Depois" |
| Gráficos, metas, exportar planilha, tema escuro, várias moedas | "Depois" |

## Checklist

Crie uma tarefa por item, nesta ordem:

1. **Olhar antes de perguntar** — se o usuário deu contexto (arquivos, links, conversa anterior), leia tudo antes da primeira pergunta. Nunca pergunte o que o material já responde.
2. **Entrevistar** — uma pergunta por mensagem.
3. **Devolver por partes** — a cada parte entendida, descreva em poucas linhas e pergunte o que está errado.
4. **Escrever o NORTE.md** na raiz, com `norte-template.md` desta pasta.
5. **Aprovação explícita** — "pode ser" sobre a ideia não é aprovação do arquivo. Mostre o arquivo.
6. **Liberar a construção** — preencha "Foco agora" com o primeiro passo e só então comece.

## Território a cobrir

Isto é território, não roteiro. Não leia em voz alta como questionário.

| Tema | O que você precisa sair sabendo |
|---|---|
| Problema | Que dor isso resolve |
| Público | Pra quem, exatamente ("todo mundo" não vale; peça um exemplo real) |
| Promessa | "X ajuda Y a fazer Z", nas palavras do usuário |
| v1 | O mínimo pra a ideia existir |
| **Não-objetivos** | O que isso **não** é e não vai ter |
| Restrições | Stack, prazo, orçamento, plataforma, estilo |
| Pronto | Como saber que o v1 está pronto — de forma verificável |

**Não-objetivos é o item mais importante.** É ele que segura a direção semanas depois. Se o usuário travar, proponha 3 tentações óbvias pro tipo de projeto ("não vai ter login social?", "não é app mobile?") e pergunte quais valem.

**"Pronto quando" tem que ser verificável.** "Ficar bom" não serve. "Um usuário novo cria conta e publica um post em menos de 1 minuto" serve.

## Como perguntar

- Uma pergunta por mensagem, uma frase, sem lista de exemplos pendurada.
- Diga por que está perguntando quando não for óbvio: o que a resposta muda no que vai ser construído.
- Pergunte com base na última resposta, como um colega afiado faria.
- Use o vocabulário do usuário. Nada de jargão de processo.
- "Sei lá, decide você" → proponha algo concreto e diga o motivo.

## Separar o que é dele do que é seu

No NORTE.md e nas devoluções:
- O que o usuário disse entra como dele.
- O que você preencheu entra marcado como **proposta sua**, com o motivo. Ex.: `- Stack: Next.js (proposta: você já usa no Aprova)`.

Um padrão que ele nunca ouviu é um padrão que ele não pôde recusar.

## Sinais de alerta

| Pensamento | Realidade |
|---|---|
| "Vou oferecer um menu de opções" | Opções conduzem. Peça pra ele descrever primeiro. |
| "Já entendi, vou escrever o NORTE.md" | Devolveu por partes? Ele corrigiu? Se não, não entendeu. |
| "Ele disse 'legal' pra ideia" | Aprovação cobre o que você mostrou. Arquivo não mostrado não está aprovado. |
| "Vou adiantar o scaffold enquanto ele responde" | Scaffold é construção. Gate. |
| "Não-objetivo é óbvio, pulo" | O óbvio é o que escapa em 3 semanas. Escreva. |
| "Ele deixou eu decidir, vou fazer um app completo" | Delegar não é pedir mais. Menor v1 que entrega a promessa; o resto em "Depois". |
| "É rapidinho adicionar mais esse recurso" | Rapidinho multiplicado por 7 vira um app de 1.600 linhas que ninguém pediu. "Depois". |

## Regras do arquivo

- Até ~80 linhas. Ele é injetado em toda sessão.
- v1 é lista de checkboxes, no máximo 4; o resto vai pra "Depois".
- Na criação, todo item do v1 começa `[ ]` e o "Estado" diz o que existe **agora** (ex.: "só existe este NORTE.md"). Nunca escreva o NORTE.md com o estado que você espera ter no fim: `[x]` só depois de verificar.
- Primeira entrada de "Decisões": `AAAA-MM-DD — projeto criado` (data de hoje, verificada com `date`, não chutada).
