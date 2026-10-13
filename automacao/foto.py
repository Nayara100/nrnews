#!/usr/bin/env python3
"""Baixa a foto principal de uma matéria da Agência Brasil ou da Agência Senado.

Uso: python3 automacao/foto.py <url da matéria> [saida.jpg]

Só aceita foto de fotógrafo da própria agência (crédito "Nome/Agência Brasil" ou
"Nome/Agência Senado"). Foto da Reuters, de campanha, de divulgação ou com
"proibida reprodução" é recusada. As duas agências liberam o uso com crédito:
- Agência Brasil: "Reprodução autorizada para veículos de comunicação com fins
  jornalísticos, mediante indicação da fonte."
- Agência Senado: "A reprodução de matérias e fotografias é livre, desde que não
  haja descaracterização de conteúdo, mediante a citação da Agência Senado e do autor."

Imprime o caminho da foto e o crédito. Sai com código 4 se não houver foto liberada.
"""
import html, os, re, sys, tempfile, urllib.parse, urllib.request

AGENCIAS = {
    "agenciabrasil.ebc.com.br": "Agência Brasil",
    "www12.senado.leg.br": "Agência Senado",
}
PROIBIDO = re.compile(r"reuters|proibid|direitos reservados|divulga|arquivo|campanha|instagram|afp|\bap\b|getty", re.I)
MIN_BYTES = 40_000  # foto muito pequena fica borrada em 1080 px

def _baixar(url, tentativas=2):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (NRNews)"})
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except OSError:
            if i == tentativas - 1:
                raise

def _limpa(t):
    return re.sub(r"\s+", " ", html.unescape(t)).strip()

def achar(url):
    """Devolve (url_da_foto, credito) ou None."""
    host = urllib.parse.urlparse(url).netloc
    agencia = AGENCIAS.get(host)
    if not agencia:
        return None
    pag = _baixar(url).decode("utf-8", "ignore")
    og = re.search(r'property="og:image"\s+content="([^"]+)"', pag)
    if not og:
        return None
    foto = html.unescape(og.group(1))
    if agencia == "Agência Brasil":
        c = re.search(r"©\s*([^<\"]{3,90})", pag)  # crédito da foto principal
    else:
        c = re.search(r'credito="([^"]{3,90})"', pag)
    credito = _limpa(c.group(1)) if c else ""
    credito = re.sub(r"\s*/\s*", "/", credito)
    if not credito.endswith("/" + agencia) or PROIBIDO.search(credito):
        return None
    return foto, credito

def baixar(url, saida=None):
    """Baixa a foto liberada da matéria. Devolve (caminho, credito) ou None.
    Falha de rede nunca impede a publicação: sem foto, o criativo sai no layout sem foto."""
    try:
        achou = achar(url)
        if not achou:
            return None
        foto, credito = achou
        dados = _baixar(foto)
    except OSError as e:
        print("foto: falha ao baixar,", e, file=sys.stderr)
        return None
    if len(dados) < MIN_BYTES:
        return None
    saida = saida or os.path.join(tempfile.mkdtemp(prefix="nrfoto-"), "foto.jpg")
    open(saida, "wb").write(dados)
    return saida, credito

if __name__ == "__main__":
    r = baixar(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    if not r:
        print("sem foto liberada")
        sys.exit(4)
    print(r[0]); print(r[1])
