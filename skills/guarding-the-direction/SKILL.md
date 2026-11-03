---
name: guarding-the-direction
description: Use quando o projeto tem NORTE.md e um pedido pode mexer em escopo - feature nova, troca de stack, mudança de público, integração, "já que estamos aqui" - confere contra a ideia original antes de codar
---

# Guardar a direção

**Anuncie só quando o pedido fugir:** "Usando onedirection:guarding-the-direction: isso foge do norte."
Se couber no norte, não anuncie nada; faça.

## Conferir (em silêncio)

Leia o NORTE.md (já está no contexto pelo hook; se não estiver, leia o arquivo) e responda:

1. Serve à promessa?
2. Bate em algum não-objetivo?
3. Contradiz uma decisão registrada?
4. É v1 ou é "Depois"?

## Decidir

| Resultado | Ação |
|---|---|
| Cabe no norte | Faça normalmente. Sem comentário. |
| Tangente pequena (detalhe, polimento, bug) | Faça. Sem cerimônia. |
| Foge do norte | **Pare antes de codar.** Avise em 2-3 linhas: o que foge e de qual item do NORTE.md. Dê as 3 opções. |

## As 3 opções

1. **Mudar o norte** — o usuário mudou de ideia de propósito. Edite o NORTE.md (a seção afetada) e adicione em "Decisões": `AAAA-MM-DD — <mudança> — porque <motivo do usuário>`. Depois faça.
2. **Anotar em "Depois"** — adicione o item na seção "Depois" do NORTE.md e volte ao que estava.
3. **Deixar pra lá.**

Formato do aviso:

```
Isso foge do norte: <o que foge>, porque o NORTE.md diz "<trecho>".
1. Mudar o norte e fazer
2. Anotar em "Depois" e seguir no v1
3. Deixar pra lá
```

## Regras

- O usuário manda. Escolheu 1, faça sem resmungar.
- Avise uma vez por assunto. Não volte nele.
- Nunca edite o NORTE.md sem a escolha explícita do usuário.
- Fuga de escopo **sua** também conta: não adicione "melhorias" que ninguém pediu.
- Ao concluir um item do v1, marque `[x]` no NORTE.md e atualize "Estado" em 1 linha.
