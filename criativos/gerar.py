#!/usr/bin/env python3
"""Gera o PNG (1080x1350) de um criativo a partir do modelo.html.

Uso: python3 criativos/gerar.py saida.png --ed Economia --date 2026-09-29 \
       --title "..." --lead "..." --src "..."

Usa o Google Chrome/Chromium instalado; se não houver, usa o Playwright
(pip install playwright && python3 -m playwright install --with-deps chromium).
No ambiente de nuvem do Claude, usa o Chromium que já vem em /opt/pw-browsers.
"""
import argparse, glob, os, shutil, subprocess, urllib.parse

CAMPOS = ("ed", "date", "title", "lead", "src")
CHROMES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    # Chromium que já vem instalado no ambiente de nuvem do Claude
    *sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"), reverse=True),
    shutil.which("google-chrome") or "", shutil.which("chromium") or "", shutil.which("chromium-browser") or "",
]

def gerar(saida, dados):
    modelo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelo.html")
    url = "file://" + urllib.parse.quote(modelo) + "?" + urllib.parse.urlencode({k: dados[k] for k in CAMPOS})
    saida = os.path.abspath(saida)
    chrome = next((c for c in CHROMES if c and os.path.exists(c)), None)
    if chrome:
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                        "--force-device-scale-factor=1", "--window-size=1080,1350",
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
    a = ap.parse_args()
    print(gerar(a.saida, vars(a)))

if __name__ == "__main__":
    main()
