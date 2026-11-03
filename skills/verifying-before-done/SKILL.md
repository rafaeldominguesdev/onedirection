---
name: verifying-before-done
description: Use quando estiver prestes a dizer que algo está pronto, funcionando, corrigido ou feito - antes de commit, antes de marcar [x] no NORTE.md, antes de passar pra próxima tarefa; exige prova nova e confere se o que foi feito é o que foi pedido
---

# Verificar antes de dizer pronto

**Princípio:** prova antes de afirmação. Sempre.

Dois jeitos de mentir sem querer: dizer que funciona sem ter visto funcionar, e dizer que fez o pedido quando fez outra coisa (ou o pedido *mais* outras coisas). Esta skill fecha os dois.

## A Lei de Ferro

```
NENHUM "PRONTO" SEM PROVA NOVA, NESTA MENSAGEM
```

Se você não rodou a verificação agora, não pode dizer que passa.

## O Portão

```
ANTES de qualquer afirmação de status:

1. PROVA     Qual comando prova isso? Rode inteiro, agora. Leia a saída e o exit code.
2. PEDIDO    Releia o pedido original do usuário. Liste item a item. Cada um foi feito?
3. ESCOPO    git diff --stat. Algum arquivo mudou sem ter sido pedido? Isso é fuga — explique ou desfaça.
4. NORTE     O resultado contradiz algum não-objetivo do NORTE.md?
5. SÓ ENTÃO  Afirme, com a prova junto. Se algo falhou, diga o status real.

Pular um passo = chutar, não verificar.
```

## O que conta como prova

| Afirmação | Precisa de | Não serve |
|---|---|---|
| Testes passam | Saída do comando: 0 falhas | Rodada anterior, "deve passar" |
| Build ok | Build com exit 0 | Lint passou, "parece certo" |
| Bug corrigido | O sintoma original testado e sumido | Código mudou, então "deve ter resolvido" |
| Tela/UI ok | Você viu (screenshot, app aberto) | Compilou |
| Pedido atendido | Checklist item a item do pedido | Testes passando |
| Subagente concluiu | `git diff` mostra a mudança | O relatório dele diz "sucesso" |
| Item do v1 pronto | Funciona de ponta a ponta | A parte principal existe |

## Sinais de alerta — PARE

- "deve", "provavelmente", "parece que", "acho que já"
- Comemorar antes de verificar ("Pronto!", "Perfeito!", "Funcionando!")
- Commit/push sem ter rodado nada
- Confiar no relatório de um subagente
- Verificação parcial
- "Só dessa vez"

## Desculpas

| Desculpa | Realidade |
|---|---|
| "Agora vai funcionar" | Rode. |
| "Tenho confiança" | Confiança não é prova. |
| "A mudança foi pequena" | Mudança pequena quebra build igual. |
| "Não tem como testar isso" | Diga isso explicitamente: "não verifiquei X porque Y". Nunca omita. |
| "Os outros arquivos eram melhorias óbvias" | Não pedido. Explique no relatório ou desfaça. |

## O hook de fim de resposta

Se você editar código e encerrar a resposta dizendo que terminou sem ter conferido nada depois da última edição (rodar um comando, reler o arquivo editado ou buscar nele; listar arquivos não conta), o onedirection devolve a resposta pra você uma vez com este lembrete. O hook só vê que houve alguma conferência, não se ela prova o que você afirmou: escolher a prova certa (tabela acima) continua sendo seu trabalho. Não é castigo: é o portão acima sendo cobrado. Confira e mostre a prova, ou declare o que não verificou.

## Quando não dá pra verificar

Às vezes não dá (sem acesso, hardware, conta). Então o relatório diz, com essas palavras: **"Não verifiquei: <o quê> — porque <motivo>."** Nunca apresente como feito o que não foi visto funcionando.

## Depois de verificar

Se o projeto tem NORTE.md: marque `[x]` no item do v1 (se for o caso), atualize "Estado" em 1 linha e o "Foco agora" pro próximo passo.
