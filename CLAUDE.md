# NR News — guia para o Claude

Portal de notícias de negócios, marketing, economia e política econômica.
Site: https://nrnews.vercel.app · Instagram: @_nrnews · Repositório: Nayara100/nrnews.

**Se você é a rotina automática de publicação:** siga o `AUTOMACAO.md` e ignore a seção
"Receitas" abaixo. Ela é para quando alguém pede uma alteração pelo chat.

## Como o projeto funciona

Todo push na branch `main` publica o site sozinho na Vercel (1–2 min). Não existe build.

| Arquivo | O que é |
|---|---|
| `index.html` | O site inteiro (HTML + CSS + JS). Lê as notícias de `noticias.json` com `fetch`. |
| `noticias.json` | Lista de notícias, a mais recente primeiro. Campos: `ed`, `date` (AAAA-MM-DD), `title`, `lead`, `body` (lista de parágrafos), `src`, `url`. |
| `AUTOMACAO.md` | Manual que a rotina segue a cada execução: fontes, rodízio de editorias, regras de redação, formato da legenda. |
| `automacao/publicar.py` | Adiciona uma notícia em `noticias.json` e gera o criativo + legenda. Bloqueia `url` repetida. |
| `automacao/foto.py` | Baixa a foto de uma matéria da Agência Brasil ou da Agência Senado, só se o crédito for da própria agência. Usado pelo `publicar.py`. |
| `automacao/postar_instagram.py` | Posta um criativo (PNG) ou um Reels (MP4) no Instagram pela API da Meta (usa `INSTAGRAM_ACCESS_TOKEN` e `INSTAGRAM_USER_ID` do ambiente). |
| `automacao/reels.py` | Gera um Reels (vídeo 1080×1920 com música) e a legenda a partir de um JSON de cenas. |
| `reels/` | Modelo animado do Reels (`modelo.html`), gerador do vídeo (`gerar.js`, usa Playwright + ffmpeg) e músicas livres com crédito (`musicas/`). |
| `automacao/CRIAR_ROTINA.md` | Roteiro para criar a rotina agendada numa conta do Claude. |
| `criativos/modelo.html` | Modelo visual do post do Instagram (1080×1350): layout A (foto em cima), B (foto de fundo) e sem foto. |
| `criativos/gerar.py` | Transforma o modelo em PNG. |
| `criativos/ilustracoes/` | Ilustrações próprias por tema, usadas quando não há foto liberada. A cor (`ACCENT`) é trocada pela da editoria. |
| `criativos/fontes/` | Fonte Poppins (licença OFL). O criativo não depende de internet. |
| `criativos/AAAA-MM-DD-*.png/.txt` | Criativos e legendas já gerados. Ficam públicos em `nrnews.vercel.app/criativos/...`. O `.mp4` de um Reels fica no site só até ser postado; depois é apagado. |

A rotina agendada fica na conta do Claude da Nayara (claude.ai/code/routines), às 7h, 11h, 14h, 17h,
20h e 23h de Brasília (`0 2,10,14,17,20,23 * * *` em UTC). Ela publica no site **e** no Instagram.
Nas execuções das 11h e das 17h, a notícia vai só para o site e fica reservada para virar Reels, que
é feito às 11h40 e 17h40 numa conversa agendada e postado sozinho, sem aprovação (pedido da Nayara em 26/11/2026;
veja "Execuções de Reels" no `AUTOMACAO.md`).

## Regras de ouro

1. **Antes de mexer:** `git pull`. A rotina também faz commits na `main`.
2. **Nunca** coloque as notícias de volta dentro do `index.html`. O site precisa continuar lendo
   `noticias.json`, senão a rotina publica e o site não mostra.
3. **Nunca** imprima, peça no chat ou grave em arquivo o `INSTAGRAM_ACCESS_TOKEN`.
4. **Nada vai para o Instagram sem a pessoa confirmar no chat**, exceto as notícias da rotina e os Reels das 11h40 e 17h40,
   que a Nayara autorizou a postar sozinhos. Post publicado não pode ser editado
   nem apagado pela API, só pelo app. Mostre o criativo e a legenda antes.
5. Não rode a rotina manualmente ("run now") perto de um horário agendado (7h, 11h, 14h, 17h, 20h, 23h): gera
   notícia e post em dobro.
6. Mostre o que vai mudar (diff ou imagem) e peça confirmação antes do commit. Commits em português.
7. Push com `git push origin HEAD:main` (o checkout pode vir com o HEAD solto). Depois confirme que a
   Vercel publicou: abra https://nrnews.vercel.app e confira a mudança.

## Receitas (pedidos comuns pelo chat)

### Fontes, quantidade, editorias ou estilo das notícias
Edite **só** o `AUTOMACAO.md` (tabela "Fontes", seção "Configuração", "Regras de redação",
"Formato da legenda"). Vale a partir da próxima execução da rotina, sem mexer nela.
Para uma fonte nova, prefira o feed RSS e confira se ele abre (`curl -sI <feed>`).

### Horários da rotina
Os horários ficam na rotina, não no repositório. Use a skill `/schedule` (ação de update) ou mande a
pessoa em claude.ai/code/routines. Converta para UTC: Brasília = UTC−3 (ex.: 9h → `0 12 * * *`).
Intervalo mínimo entre execuções: 1 hora.

### Corrigir ou remover uma notícia do site
Edite a entrada em `noticias.json`, mantendo os campos e o formato. Valide antes do commit:
`python3 -c "import json;d=json.load(open('noticias.json'));print(len(d),'ok')"`.
Se a notícia já foi para o Instagram, avise que o post precisa ser editado ou apagado pelo app.

### Publicar uma notícia manualmente
1. Leia a matéria original e escreva do zero, seguindo as regras de redação do `AUTOMACAO.md`.
2. Monte `nova.json` (formato no topo de `automacao/publicar.py`) e rode
   `python3 automacao/publicar.py nova.json`.
3. Mostre o PNG gerado e a legenda (`.txt`). Com o ok da pessoa: commit + push.
4. Só depois do push, e com novo ok: `python3 automacao/postar_instagram.py criativos/<arquivo>.png`.
   As variáveis do Instagram só existem no ambiente de nuvem. Se não estiverem definidas, avise.
5. Não commite o `nova.json`.

### Refazer o criativo de uma notícia já publicada
Gere com um **nome novo** (ex.: sufixo `-v2`), porque o link antigo pode estar em cache:
`python3 criativos/gerar.py criativos/<nome>-v2.png --ed ... --date ... --title ... --lead ... --src ...`
Renomeie o `.txt` para combinar e remova o PNG antigo.

### Mudar o visual do criativo (cores, textos fixos, @ do rodapé, tamanhos)
Edite `criativos/modelo.html`. O @ do rodapé está em `<b>@_nrnews</b>`. As regras de quais fotos
podem ser usadas ficam no `AUTOMACAO.md` (seção "Fotos do criativo"). Cores das editorias: objeto `ED` no script. Depois **gere uma imagem de teste**
(`python3 criativos/gerar.py /tmp/teste.png --ed Economia --date 2026-01-01 --title "Título de teste com tamanho real" --lead "Resumo de teste com duas frases." --src "Fonte"`;
para testar com foto, acrescente `--img foto.jpg --credito "Nome/Agência Brasil" --v A` ou `--v B`)
e mostre à pessoa antes do commit. Mantenha as `@font-face` da Poppins local e o
`data-fonte`/`data-ready`, que a rotina usa para conferir o criativo.

### Mudar o site (layout, textos, seções)
Edite o `index.html`. Se a pessoa mandar um HTML novo pronto, feito em outro chat, use-o, mas
**religue as notícias**:
- troque o `const NEWS = [...]` por `let NEWS = [];`;
- troque a chamada final `render();` por
  `fetch("noticias.json",{cache:"no-cache"}).then(r=>r.json()).then(d=>{NEWS=d;render()});`;
- mantenha o link da fonte: `const fonte = n => n.url ? \`<a href="${n.url}" target="_blank" rel="noopener">${n.src}</a>\` : n.src;`,
  usando `fonte(n)` onde aparece `n.src`.

Se o HTML novo tiver notícias que ainda não estão no `noticias.json`, pergunte se devem ser
adicionadas. Para testar localmente: `python3 -m http.server 8765` e abra http://localhost:8765.

### Token do Instagram vencido (erro 190 / "token expirado")
O token dura cerca de 60 dias. Ele é gerado no painel da Meta for Developers (o app da automação fica na conta de
desenvolvedor do Matheus → Casos de uso → Instagram → Gerar token).
Depois, troque a variável `INSTAGRAM_ACCESS_TOKEN` no ambiente de nuvem, em claude.ai/code →
ambiente → Environment variables. Não há nada a mudar no repositório.

### Fazer um Reels
1. Escolha a notícia (nas execuções das 11h e 17h a rotina já reserva uma: commit `Publica notícia (Reels): ...`).
2. Monte `reels.json` (formato no topo de `automacao/reels.py`): gancho, número de destaque, comparação
   em barras e/ou uma frase de contexto, só com dados da notícia. Rode `python3 automacao/reels.py reels.json`.
3. Confira os quadros do vídeo. Commit + push só do `.mp4` e `.txt` (a partir de um worktree limpo da `main`),
   `python3 automacao/postar_instagram.py criativos/<arquivo>.mp4`, e depois apague o `.mp4` com outro commit.
4. Não commite o `reels.json`. A API não apaga posts: se precisar trocar, a pessoa apaga pelo app.
