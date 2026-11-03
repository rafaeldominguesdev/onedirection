---
name: guarding-the-direction
description: Use quando o projeto tem NORTE.md e um pedido pode mexer em escopo - feature nova, troca de stack, mudança de público, integração, "já que estamos aqui" - e também quando VOCÊ estiver prestes a fazer algo que ninguém pediu; confere contra a ideia original antes de codar
---

# Guardar a direção

A direção se perde de dois jeitos: o usuário pede algo que foge, ou **você** foge sozinho — a refatoração "rápida", a dependência "melhor", o arquivo a mais "já que estava aberto". Esta skill pega os dois.

**Anuncie só quando fugir:** "Usando onedirection:guarding-the-direction: isso foge do norte."
Se couber no norte, não anuncie nada; faça.

## Conferir (em silêncio)

O NORTE.md está no contexto pelo hook. Se não estiver, leia o arquivo — não confie na memória dele.

1. Serve à promessa?
2. Bate em algum não-objetivo?
3. Contradiz uma decisão registrada?
4. É v1 ou é "Depois"?
5. Tem relação com o "Foco agora"?

## Decidir

| Resultado | Ação |
|---|---|
| Cabe no norte e no foco | Faça. Sem comentário. |
| Tangente pequena (bug, polimento) | Faça. Sem cerimônia. |
| Cabe no norte, mas não no foco atual | Pergunte em 1 linha: "Pauso <foco> pra fazer isso, ou anoto pra depois?" |
| Foge do norte | **Pare antes de codar.** Aviso + 3 opções. |

## As 3 opções

```
Isso foge do norte: <o que foge>, porque o NORTE.md diz "<trecho literal>".
1. Mudar o norte e fazer
2. Anotar em "Depois" e seguir no foco
3. Deixar pra lá
```

Cite o trecho **literal** do NORTE.md. Parafrasear abre espaço pra você distorcer o que está escrito.

1. **Mudar o norte** — edite a seção afetada e adicione em "Decisões": `AAAA-MM-DD — <mudança> — porque <motivo do usuário>`. Depois faça.
2. **Anotar em "Depois"** — adicione o item e volte ao foco.
3. **Deixar pra lá.**

## Um foco por vez

- Ao começar algo, atualize "Foco agora" (Fazendo + Próximo passo). É isso que te devolve ao trilho depois de uma compactação.
- Terminou → use `onedirection:verifying-before-done` antes de dizer pronto. Depois marque `[x]` no v1 se for o caso, atualize "Estado" em 1 linha e o "Foco agora".
- Pedido novo no meio do foco → pergunte se pausa. Não empilhe dois focos em silêncio.

## A sua própria fuga

Antes de cada mudança que você não foi pedido pra fazer:

| Pensamento | Realidade |
|---|---|
| "Já que estou aqui, vou melhorar isso" | Não pedido = fuga. Anote em "Depois" ou pergunte. |
| "Essa lib é melhor que a atual" | Troca de stack é decisão do usuário. Pergunte. |
| "Vou refatorar pra ficar mais limpo" | Refactor não pedido mistura escopo no diff. Pergunte. |
| "É rapidinho, nem precisa avisar" | Rapidinho fora do foco é como o foco morre. |
| "O usuário com certeza vai querer" | Então custa uma pergunta. Faça a pergunta. |

## Regras

- O usuário manda. Escolheu 1, faça sem resmungar.
- Avise uma vez por assunto. Decidido, não volte nele.
- Nunca edite o NORTE.md sem escolha explícita do usuário — exceto "Foco agora" e "Estado", que são seu caderno de bordo.
