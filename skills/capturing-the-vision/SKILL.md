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

Exceção: o usuário disse "não quero perguntas, só faz". Então registre em 3-5 linhas o que você entendeu como NORTE.md mínimo, avise que as lacunas foram decisões suas, e siga.
</HARD-GATE>

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

## Regras do arquivo

- Até ~80 linhas. Ele é injetado em toda sessão.
- v1 é lista de checkboxes; o resto vai pra "Depois".
- Primeira entrada de "Decisões": `AAAA-MM-DD — projeto criado` (data de hoje, verificada com `date`, não chutada).
