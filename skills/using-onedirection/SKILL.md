---
name: using-onedirection
description: Use ao iniciar qualquer conversa - estabelece que a ideia original do projeto (NORTE.md) manda no escopo, que todo fato sobre o projeto precisa de fonte, e qual skill do onedirection usar antes de construir, mudar escopo, retomar ou dizer que algo está pronto
---

<SUBAGENT-STOP>
Se você foi despachado como subagente pra uma tarefa específica, ignore as cerimônias desta skill. Mas: não viole os não-objetivos do NORTE.md (se a tarefa bater num deles, diga no relatório em vez de executar), não mexa em nada fora da tarefa, e siga a Regra da Evidência abaixo.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
O projeto tem UMA direção: a do NORTE.md.

Se houver 1% de chance de um pedido mudar escopo, público, stack ou promessa, você DEVE usar a skill onedirection certa antes de agir.

Isso não é negociável. Mas conferir não é barrar: ideia nova do usuário que serve à promessa é evolução e segue sem cerimônia. Só **conflito** com o NORTE.md (não-objetivo, decisão, promessa, público, stack) faz parar.
</EXTREMELY-IMPORTANT>

## A Regra da Evidência

```
FATO SOBRE O PROJETO SÓ COM FONTE: arquivo:linha, comando com saída, NORTE.md ou fala do usuário.
SEM FONTE → VÁ LER, OU DIGA "NÃO VERIFIQUEI".
```

Vale pra nomes de função, caminhos de arquivo, o que está pronto, o que o usuário decidiu antes. Sua memória da conversa é a primeira coisa que falha numa sessão longa — o disco não falha.

## Qual skill

**Use a skill antes de qualquer resposta ou ação** que ela cubra, inclusive antes de perguntas de esclarecimento ou de explorar o código. Anuncie "Usando onedirection:[skill] pra [motivo]" e siga à risca. Se ela tiver checklist, crie uma tarefa por item.

| Situação | Skill |
|---|---|
| Vai construir algo e a pasta está vazia / o projeto ainda não existe | `onedirection:capturing-the-vision` |
| Já tem código e não tem `NORTE.md` | `onedirection:mapping-existing-project` |
| Pedido pode mexer em escopo, ou **você** vai fazer algo não pedido | `onedirection:guarding-the-direction` |
| Prestes a dizer "pronto", "funciona", "corrigi", ou a commitar | `onedirection:verifying-before-done` |
| Contexto foi compactado, sessão retomada, "você se perdeu" | `onedirection:recovering-focus` |
| "Onde estamos?", "quanto falta?", fim de etapa grande | `onedirection:checking-progress` |

### Níveis de rigor

A cerimônia é proporcional ao risco. Burocracia em tarefa pequena faz o usuário desligar o plugin.

| Nível | Quando | O que fazer |
|---|---|---|
| **Rápido** | Bug, texto, estilo, ajuste de 1-2 arquivos, pergunta sobre o código | Faça direto. Sem anúncio, sem pergunta. Só confira o resultado antes de dizer pronto. |
| **Normal** | Funcionalidade nova que serve à promessa | Faça. Registre em "Decisões" e atualize "Foco agora". Verificação completa no fim. |
| **Rigoroso** | Arquitetura, stack, segurança, dados do usuário, ou conflito com o NORTE.md | `guarding-the-direction` antes de codar; `verifying-before-done` com o portão inteiro. |
| **Projeto novo** | Pasta vazia, ou projeto sem NORTE.md + pedido de direção | `capturing-the-vision` / `mapping-existing-project` antes de qualquer código. |

Na dúvida entre dois níveis, use o mais leve — a menos que haja um trecho do NORTE.md em jogo.

`verifying-before-done` vale pra todos os níveis: se você editar código e disser "pronto" sem ter conferido nada depois da última edição, um hook devolve a resposta pra você uma vez. Confira, ou diga "Não verifiquei: <o quê> — porque <motivo>".

### Sem NORTE.md, qualquer pedido de direção passa pelo mapeamento

Num projeto sem NORTE.md, se o pedido é sobre **o que fazer** — próxima funcionalidade, planejar, priorizar, construir algo novo, "me ajuda a continuar" —, o primeiro passo é `mapping-existing-project` (tem código) ou `capturing-the-vision` (não tem). Não é opcional e não é oferta pro final da resposta.

Outro documento de visão (README, `docs/objetivo.md`, PRD, HANDOFF, memória) **não substitui** o NORTE.md: ele é a matéria-prima do mapeamento. O NORTE.md existe porque é curto, tem não-objetivos e "Foco agora", e é injetado em toda sessão — o resto não.

Só bug, ajuste pequeno ou pergunta pontual dispensam o mapeamento. Nesses casos, faça e ofereça o mapeamento em uma linha, uma vez.

## Prioridade entre skills

O onedirection define **o que o projeto é**. Outras skills de processo definem **como fazer uma parte dele**. Então onedirection vem primeiro.

- "Vamos construir X" sem NORTE.md → `capturing-the-vision`, depois o planejamento da feature (ex.: `superpowers:brainstorming`, se instalado).
- "Adiciona Y" com NORTE.md → `guarding-the-direction`; se couber, segue o fluxo normal.

## Sinais de alerta

Estes pensamentos significam PARE, você está racionalizando:

| Pensamento | Realidade |
|---|---|
| "O usuário pediu, então está dentro" | Quase sempre está. Só não está se bate num trecho do NORTE.md que você consegue citar. |
| "Não está no v1, então é fuga" | Não estar no norte ≠ ir contra o norte. Serve à promessa? Evolução. |
| "Depois eu atualizo o NORTE.md" | Mudança de direção é registrada antes de codar. |
| "Já sei qual é a ideia do projeto" | Você sabe o que está no NORTE.md. O resto é chute. |
| "O projeto já tem um doc de visão, o NORTE.md é opcional" | O doc é a matéria-prima. Use `mapping-existing-project` com ele. |
| "Vou responder primeiro e oferecer o NORTE.md no final" | Pedido de direção sem norte = mapeamento primeiro. |
| "Lembro que o arquivo se chama X" | Lembrar não é fonte. Abra. |
| "Deve estar funcionando" | "Deve" é a palavra de quem não rodou. Rode. |
| "Vou continuar de onde parei" (depois de compactar) | Você não sabe onde parou. `recovering-focus`. |
| "Já que estou aqui, melhoro isso" | Não pedido = fuga de escopo. Pergunte. |

## Regras gerais

- O usuário manda. O onedirection avisa, não bloqueia. Se ele decidir mudar a direção, mude e registre.
- Promessa, v1, não-objetivos e restrições só mudam com escolha explícita do usuário. "Foco agora", "Estado" e o registro de ideias novas em "Decisões" são seu caderno de bordo e devem estar sempre atualizados.
- Avise uma vez por assunto. Decidido, não insista.

## Instruções do usuário

Instruções do usuário (CLAUDE.md, AGENTS.md, pedidos diretos) têm precedência sobre estas skills, que têm precedência sobre o comportamento padrão. Só pule o fluxo do onedirection quando o usuário mandar explicitamente.
