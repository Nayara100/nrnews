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
| `automacao/postar_instagram.py` | Posta um criativo no Instagram pela API da Meta (usa `INSTAGRAM_ACCESS_TOKEN` e `INSTAGRAM_USER_ID` do ambiente). |
| `automacao/CRIAR_ROTINA.md` | Roteiro para criar a rotina agendada numa conta do Claude. |
| `criativos/modelo.html` | Modelo visual do post do Instagram (1080×1350). |
| `criativos/gerar.py` | Transforma o modelo em PNG. |
| `criativos/fontes/` | Fonte Poppins (licença OFL). O criativo não depende de internet. |
| `criativos/AAAA-MM-DD-*.png/.txt` | Criativos e legendas já gerados. Ficam públicos em `nrnews.vercel.app/criativos/...`. |

A rotina agendada fica na conta do Claude da Nayara (claude.ai/code/routines), às 8h, 13h e 18h
de Brasília (`0 11,16,21 * * *` em UTC). Ela publica no site **e** no Instagram.

## Regras de ouro

1. **Antes de mexer:** `git pull`. A rotina também faz commits na `main`.
2. **Nunca** coloque as notícias de volta dentro do `index.html`. O site precisa continuar lendo
   `noticias.json`, senão a rotina publica e o site não mostra.
3. **Nunca** imprima, peça no chat ou grave em arquivo o `INSTAGRAM_ACCESS_TOKEN`.
4. **Nada vai para o Instagram sem a pessoa confirmar no chat.** Post publicado não pode ser editado
   nem apagado pela API, só pelo app. Mostre o criativo e a legenda antes.
5. Não rode a rotina manualmente ("run now") perto de um horário agendado (8h, 13h, 18h): gera
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
Edite `criativos/modelo.html`. O @ do rodapé está em `<span>@nrnews</span>` (a conta real é
`@_nrnews`). Cores das editorias: objeto `ED` no script. Depois **gere uma imagem de teste**
(`python3 criativos/gerar.py /tmp/teste.png --ed Economia --date 2026-01-01 --title "Título de teste com tamanho real" --lead "Resumo de teste com duas frases." --src "Fonte"`)
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
