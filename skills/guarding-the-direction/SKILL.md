---
name: guarding-the-direction
description: Use quando o projeto tem NORTE.md e um pedido pode mexer em escopo - feature nova, troca de stack, mudança de público, integração, "já que estamos aqui" - e também quando VOCÊ estiver prestes a fazer algo que ninguém pediu; separa evolução (segue) de conflito com o norte (para)
---

# Guardar a direção

A direção se perde de dois jeitos: o usuário pede algo que **contradiz** o norte, ou **você** foge sozinho — a refatoração "rápida", a dependência "melhor", o arquivo a mais "já que estava aberto".

Ideia nova do usuário que serve ao projeto **não é perda de foco**. É o projeto evoluindo. Tratar evolução como fuga transforma o onedirection num chato que o usuário vai desligar.

## A Regra

```
NÃO ESTAR NO NORTE.md ≠ IR CONTRA O NORTE.md
O ALARME TOCA PRA CONFLITO, NUNCA PRA NOVIDADE.
```

O NORTE.md lista o que precisa existir (v1) e o que não pode existir (não-objetivos). Tudo entre os dois é espaço livre, desde que sirva à promessa.

## Conferir (em silêncio)

O NORTE.md está no contexto pelo hook. Se não estiver, leia o arquivo — não confie na memória dele.

1. **Conflito?** Bate em algum não-objetivo, contradiz uma decisão registrada, ou muda a promessa, o público ou a stack?
2. **Serve à promessa?** Ajuda o público do NORTE.md a fazer o que a promessa diz?
3. **Foco:** tem trabalho pela metade (`git status` sujo, "Foco agora" sem concluir)?
4. **Quem pediu?** O usuário, ou é ideia sua?

## Decidir

| Situação | Nível | Ação |
|---|---|---|
| Cabe no v1 / no foco atual | — | Faça. Sem comentário. |
| Bug, polimento, ajuste pequeno | — | Faça. Sem cerimônia. |
| **Ideia nova do usuário**, serve à promessa, sem conflito | Evolução | Faça. No relatório final, 1 linha: "Registrei em Decisões: <ideia>". Não pergunte se pode. |
| Ideia do usuário que serve, mas tem trabalho pela metade | Troca de foco | 1 linha: "Pauso <foco> (fica salvo em Foco agora) ou termino antes?" Sem trabalho pendente: só troque o foco. |
| Ideia do usuário que **não serve à promessa** mas não bate em não-objetivo | Dúvida | 1 linha: "Isso não tem a ver com <promessa> — é parte do projeto ou é outra coisa?" Respondeu que é parte: siga como evolução. |
| Bate em não-objetivo, contradiz decisão, muda promessa/público/stack | **Conflito** | **Pare antes de codar.** Aviso + 3 opções. |
| **Ideia sua** que ninguém pediu | Fuga sua | Não faça. Anote em "Depois" ou pergunte em 1 linha. |

Na dúvida entre evolução e conflito: é evolução. Só é conflito se você consegue apontar o trecho do NORTE.md que a ideia contradiz.

## Conflito: as 3 opções

```
Isso vai contra o norte: <o que conflita>, porque o NORTE.md diz "<trecho literal>".
1. Mudar o norte e fazer
2. Anotar em "Depois" e seguir no foco
3. Deixar pra lá
```

Cite o trecho **literal**. Se você não acha um trecho pra citar, não é conflito — volte pra tabela.

1. **Mudar o norte** — edite a seção afetada e adicione em "Decisões": `AAAA-MM-DD — <mudança> — porque <motivo do usuário>`. Depois faça.
2. **Anotar em "Depois"** — adicione o item e volte ao foco.
3. **Deixar pra lá.**

## Registrar evolução

Ideia nova que entrou no projeto vai pro NORTE.md, pra não sumir numa compactação:
- Em "Decisões": `AAAA-MM-DD — entra <ideia> — pedido do usuário`.
- Se ela vira parte do que precisa estar pronto, proponha no relatório: "Coloco <ideia> no v1?" — o v1 só muda com o sim dele.

## Um foco por vez

- Ao começar algo, atualize "Foco agora" (Fazendo + Próximo passo). É isso que te devolve ao trilho depois de uma compactação.
- Terminou → `onedirection:verifying-before-done` antes de dizer pronto. Depois marque `[x]` no v1 se for o caso, atualize "Estado" e "Foco agora".
- O usuário mudar de assunto é troca de foco, não perda. Perda é **você** misturar duas coisas no mesmo diff sem ninguém pedir.

## Sinais de alerta

Do lado do excesso de zelo:

| Pensamento | Realidade |
|---|---|
| "Isso não está no v1, então foge" | Não estar ≠ ir contra. Serve à promessa? Então é evolução. |
| "Melhor confirmar se ele quer mesmo" | Ele acabou de pedir. Confirmar o óbvio é ruído. |
| "Vou avisar só por precaução" | Aviso sem trecho literal pra citar é alarme falso. |

Do lado da sua própria fuga:

| Pensamento | Realidade |
|---|---|
| "Já que estou aqui, vou melhorar isso" | Não pedido = fuga. Anote em "Depois" ou pergunte. |
| "Essa lib é melhor que a atual" | Troca de stack é decisão do usuário. Pergunte. |
| "Vou refatorar pra ficar mais limpo" | Refactor não pedido mistura escopo no diff. Pergunte. |
| "O usuário com certeza vai querer" | Então custa uma pergunta. Faça a pergunta. |

## Regras

- O usuário manda. Escolheu "mudar o norte", faça sem resmungar.
- Avise uma vez por assunto. Decidido, não volte nele.
- Promessa, v1, não-objetivos e restrições só mudam com escolha explícita do usuário. "Foco agora", "Estado" e o registro de evolução em "Decisões" são seu caderno de bordo.
