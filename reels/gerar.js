// Gera o MP4 (1080x1920, 30 fps) de um Reels a partir do reels/modelo.html.
// Uso: node reels/gerar.js dados.json saida.mp4 [musica.mp3]
// Normalmente é chamado pelo automacao/reels.py, que escolhe a música e escreve a legenda.
const { chromium } = require("playwright");
const { spawn } = require("child_process");
const fs = require("fs"), path = require("path"), url = require("url");

const FPS = 30;
const [dadosArq, saida, musica] = process.argv.slice(2);

(async () => {
  const dados = JSON.parse(fs.readFileSync(dadosArq, "utf8"));
  const browser = await chromium.launch({ args: ["--allow-file-access-from-files"] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto(url.pathToFileURL(path.join(__dirname, "modelo.html")).href);
  await page.waitForSelector("body[data-ready='1']");
  if (await page.evaluate(() => document.body.dataset.fonte) !== "poppins") throw new Error("fonte Poppins não carregou");
  const total = await page.evaluate(d => window.cenas(d), dados);

  const audio = musica ? ["-ss", String(dados.musica_inicio || 0), "-t", String(total), "-i", musica] : [];
  const filtro = musica ? ["-af", `afade=t=in:d=0.3,afade=t=out:st=${total - 1.5}:d=1.5,loudnorm=I=-14:TP=-1.5`,
                           "-c:a", "aac", "-b:a", "192k", "-ar", "44100"] : ["-an"];
  const ff = spawn("ffmpeg", ["-v", "error", "-y", "-f", "image2pipe", "-framerate", String(FPS), "-i", "-", ...audio,
    "-map", "0:v", ...(musica ? ["-map", "1:a"] : []), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium",
    "-crf", "20", "-movflags", "+faststart", ...filtro, "-shortest", saida], { stdio: ["pipe", "inherit", "inherit"] });
  const fim = new Promise((ok, erro) => ff.on("close", c => c === 0 ? ok() : erro(new Error("ffmpeg saiu com " + c))));

  for (let i = 0, n = Math.round(total * FPS); i < n; i++) {
    await page.evaluate(t => window.quadro(t), i / FPS);
    const img = await page.screenshot({ type: "jpeg", quality: 92 });
    if (!ff.stdin.write(img)) await new Promise(r => ff.stdin.once("drain", r));
  }
  ff.stdin.end();
  await fim;
  await browser.close();
  console.log(saida, total.toFixed(1) + "s");
})().catch(e => { console.error("reels:", e.message); process.exit(1); });
