---
name: checking-progress
description: Use quando o usuário perguntar "onde estamos", chamar /onedirection, retomar um projeto depois de um tempo ou fechar uma etapa grande - compara o NORTE.md com o que o código realmente tem
---

# Conferir o progresso

**Anuncie no início:** "Usando onedirection:checking-progress pra comparar o projeto com o norte."

Sem NORTE.md: pare e use `onedirection:mapping-existing-project` (tem código) ou `onedirection:capturing-the-vision` (não tem).

## Checklist

1. **Ler o NORTE.md.**
2. **Verificar no código cada item do v1.** Não confie nos checkboxes: abra o código, rode o build ou os testes se for barato. Um item só está pronto se funciona.
3. **Procurar desvios desde a última conferência:** `git log` desde a última data em "Decisões"; funcionalidades que não estão no norte.
4. **Relatar** no formato abaixo.
5. **Propor a atualização** dos checkboxes e de "Estado". Só grave depois que o usuário concordar.

## Formato do relatório

```
Promessa: <frase do NORTE.md>

| Item do v1 | Status | Evidência |
|---|---|---|
| ... | pronto / parcial / falta | arquivo:linha ou comando |

Desvios: <tópicos, ou "nenhum">
Próximo passo que mais aproxima do "Pronto quando": <um só>
```
