---
name: checking-progress
description: Use quando o usuário perguntar "onde estamos", "quanto falta", retomar um projeto depois de dias, ou ao fechar uma etapa grande - compara cada item do NORTE.md com o que o código realmente faz, com evidência
---

# Conferir o progresso

**Anuncie:** "Usando onedirection:checking-progress pra comparar o projeto com o norte."

Sem NORTE.md: pare e use `onedirection:mapping-existing-project` (tem código) ou `onedirection:capturing-the-vision` (não tem).

## A Regra

```
CHECKBOX NÃO É PROVA. CADA ITEM DO V1 É VERIFICADO NO CÓDIGO AGORA.
```

## Checklist

1. **Ler o NORTE.md** — o arquivo, não a sua memória dele.
2. **Verificar cada item do v1** — abra o código, rode build/testes se for barato. Pronto = funciona de ponta a ponta.
3. **Procurar desvios** — `git log` desde a última data em "Decisões"; funcionalidades que existem e não estão no norte.
4. **Relatar** no formato abaixo.
5. **Propor a atualização** dos checkboxes, "Estado" e "Foco agora". Grave só depois que o usuário concordar.

## Formato

```
Promessa: <frase literal do NORTE.md>

| Item do v1 | Status | Evidência |
|---|---|---|
| ... | pronto / parcial / falta | arquivo:linha ou comando + resultado |

Desvios: <tópicos com fonte, ou "nenhum">
Não verifiquei: <o quê e por quê, ou "nada">
Próximo passo que mais aproxima do "Pronto quando": <um só>
```

## Sinais de alerta

| Pensamento | Realidade |
|---|---|
| "Está marcado [x], então está pronto" | Marcado por quem, quando? Verifique. |
| "A tela existe, então o item está pronto" | Existir não é funcionar. Ponta a ponta. |
| "Não dá pra rodar, vou assumir que funciona" | Vai pra "Não verifiquei". Nunca pra "pronto". |
