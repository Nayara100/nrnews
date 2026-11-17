# Músicas dos Reels

Trechos de 40 s de músicas de Kevin MacLeod (incompetech.com), licença
[Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/).
Podem ser usadas em posts e anúncios, desde que haja crédito. O `automacao/reels.py` coloca o
crédito sozinho no fim do vídeo, embaixo da fonte:

    Música: "<nome>", Kevin MacLeod (incompetech.com), CC BY 4.0

Para incluir uma música nova: use só faixas com licença que permita uso comercial,
corte um trecho animado de 40 s (`ffmpeg -ss <início> -t 40 -i original.mp3 -b:a 160k nome.mp3`)
e acrescente no `musicas.json`.
