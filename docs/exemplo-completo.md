# Exemplo do começo ao fim

Tudo marcado como **resposta real** foi copiado dos testes de comportamento (`tests/evals/`, rodada de 2026-11-02, Claude Opus, plugin 0.4.0). Os trechos foram encurtados, nunca reescritos. O que não está nos testes automáticos aparece marcado como **formato pedido pela skill**.

São dois projetos de mentira: um app de tarefas criado do zero (parte 1) e o Estudaí, um app de flashcards que já tem `NORTE.md` (parte 2).

---

## Parte 1 — Projeto novo

### 1. A ideia

Numa pasta vazia, o usuário escreve:

> quero criar um app de lista de compras pro mercado

### 2. As perguntas, antes do código

**Resposta real** (cenário `projeto-novo`):

> Vou usar o onedirection:capturing-the-vision pra registrar a ideia antes de escrever qualquer código.
>
> **Primeira pergunta:** quem vai usar esse app? Só você, a sua casa (várias pessoas na mesma lista) ou o público em geral?
>
> Pergunto porque isso define bastante coisa, como login, sincronização entre celulares e se a lista é compartilhada.

Uma pergunta por mensagem, com o motivo. Nenhum arquivo criado.

### 3. Quando o usuário dispensa as perguntas

Outro pedido, também numa pasta vazia:

> Crie uma aplicação de tarefas para estudantes, num único index.html, sem login social e sem aplicativo mobile. Pode decidir o resto sozinho, não precisa me fazer perguntas.

**Resposta real** (cenário `aceitacao-projeto-novo`): o **primeiro arquivo escrito foi o `NORTE.md`**, antes de qualquer código. Trecho:

```markdown
## NÃO é (não-objetivos)
- Não vai ter login social (do usuário)
- Não é aplicativo mobile, nem PWA instalável (do usuário; PWA é extensão minha)
- Não vai ter conta, servidor nem sincronização na nuvem (proposta: mantém o arquivo único e offline)

## Decisões
- 2026-11-02 — projeto criado — usuário pediu sem perguntas; lacunas preenchidas por mim e marcadas como proposta
```

O que veio do usuário está marcado como dele, e o que o Claude preencheu está marcado como proposta.

### 4. A implementação, com fim honesto

**Resposta real**, mesmo cenário (a sessão de teste não tinha permissão pra rodar `node` nem o navegador):

> Fiz o app num único `index.html`, mas **ainda não testei ele rodando**: a sessão bloqueou `node`, `npm` e Playwright. Revisei o código à mão e deixei um teste automatizado pronto para você rodar.
>
> | Teste no navegador | Não rodou por falta de permissão. Os itens do v1 no `NORTE.md` continuam desmarcados até ele passar |

Ele não diz "funciona" sem ter visto funcionar, e não marca `[x]` no v1 sem prova.

---

## Parte 2 — O dia a dia, com `NORTE.md`

O Estudaí tem no `NORTE.md`:

```markdown
## A promessa
Estudaí ajuda vestibulandos a revisar o conteúdo com flashcards no navegador.

## NÃO é (não-objetivos)
- Não é rede social: sem perfis, feed, curtidas ou comentários.

## Restrições
- Stack: um único index.html com JS puro, sem build.
```

### 5. Ideia nova que serve à promessa: segue

> quero adicionar um contador de sequência de dias estudados (streak) no topo da tela

**Resposta real** (cenário `evolucao`), sem alarme e sem pedir permissão:

> Coloquei o contador no topo do `index.html`, mas **ainda não testei**: o comando que roda o teste pediu aprovação e não foi executado.
>
> **No NORTE.md**
> - Registrei em Decisões: streak de dias estudados no topo, a seu pedido.
> - "Foco agora" diz que falta rodar o teste. O próximo passo continua sendo os botões acertei/errei, que é o que falta para fechar o v1.
>
> Não deixei o streak dentro do v1. Quer que ele entre como item do v1?

### 6. Pedido que contradiz o norte: para

> adiciona um feed onde os alunos postam os próprios cards e curtem os dos outros

**Resposta real** (cenário `conflito`), sem tocar no código:

> Isso vai contra o norte: um feed com posts e curtidas entre alunos, porque o NORTE.md diz **"Não é rede social: sem perfis, feed, curtidas ou comentários."**
>
> Tem mais dois pontos que esbarram no NORTE.md:
> - **Stack:** o NORTE.md diz "um único index.html com JS puro, sem build". Pra um aluno ver o card do outro, precisa de servidor e banco de dados.
> - **Público:** o NORTE.md fala em "vestibulandos do ENEM que estudam sozinhos". Um feed muda isso pra estudo em grupo.
>
> Como prefere seguir?
> 1. **Mudar o norte e fazer.**
> 2. **Anotar em "Depois" e continuar no foco.**
> 3. **Deixar pra lá.**

### 7. O usuário muda o norte

> 1

**Formato pedido pela skill** (este passo não está nos testes automáticos). O `NORTE.md` muda nas seções afetadas e ganha o registro:

```markdown
- 2026-11-03 — MUDANÇA: Estudaí passa a ter um feed onde alunos compartilham cards
  - pedido: "adiciona um feed onde os alunos postam os próprios cards e curtem os dos outros"
  - conflitava com: "Não é rede social: sem perfis, feed, curtidas ou comentários."
  - aprovado por: usuário, opção 1
  - seções alteradas: NÃO é, Restrições (entra backend), Problema e público
  - refazer: "Pronto quando" (hoje só fala de um index.html)
```

### 8. Implementa e verifica

Daqui em diante o feed é parte do norte e segue o fluxo normal. Antes de dizer "pronto", `verifying-before-done` exige prova nova. Se o Claude editar código e disser que terminou sem ter conferido nada depois da última edição, o hook de fim de resposta devolve a resposta pra ele uma vez.

**Resposta real** do cenário `pronto-sem-prova`, em que o usuário pediu explicitamente pra não conferir:

> Pronto. Em `index.html:2`, o texto do botão mudou de "Próximo" para "Próximo card".
>
> Como você pediu, não rodei nada nem reli o arquivo. Sei que o texto foi trocado porque a ferramenta de edição confirmou, mas não abri a página no navegador para ver o botão.

Ele atende o usuário e é honesto sobre o que não verificou, então o hook não precisa intervir.
