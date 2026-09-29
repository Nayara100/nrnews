# Automação de notícias do NR News

Este arquivo é o manual da rotina automática. A cada execução, siga **todos** os passos abaixo.
Para mudar fontes, estilo ou quantidade, edite só este arquivo.

## Configuração

- **Fontes:** as da tabela abaixo (use os feeds RSS: são mais rápidos e mostram a data de cada matéria).
- **Notícias por execução:** 1
- **Editorias aceitas:** Negócios, Marketing, Economia, Política
- **Fuso horário:** America/Sao_Paulo (use a data de hoje nesse fuso)

## Fontes

| Fonte | Foco | Feed RSS | Nome em `src` |
|---|---|---|---|
| Metrópoles | Economia e negócios no Brasil | https://www.metropoles.com/brasil/feed e https://www.metropoles.com/brasil/economia-br/feed | Metrópoles |
| g1 Economia | Economia, emprego, consumo | https://g1.globo.com/rss/g1/economia/ | g1 |
| Valor Econômico | Empresas, mercado, finanças | https://valor.globo.com/rss/valor | Valor Econômico |
| InfoMoney | Mercado, investimentos, empresas | https://www.infomoney.com.br/feed/ | InfoMoney |
| Folha Mercado | Economia e mercado | https://feeds.folha.uol.com.br/mercado/rss091.xml | Folha de S.Paulo |
| Meio & Mensagem | Marketing, publicidade, mídia | https://www.meioemensagem.com.br/feed | Meio & Mensagem |
| Propmark | Marketing, publicidade, agências | https://propmark.com.br/feed/ | Propmark |
| Exame | Negócios, empresas, carreira | https://exame.com/feed/ | Exame |
| NeoFeed | Negócios, investimentos, startups | https://neofeed.com.br/feed/ | NeoFeed |
| Startups.com.br | Startups e inovação | https://startups.com.br/feed/ | Startups |
| Agência Brasil | Dados oficiais (IBGE, BC, governo) | https://agenciabrasil.ebc.com.br/rss/economia/feed.xml | Agência Brasil |

Como escolher entre elas:
- Leia os feeds de todas as fontes e junte as matérias das últimas 24h num só lugar antes de escolher.
- **Varie a editoria:** veja as 3 notícias mais recentes de `noticias.json`. Se nenhuma for de Marketing,
  prefira uma de Marketing (Meio & Mensagem ou Propmark) quando houver uma boa. Não publique três
  seguidas da mesma editoria se houver alternativa relevante.
- **Varie a fonte:** entre matérias de relevância parecida, prefira uma fonte diferente da usada na
  notícia mais recente.
- Se o mesmo fato aparece em várias fontes, escolha a matéria mais completa e confira os números
  numa segunda fonte. Se as fontes divergirem num número, deixe esse número de fora.
- Se a matéria estiver bloqueada por paywall e você não conseguir ler os fatos completos, use outra
  fonte sobre o mesmo fato ou escolha outra notícia.
- Ignore conteúdo patrocinado (ex.: links com `conteudo-especial`, "publieditorial", "oferecido por").
- Se um feed não abrir, siga com os outros e cite a falha no resumo final.

## O que o NR News publica

Portal de negócios, marketing, economia e política econômica para quem empreende ou trabalha com
marketing. Prefira notícias sobre empresas, mercado, consumo, publicidade, indicadores econômicos
(juros, inflação, emprego, dólar), regulação que afeta negócios e tecnologia aplicada a negócios.

**Não publique:** crimes, polícia, fofoca, celebridades sem ligação com marcas, esportes, clima,
política partidária ou eleitoral, tragédias, e matérias opinativas ou de colunistas.

## Passo a passo

1. **Prepare o ambiente:** o `criativos/gerar.py` usa sozinho o Chromium que já vem instalado em
   `/opt/pw-browsers`. Só se ele falhar por falta de navegador, rode
   `pip install playwright && python3 -m playwright install --with-deps chromium`.
2. **Veja o que já foi publicado:** leia `noticias.json`. Nunca publique uma matéria cujo `url`
   já esteja lá, nem outra matéria sobre o mesmo fato.
3. **Busque nas fontes:** leia os feeds da seção "Fontes". Escolha a matéria mais relevante e
   **recente** (publicada nas últimas 24h) que se encaixe nas editorias, seguindo as regras de
   variedade. Abra a matéria e anote os fatos e números.
4. **Se nada relevante e novo tiver sido publicado, pare aqui** sem fazer commit. É melhor não
   publicar do que publicar algo fraco ou repetido.
5. **Escreva a notícia** num arquivo temporário `nova.json` (formato em `automacao/publicar.py`):
   - `title`: até ~70 caracteres, direto, com o fato principal.
   - `lead`: 1 frase que complementa o título.
   - `body`: 1 ou 2 parágrafos curtos, com números e contexto e, se couber, o que muda na prática.
   - `src`: nome do veículo, como na coluna "Nome em `src`" (ex.: "Meio & Mensagem"). Se o dado
     for de um órgão citado na matéria, use "Órgão, via Veículo" (ex.: "IBGE, via g1").
   - `url`: link da matéria original.
   - `criativo.title`: versão curta do título para o Instagram, com **até 50 caracteres**.
   - `criativo.lead`: 1 ou 2 frases, com **até 130 caracteres**.
   - `legenda`: legenda do Instagram no formato abaixo.
6. **Publique:** `python3 automacao/publicar.py nova.json`. Isso adiciona a notícia no topo
   de `noticias.json` e gera `criativos/AAAA-MM-DD-titulo.png` e `.txt`.
   Se sair com código 3, a matéria já existe: volte ao passo 3 e escolha outra, ou pare.
7. **Confira o criativo:** abra o PNG gerado e verifique se o texto não está cortado nem
   sobreposto, se o rodapé (fonte e @nrnews) aparece inteiro e se a fonte é a Poppins
   (arredondada, como nos criativos anteriores), e não Arial/Helvetica. Se algo disso falhar
   depois de uma nova tentativa, **não poste no Instagram**: faça o commit só da notícia no site
   e explique o problema no resumo. Se estiver, encurte `criativo.title`/`criativo.lead`, desfaça as mudanças
   (`git checkout -- noticias.json && git clean -fd criativos/`) e rode de novo.
8. **Commit e push** direto na branch `main` (a Vercel publica o site sozinha):
   `git add noticias.json criativos/ && git commit -m "Publica notícia: <título curto>" && git push origin HEAD:main`
   (use `HEAD:main`: o repositório pode vir com o HEAD solto).
   Não commite o `nova.json`.
9. **Poste no Instagram:** `python3 automacao/postar_instagram.py criativos/AAAA-MM-DD-titulo.png`
   (o PNG gerado no passo 6). O script espera a Vercel publicar a imagem e posta com a legenda do
   `.txt`. Se ele falhar, **não tente de novo em loop**: registre o erro no resumo final. Se o erro
   for de token (código 190), avise no resumo que o token do Instagram precisa ser renovado.
10. **Resumo final:** título publicado, link da fonte, caminho do criativo e link do post no
    Instagram — ou o motivo de não ter publicado.

## Regras de redação (obrigatórias)

- **Escreva do zero.** Não copie nem parafraseie frases da matéria original: use só os fatos.
- Linguagem simples e direta, frases curtas, sem jargão e sem adjetivos de efeito.
- **Nunca invente ou arredonde dados.** Se um número estiver ambíguo na fonte, deixe-o de fora.
- Valores em reais com espaço: "R$ 3.777". Porcentagem com vírgula: "5,3%".
- Sempre cite a fonte e mantenha o `url` original.

## Formato da legenda do Instagram

```
<gancho em 1 frase com o fato principal> <1 emoji opcional>

<2 ou 3 frases com os números e o contexto>

Fonte: <src>
Leia mais em nrnews.vercel.app

#<editoria> #<2 a 3 hashtags do tema> #nrnews
```
