#!/usr/bin/env python3
"""Gera um Reels (vídeo vertical 1080x1920 com música) e a legenda dele.

Uso: python3 automacao/reels.py reels.json

reels.json:
{
  "ed": "Negócios", "date": "2026-11-17", "src": "Confi e E-Commerce Brasil",
  "titulo": "Black Friday deve faturar R$ 13,3 bi",   # só para o nome do arquivo
  "cenas": [                                          # 2 a 4 cenas; o fechamento entra sozinho
    {"tipo": "gancho", "texto": "Quanto o Brasil vai gastar na Black Friday?"},
    {"tipo": "numero", "antes": "Só no e-commerce", "valor": 13.3, "casas": 1,
     "prefixo": "R$ ", "sufixo": " bi", "depois": "é a previsão de faturamento", "nota": "opcional"},
    {"tipo": "barras", "titulo": "Comparado com 2025", "selo": "+20,7%",
     "itens": [{"rotulo": "2025", "valor": 11.03, "texto": "R$ 11,0 bi"},
               {"rotulo": "2026", "valor": 13.3, "texto": "R$ 13,3 bi"}]},
    {"tipo": "texto", "texto": "Uma frase curta com o contexto."}
  ],
  "legenda": "...",                                   # legenda do post, sem o crédito da música
  "musica": "Pump"                                    # opcional; sem ela, as músicas se revezam
}

Gera criativos/AAAA-MM-DD-reels-<titulo>.mp4 e .txt (legenda + crédito da música).
"""
import glob, json, os, subprocess, sys, tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from publicar import EDITORIAS, slug  # noqa: E402

TIPOS = {"gancho", "numero", "barras", "texto"}

def main():
    dados = json.load(open(sys.argv[1], encoding="utf-8"))
    for k in ("ed", "date", "src", "titulo", "cenas", "legenda"):
        if not dados.get(k):
            sys.exit(f"campo obrigatório ausente: {k}")
    if dados["ed"] not in EDITORIAS:
        sys.exit(f"editoria inválida: {dados['ed']}")
    for c in dados["cenas"]:
        if c.get("tipo") not in TIPOS:
            sys.exit(f"tipo de cena inválido: {c.get('tipo')} (use um de: {', '.join(sorted(TIPOS))})")

    pasta = os.path.join(RAIZ, "reels", "musicas")
    musicas = json.load(open(os.path.join(pasta, "musicas.json"), encoding="utf-8"))
    if dados.get("musica"):
        musica = next((m for m in musicas if m["nome"].lower() == dados["musica"].lower()), None)
        if not musica:
            sys.exit(f"música desconhecida: {dados['musica']} (use uma de: {', '.join(m['nome'] for m in musicas)})")
    else:
        # revezamento: cada Reels novo usa a próxima música da lista
        musica = musicas[len(glob.glob(os.path.join(RAIZ, "criativos", "*-reels-*.txt"))) % len(musicas)]

    base = os.path.join(RAIZ, "criativos", f"{dados['date']}-reels-{slug(dados['titulo'])}")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False)
    subprocess.run(["node", os.path.join(RAIZ, "reels", "gerar.js"), f.name, base + ".mp4",
                    os.path.join(pasta, musica["arquivo"])], check=True)
    os.unlink(f.name)

    # o crédito da música (exigido pela licença CC BY) vai antes das hashtags
    legenda = dados["legenda"].strip()
    credito = f'Música: "{musica["nome"]}", Kevin MacLeod (incompetech.com), CC BY 4.0'
    partes = legenda.rsplit("\n\n", 1)
    if len(partes) == 2 and partes[1].lstrip().startswith("#"):
        legenda = f"{partes[0]}\n{credito}\n\n{partes[1]}"
    else:
        legenda = f"{legenda}\n\n{credito}"
    open(base + ".txt", "w", encoding="utf-8").write(legenda + "\n")

    print("reels:", os.path.relpath(base + ".mp4", RAIZ))
    print("música:", musica["nome"])
    print("legenda:", os.path.relpath(base + ".txt", RAIZ))

if __name__ == "__main__":
    main()
