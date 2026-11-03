---
name: recovering-focus
description: Use logo depois de uma compactação de contexto, ao retomar uma sessão, quando o usuário disser "perdeu o foco", "onde a gente tava", "você se perdeu", ou quando você notar que não sabe exatamente o que estava fazendo - reconstrói o ponto exato a partir do NORTE.md e do git, não da memória
---

# Recuperar o foco

Depois de uma compactação, o resumo da conversa parece completo — e é aí que mora o perigo. Detalhes somem, e você preenche o buraco com o que parece plausível. Esta skill reconstrói o ponto exato a partir de fontes, não da memória.

**Anuncie:** "Usando onedirection:recovering-focus pra retomar de onde paramos."

## A Regra

```
NÃO CONTINUE NENHUMA TAREFA ATÉ TER RECONSTRUÍDO O PONTO EXATO A PARTIR DE FONTES
```

O resumo da compactação é uma pista, não uma fonte.

## Checklist

1. **NORTE.md** — leia "Foco agora" e "Estado". (Sem NORTE.md: pule pra 2 e, ao final, sugira `onedirection:mapping-existing-project`.)
2. **Git** — o que realmente mudou:
   ```bash
   git status --short
   git diff --stat
   git log --oneline -10
   ```
3. **Tarefas** — se houver lista de tarefas na sessão, quais estão abertas.
4. **Cruzar** — o "Foco agora" bate com o que o git mostra? O resumo da compactação bate com os dois?
5. **Declarar** ao usuário, antes de qualquer ação:

```
Retomando:
- Foco: <do NORTE.md>
- Feito até aqui: <do git, com arquivos>
- Próximo passo: <um só>
- Divergência: <se o resumo, o NORTE.md e o git discordam, diga onde — ou "nenhuma">
```

6. **Divergência** → pergunte qual vale antes de continuar. **Sem divergência** → continue no próximo passo.

## Sinais de alerta

| Pensamento | Realidade |
|---|---|
| "O resumo diz que eu tinha terminado X" | Resumo não é prova. O git diz? |
| "Lembro que a função se chamava Y" | Memória pós-compactação inventa. Abra o arquivo. |
| "Vou só continuar de onde parei" | Você não sabe onde parou. É isso que esta skill descobre. |
| "É óbvio o próximo passo" | Então custa 3 comandos confirmar. Rode. |
