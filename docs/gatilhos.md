# Quando cada skill entra

Matriz de referência pra quem usa e pra quem mexe nas skills. As skills seguem esta tabela; se ela e uma skill discordarem, a skill está errada.

## Matriz

| Situação | Skill | Ação obrigatória | Exemplo | Exceção |
|---|---|---|---|---|
| Pasta vazia + ideia de projeto | `capturing-the-vision` | Entrevistar e gravar o `NORTE.md` antes de qualquer código | "quero criar um app de lista de compras" | Usuário dispensa perguntas: grava um `NORTE.md` mínimo com o que ele disse e segue |
| Tem código, sem `NORTE.md`, pedido de **direção** | `mapping-existing-project` | Ler docs, git e código; rascunho com fonte; confirmar antes de gravar | "me ajuda a decidir a próxima funcionalidade" | — |
| Tem código, sem `NORTE.md`, pedido **pontual** | nenhuma (nível rápido) | Fazer; oferecer o mapeamento em 1 linha, uma vez | "corrige esse erro de digitação" | — |
| Ideia nova do usuário que serve à promessa | `guarding-the-direction` (silenciosa) | Fazer; registrar em "Decisões" | "adiciona um contador de dias seguidos" | — |
| Pedido que bate num trecho do `NORTE.md` | `guarding-the-direction` | Parar antes de codar; citar o trecho; 3 opções | "adiciona um feed com curtidas" quando o norte diz "não é rede social" | Sem trecho pra citar, não é conflito: volta pra linha de cima |
| Ideia do usuário que não tem a ver com a promessa | `guarding-the-direction` | Perguntar em 1 linha se é parte do projeto | "faz um gerador de memes" num app de flashcards | Respondeu que é parte: segue como evolução |
| O próprio agente quer fazer algo não pedido | `guarding-the-direction` | Não fazer; anotar em "Depois" ou perguntar | refatorar o arquivo "já que está aberto" | — |
| Pedido novo com trabalho pela metade | `guarding-the-direction` | Perguntar "pauso ou termino antes?" | git sujo + "agora faz a tela de login" | Sem trabalho pendente: só troca o "Foco agora" |
| Prestes a dizer "pronto", "funciona", "corrigi", ou a commitar | `verifying-before-done` | Prova nova, pedido relido, `git diff` conferido | qualquer fim de tarefa com código | Impossível verificar: "Não verifiquei: X — porque Y" |
| Contexto compactado, sessão retomada, "você se perdeu" | `recovering-focus` | Reconstruir pelo `NORTE.md` e pelo git; declarar antes de agir | "continua de onde a gente parou" | — |
| "Onde estamos?", "quanto falta?", fim de etapa | `checking-progress` | Verificar cada item do v1 no código, com evidência | "quanto falta pro v1?" | — |
| Fora de projeto (sem git, sem manifesto, pasta pessoal) | nenhuma | Responder normalmente | "quanto é 15% de 80?" | Se a conversa virar "vamos criar um projeto aqui": `capturing-the-vision` |

## Perguntas difíceis

**Quando uma mudança é "só um bug"?** Quando o comportamento esperado já está decidido (no `NORTE.md`, no código ou no pedido) e o código não faz isso. Se consertar exige decidir *o que* o produto deve fazer, não é bug: é nível normal.

**Evolução ou mudança de escopo?** Evolução serve à promessa e não contradiz nada escrito. Mudança de escopo contradiz um trecho que dá pra citar (não-objetivo, decisão, promessa, público, stack). Na dúvida: evolução.

**O que é um projeto "novo"?** Pasta vazia, ou só com arquivos que não são código (anotações, imagens). Tem código e não tem `NORTE.md`: é projeto em andamento → mapeamento.

**E em monorepo?** O `NORTE.md` é procurado primeiro na pasta onde o Claude foi aberto, depois na raiz do git. Um norte por pacote: coloque o `NORTE.md` na pasta do pacote e abra o Claude nela. Um norte pro repositório inteiro: na raiz.

**E em worktree?** Funciona igual: o `NORTE.md` é versionado e vai junto, e o `.git` em forma de arquivo é reconhecido.

**Quando usar `checking-progress` sem o usuário pedir?** Ao fechar um item do v1 ou uma etapa grande, e quando o "Estado" do `NORTE.md` parecer não bater com o git. Não a cada tarefa pequena.
