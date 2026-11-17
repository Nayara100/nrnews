#!/usr/bin/env python3
"""Posta um criativo no Instagram do NR News pela API oficial da Meta.

Uso: python3 automacao/postar_instagram.py criativos/AAAA-MM-DD-titulo.png
     python3 automacao/postar_instagram.py criativos/AAAA-MM-DD-titulo.mp4   (Reels)

A legenda vem do .txt com o mesmo nome. A imagem precisa já estar publicada
no site (o Instagram busca pelo link público), então rode depois do push:
o script espera a Vercel publicar a imagem antes de postar.

Precisa das variáveis de ambiente INSTAGRAM_ACCESS_TOKEN e INSTAGRAM_USER_ID.
"""
import json, os, sys, time, urllib.error, urllib.parse, urllib.request

SITE = "https://nrnews.vercel.app"
API = "https://graph.instagram.com"

def chamar(metodo, caminho, **params):
    params["access_token"] = os.environ["INSTAGRAM_ACCESS_TOKEN"]
    dados = urllib.parse.urlencode(params)
    if metodo == "GET":
        req = urllib.request.Request(f"{API}/{caminho}?{dados}")
    else:
        req = urllib.request.Request(f"{API}/{caminho}", data=dados.encode(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        erro = json.load(e).get("error", {})
        # nunca imprime o token: só a mensagem de erro da API
        sys.exit(f"erro da API do Instagram ({erro.get('code')}): {erro.get('message')}")

def esperar_arquivo(url, tipo, limite=600):
    fim = time.time() + limite
    while time.time() < fim:
        try:
            with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=30) as r:
                if r.status == 200 and r.headers.get("Content-Type", "").startswith(tipo):
                    return
        except urllib.error.URLError:
            pass
        time.sleep(15)
    sys.exit(f"o arquivo não ficou disponível no site em {limite}s: {url}")

def main():
    arquivo = sys.argv[1].lstrip("./")
    legenda = open(os.path.splitext(arquivo)[0] + ".txt", encoding="utf-8").read().strip()
    uid = os.environ["INSTAGRAM_USER_ID"]
    url = f"{SITE}/{urllib.parse.quote(arquivo)}"
    video = arquivo.lower().endswith(".mp4")

    esperar_arquivo(url, "video/" if video else "image/")
    if video:
        midia = dict(media_type="REELS", video_url=url, share_to_feed="true")
    else:
        midia = dict(image_url=url)
    container = chamar("POST", f"{uid}/media", caption=legenda, **midia)["id"]
    # vídeo demora mais para o Instagram processar
    for _ in range(120 if video else 30):
        status = chamar("GET", container, fields="status_code").get("status_code")
        if status == "FINISHED":
            break
        if status in ("ERROR", "EXPIRED"):
            sys.exit(f"o Instagram não processou o arquivo (status {status})")
        time.sleep(5)
    post = chamar("POST", f"{uid}/media_publish", creation_id=container)["id"]
    link = chamar("GET", post, fields="permalink").get("permalink", "")
    print("postado no Instagram:", link or post)

if __name__ == "__main__":
    main()
