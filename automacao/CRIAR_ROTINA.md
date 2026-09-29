# Criar a rotina do NR News numa conta do Claude

Instruções para o **Claude Code** criar, na conta de quem está usando, a rotina na nuvem que publica
notícias no site e no Instagram 3 vezes por dia. Siga os passos na ordem e confirme cada decisão com
a pessoa antes de criar ou rodar qualquer coisa.

## Passo 0 — Conferir o que precisa existir antes

Pergunte à pessoa e só continue quando as três respostas forem "sim":

1. O GitHub `Nayara100` está conectado nesta conta do Claude (claude.ai/code) e o repositório
   `Nayara100/nrnews` aparece na lista de repositórios?
2. Existe um ambiente de nuvem com **Network access = Full** (acesso total à internet)?
3. Nesse ambiente estão cadastradas as variáveis `INSTAGRAM_ACCESS_TOKEN` e `INSTAGRAM_USER_ID`
   (sem `<` `>`, sem aspas, sem espaços)?

Se algo faltar, explique como fazer em claude.ai/code (editar o ambiente → Network access /
Environment variables) e espere. **Nunca peça para a pessoa colar o token no chat.**

## Passo 1 — Carregar a ferramenta de rotinas

Use a skill `/schedule` (ou carregue a ferramenta `RemoteTrigger`). Liste as rotinas existentes
(`action: "list"`) e verifique se já existe alguma com "NR News" no nome, para não criar duplicada.
Pegue na listagem de ambientes o `environment_id` do ambiente do passo 0 e confirme com a pessoa.

## Passo 2 — Verificar o ambiente antes de criar a rotina

Crie uma rotina **de uma vez só** (`run_once_at` alguns minutos no futuro, `enabled: false`) chamada
"NR News: verificação", no repositório `https://github.com/Nayara100/nrnews`, com
`allowed_tools: ["Bash", "Read"]` e este prompt:

```
Execução SOMENTE DE VERIFICAÇÃO. Não altere arquivos, não faça commit, não publique nada.
NUNCA imprima o valor de INSTAGRAM_ACCESS_TOKEN. Responda com uma tabela OK/FALHOU:
1. INSTAGRAM_ACCESS_TOKEN e INSTAGRAM_USER_ID definidas (mostre só o comprimento do token e o user_id).
2. curl -s "https://graph.instagram.com/me?fields=user_id,username,account_type&access_token=$INSTAGRAM_ACCESS_TOKEN" — mostre username e se user_id bate.
3. curl -s "https://graph.instagram.com/$INSTAGRAM_USER_ID/content_publishing_limit?fields=quota_usage,config&access_token=$INSTAGRAM_ACCESS_TOKEN"
4. Código HTTP de https://www.metropoles.com/ e de https://nrnews.vercel.app/
5. python3 criativos/gerar.py /tmp/t.png --ed Economia --date 2026-01-01 --title Teste --lead Teste --src Teste — gerou 1080x1350?
6. git push --dry-run origin HEAD:main — autenticação ok?
```

Depois de criar, remova os conectores (`update` com `{"clear_mcp_connections": true}`), rode
(`action: "run"`), espere ~1 minuto e leia o resultado com `list_runs` + `get_run_log`.
Mostre a tabela à pessoa. **Se algum item falhar, pare e ajude a corrigir antes de seguir.**

## Passo 3 — Criar a rotina principal

Mostre a configuração abaixo à pessoa, peça confirmação e crie com `action: "create"`:

- **name:** `NR News: notícia + criativo + Instagram (8h, 13h, 18h)`
- **cron_expression:** `0 11,16,21 * * *` (UTC = 8h, 13h e 18h em Brasília)
- **enabled:** `true`
- **environment_id:** o do passo 1
- **model:** `claude-sonnet-5-5`
- **sources:** `[{"git_repository": {"url": "https://github.com/Nayara100/nrnews"}}]`
- **allowed_tools:** `["Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebFetch", "WebSearch"]`
- **prompt** (mensagem do evento, `role: "user"`), exatamente:

```
Você é o redator automático do portal NR News (https://nrnews.vercel.app).

Siga à risca TODOS os passos de `AUTOMACAO.md`, na raiz deste repositório: busque 1 notícia nova na(s) fonte(s) indicada(s) lá, escreva-a do zero seguindo as regras de redação, publique com `automacao/publicar.py`, confira o criativo gerado, faça commit e push na branch `main` (`git push origin HEAD:main`) e poste no Instagram com `automacao/postar_instagram.py`.

Regras importantes:
- Leia `AUTOMACAO.md` e `noticias.json` antes de qualquer coisa.
- Nunca imprima o valor de INSTAGRAM_ACCESS_TOKEN.
- Se não houver notícia nova e relevante, não faça commit nem post.
- Se o criativo sair com fonte errada ou texto cortado, não poste no Instagram.
- Se o push ou a postagem falhar, não tente em loop: registre o erro.

No final, responda com um resumo: título publicado, link da matéria original, caminho do criativo, hash do commit e link do post no Instagram (ou o motivo de algo não ter sido feito).
```

Logo após criar, remova os conectores anexados automaticamente
(`update` com `{"clear_mcp_connections": true}`) — a rotina não usa nenhum.

## Passo 4 — Evitar publicação em dobro

Avise a pessoa, com destaque: **a rotina antiga, na conta do Matheus, precisa ser pausada** antes do
próximo horário (8h, 13h ou 18h). Se as duas ficarem ativas, cada horário publica duas notícias e
dois posts no Instagram. Pergunte se isso já foi combinado.

**Não** rode a rotina principal manualmente ("run now") se a rotina antiga ainda estiver ativa e
tiver rodado há menos de 1 hora — isso também gera post duplicado.

## Passo 5 — Resumo final

Mostre à pessoa: nome da rotina, horários em Brasília, próxima execução, link
`https://claude.ai/code/routines/<ID>`, e lembre que:
- fontes, quantidade e estilo se mudam editando `AUTOMACAO.md` no repositório;
- o token do Instagram vence a cada ~60 dias e precisa ser trocado na variável do ambiente;
- a rotina de verificação do passo 2 fica desativada e pode ser excluída em claude.ai/code/routines.
