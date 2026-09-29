#!/usr/bin/env python3
"""Publica uma notícia nova: adiciona em noticias.json e gera criativo + legenda.

Uso: python3 automacao/publicar.py nova.json

nova.json:
{
  "ed": "Economia",                      # Negócios | Marketing | Economia | Política
  "date": "2026-09-29",
  "title": "...", "lead": "...", "body": ["...", "..."],
  "src": "Metrópoles", "url": "https://www.metropoles.com/...",
  "criativo": {"title": "...", "lead": "..."},   # versão curta para o Instagram
  "legenda": "..."                                # legenda do post
}

Sai com código 3 (sem alterar nada) se a matéria já foi publicada.
"""
import json, os, re, sys, unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "criativos"))
from gerar import gerar  # noqa: E402

EDITORIAS = {"Negócios", "Marketing", "Economia", "Política"}
MAX_NOTICIAS = 60  # o site mostra só as mais recentes

def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:50].rstrip("-")

def main():
    nova = json.load(open(sys.argv[1], encoding="utf-8"))
    for k in ("ed", "date", "title", "lead", "body", "src", "url", "criativo", "legenda"):
        if not nova.get(k):
            sys.exit(f"campo obrigatório ausente: {k}")
    if nova["ed"] not in EDITORIAS:
        sys.exit(f"editoria inválida: {nova['ed']}")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", nova["date"]):
        sys.exit("date deve estar no formato AAAA-MM-DD")

    arq = os.path.join(RAIZ, "noticias.json")
    noticias = json.load(open(arq, encoding="utf-8"))
    if any(n.get("url") == nova["url"] for n in noticias):
        print("já publicada:", nova["url"])
        sys.exit(3)

    base = os.path.join(RAIZ, "criativos", f"{nova['date']}-{slug(nova['criativo']['title'])}")
    gerar(base + ".png", {"ed": nova["ed"], "date": nova["date"], "src": nova["src"], **nova["criativo"]})
    open(base + ".txt", "w", encoding="utf-8").write(nova["legenda"].strip() + "\n")

    item = {k: nova[k] for k in ("ed", "date", "title", "lead", "body", "src", "url")}
    noticias = [item] + noticias
    json.dump(noticias[:MAX_NOTICIAS], open(arq, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(arq, "a", encoding="utf-8").write("\n")

    print("publicada:", item["title"])
    print("criativo:", os.path.relpath(base + ".png", RAIZ))
    print("legenda:", os.path.relpath(base + ".txt", RAIZ))

if __name__ == "__main__":
    main()
