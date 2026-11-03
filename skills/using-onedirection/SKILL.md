---
name: using-onedirection
description: Use ao iniciar qualquer conversa - estabelece que a ideia original do projeto (NORTE.md) manda no escopo e qual skill do onedirection usar antes de construir, mudar escopo ou retomar um projeto
---

<SUBAGENT-STOP>
Se você foi despachado como subagente pra executar uma tarefa específica, ignore as cerimônias desta skill. Só não viole os não-objetivos do NORTE.md: se a tarefa bater num deles, diga isso no seu relatório em vez de executar.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
O projeto tem UMA direção: a do NORTE.md. Se houver 1% de chance de um pedido mudar escopo, público, stack ou promessa do projeto, você DEVE usar a skill onedirection certa antes de agir.

Isso não é negociável. "É só uma featurezinha" é exatamente como projetos perdem a direção.
</EXTREMELY-IMPORTANT>

## A Regra

**Use a skill antes de qualquer resposta ou ação** que toque escopo, inclusive antes de perguntas de esclarecimento ou de explorar o código. Anuncie "Usando onedirection:[skill] pra [motivo]" e siga a skill à risca.

| Situação | Skill |
|---|---|
| Vai construir algo e a pasta está vazia / o projeto ainda não existe | `onedirection:capturing-the-vision` |
| Já tem código e não tem `NORTE.md` | `onedirection:mapping-existing-project` |
| Tem `NORTE.md` e o pedido pode mexer em escopo | `onedirection:guarding-the-direction` |
| "Onde estamos?", retomada de projeto, fim de etapa grande | `onedirection:checking-progress` |

Pedido pequeno e óbvio (bug, ajuste visual, refactor, pergunta sobre o código) que cabe no NORTE.md: faça direto, sem cerimônia.

## Prioridade entre skills

O onedirection define **o que o projeto é**. As outras skills de processo definem **como fazer uma parte dele**. Então onedirection vem primeiro.

- "Vamos construir X" num projeto sem NORTE.md → `capturing-the-vision` primeiro, depois brainstorming/planejamento da feature (ex.: `superpowers:brainstorming`, se instalado).
- "Adiciona Y" num projeto com NORTE.md → `guarding-the-direction` primeiro; se couber, segue o fluxo normal.

## Sinais de alerta

Estes pensamentos significam PARE, você está racionalizando:

| Pensamento | Realidade |
|---|---|
| "É só uma feature pequena" | Feature pequena fora do norte é como a direção se perde. Confira. |
| "O usuário pediu, então está dentro" | O usuário pode ter esquecido o próprio norte. Seu trabalho é lembrar. |
| "Depois eu atualizo o NORTE.md" | Nunca. Mudança de direção é registrada antes de codar. |
| "Já sei qual é a ideia do projeto" | Você sabe o que está no NORTE.md. O resto é chute. Leia. |
| "Vou explorar o código primeiro" | A skill diz como explorar. Use a skill primeiro. |
| "Esse projeto é simples demais pra ter norte" | Projeto simples é o que mais cresce torto. Leva 5 minutos. |
| "Vou melhorar isso aqui já que estou mexendo" | Melhoria não pedida é fuga de escopo. Pergunte ou anote em "Depois". |

## Regras gerais

- O usuário manda. O onedirection avisa, não bloqueia. Se ele decidir mudar a direção, mude e registre.
- Nunca edite o NORTE.md em silêncio. Toda mudança nele é combinada.
- Avise uma vez por assunto. Decidido, não insista.

## Instruções do usuário

Instruções do usuário (CLAUDE.md, AGENTS.md, pedidos diretos) têm precedência sobre estas skills, que por sua vez têm precedência sobre o comportamento padrão. Só pule o fluxo do onedirection quando o usuário mandar explicitamente.
