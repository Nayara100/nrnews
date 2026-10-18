#!/usr/bin/env python3
"""Gera o PNG (1080x1350) de um criativo a partir do modelo.html.

Uso: python3 criativos/gerar.py saida.png --ed Economia --date 2026-09-29 \
       --title "..." --lead "..." --src "..." [--img foto.jpg --credito "Nome/Agência Brasil" --v A]

Com --img, sai o layout com foto: A (foto em cima) ou B (foto de fundo).
Sem foto, --tema usa uma ilustração própria de criativos/ilustracoes/ (layout A, sem crédito).

Usa o Google Chrome/Chromium instalado; se não houver, usa o Playwright
(pip install playwright && python3 -m playwright install --with-deps chromium).
No ambiente de nuvem do Claude, usa o Chromium que já vem em /opt/pw-browsers.
"""
import argparse, glob, os, shutil, subprocess, tempfile, urllib.parse

CAMPOS = ("ed", "date", "title", "lead", "src")
OPCIONAIS = ("img", "credito", "v", "tema")
PASTA = os.path.dirname(os.path.abspath(__file__))
ILUSTRACOES = os.path.join(PASTA, "ilustracoes")
CORES = {"Negócios": "#c4a0f5", "Marketing": "#ff78be", "Economia": "#40c48c", "Política": "#6fa8ff", "Mundo": "#5ad2eb"}  # = ED no modelo.html

def temas():
    return sorted(f[:-4] for f in os.listdir(ILUSTRACOES) if f.endswith(".svg"))

def ilustracao(tema, ed):
    """Copia a ilustração do tema pintada com a cor da editoria. Devolve o caminho ou None."""
    arq = os.path.join(ILUSTRACOES, f"{tema}.svg")
    if not os.path.exists(arq):
        return None
    svg = open(arq, encoding="utf-8").read().replace("ACCENT", CORES.get(ed, CORES["Negócios"]))
    saida = os.path.join(tempfile.mkdtemp(prefix="nrilu-"), f"{tema}.svg")
    open(saida, "w", encoding="utf-8").write(svg)
    return saida
CHROMES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    # Chromium que já vem instalado no ambiente de nuvem do Claude. O headless shell
    # respeita o tamanho exato da janela; o chrome comum cortava o rodapé lá.
    *sorted((f for f in glob.glob("/opt/pw-browsers/chromium_headless_shell-*/**/*", recursive=True)
             if os.path.basename(f) in ("headless_shell", "chrome-headless-shell") and os.access(f, os.X_OK)),
            reverse=True),
    *sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"), reverse=True),
    shutil.which("google-chrome") or "", shutil.which("chromium") or "", shutil.which("chromium-browser") or "",
]

def gerar(saida, dados):
    modelo = os.path.join(PASTA, "modelo.html")
    params = {k: dados[k] for k in CAMPOS}
    if not dados.get("img") and dados.get("tema"):
        ilu = ilustracao(dados["tema"], dados["ed"])
        if ilu:
            dados = {**dados, "img": ilu, "credito": "", "v": "A"}
    if dados.get("img"):
        params["img"] = "file://" + urllib.parse.quote(os.path.abspath(dados["img"]))
        params["credito"] = dados.get("credito") or ""
        params["v"] = dados.get("v") or "A"
    url = "file://" + urllib.parse.quote(modelo) + "?" + urllib.parse.urlencode(params)
    saida = os.path.abspath(saida)
    chrome = next((c for c in CHROMES if c and os.path.exists(c)), None)
    if chrome:
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                        "--allow-file-access-from-files", "--force-device-scale-factor=1", "--window-size=1080,1350",
                        "--virtual-time-budget=5000", "--screenshot=" + saida, url],
                       check=True, capture_output=True)
    else:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.goto(url)
            pg.wait_for_selector("body[data-ready='1']", timeout=15000)
            pg.screenshot(path=saida)
            b.close()
    return saida

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("saida")
    for k in CAMPOS:
        ap.add_argument("--" + k, required=True)
    for k in OPCIONAIS:
        ap.add_argument("--" + k)
    a = ap.parse_args()
    print(gerar(a.saida, vars(a)))

if __name__ == "__main__":
    main()
