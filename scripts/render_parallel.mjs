// Parallel deterministic renderer: drives window.__setTime(t) per frame,
// split across 2 pages (2 CPUs). CLI:
//   node render_parallel.mjs <html-file> <duration-sec> <output-mp4> [fromSec] [toSec]
//
// fromSec/toSec (optional): render only that time range — for QA spot-checks
// (e.g. first 15s) without paying for a full render. Defaults: 0..duration.
//
// Design:
// - 1 browser (puppeteer, /opt/meta-chromium/chrome, headless new), 2 pages.
// - Frames split: page A = first half, page B = second half of the range.
//   __setTime(t) is stateless, so pages are independent — output is
//   deterministic and identical to serial.
// - setTime via ONE page.evaluate (no in-page waiting — requestAnimationFrame /
//   setTimeout freeze on background pages). Seek-waiting happens Node-side by
//   polling video.seeking (trivial evaluates work on background pages), and
//   page.screenshot() forces a fresh compositor frame per shot (verified).
// - Each page pipes JPEG to its own ffmpeg (preset veryfast, -threads 1 —
//   2 encoders on 2 CPUs must not oversubscribe; less CPU contention when
//   both encodes run together). Segments concatenated with -c copy
//   (no re-encode).
// - Seek fallback 1500ms -> 600ms + console.warn when used.
// - video.bgvid wait is conditional: skipped when the page has no bg video
//   (render_full.mjs would time out 30s on such pages).
// - Resource guards: --disable-dev-shm-usage (small /dev/shm in containers
//   crashes tabs), V8 heap cap 512MB, try/finally always closes the browser
//   and cleans tmp (no leaked Chromium/ffmpeg on failure).
//
// Requires: puppeteer resolvable from this script's directory.
// ESM ignores NODE_PATH, so either:
//   - symlink: ln -s <dir-with-puppeteer>/node_modules <skill>/node_modules
//     (e.g. ~/workspace/std-video/v2/node_modules), or
//   - npm install puppeteer inside the skill directory.
import puppeteer from 'puppeteer';
import { spawn, execFile } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import os from 'os';
import path from 'path';

const execFileAsync = promisify(execFile);

const HTML = path.resolve(process.argv[2] || '/home/hatch/workspace/std-video/v2/full.html');
const DUR = parseFloat(process.argv[3] || '60.575');
const OUT = process.argv[4] || '/home/hatch/workspace/std-video/v2/full-raw.mp4';
// Optional range (seconds) — QA spot-check without a full render.
const FROM_SEC = parseFloat(process.argv[5] || '0');
const TO_SEC = parseFloat(process.argv[6] || String(DUR));

const W = 1080, H = 1920, FPS = 24;
const N = Math.round(FPS * DUR);
const START_F = Math.max(0, Math.round(FROM_SEC * FPS));
const END_F = Math.min(N, Math.round(TO_SEC * FPS));
const MID = Math.ceil((START_F + END_F) / 2);
const FALLBACK_MS = 600;

if (END_F <= START_F) {
  console.error(`empty range: frames ${START_F}..${END_F}`);
  process.exit(1);
}

const children = []; // spawned ffmpeg handles, killed on failure

const browser = await puppeteer.launch({
  executablePath: '/opt/meta-chromium/chrome',
  headless: 'new',
  args: ['--no-sandbox', '--disable-gpu', '--window-size=1080,1920',
         '--force-device-scale-factor=1', '--hide-scrollbars',
         '--disable-dev-shm-usage', // /dev/shm too small in containers -> tab crash
         '--js-flags=--max-old-space-size=512'], // cap V8 heap per renderer
});
const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'rpar-'));

async function makePage() {
  const page = await browser.newPage();
  await page.setViewport({ width: W, height: H, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => console.log('PAGEERROR:', e.message));
  await page.goto('file://' + HTML);
  await page.evaluate(() => document.fonts.load('100px Anton').catch(() => {}));
  await page.waitForFunction(() => window.__tlReady === true, { timeout: 30000 });
  // only wait for bg video when the page actually has one
  const hasVideo = await page.evaluate(
    () => document.querySelectorAll('video.bgvid').length > 0);
  if (hasVideo) {
    await page.waitForFunction(() => {
      const vs = [...document.querySelectorAll('video.bgvid')];
      return vs.length >= 1 && vs.every((v) => v.readyState >= 2);
    }, { timeout: 30000 });
  }
  page.__hasVideo = hasVideo;
  return page;
}

// One evaluate does setTime ONLY (no in-page waiting).
// Background pages freeze requestAnimationFrame/setTimeout, so ALL waiting
// happens Node-side: trivial evaluates + polling work fine on background pages
// (verified), and page.screenshot() forces a fresh compositor frame anyway.
async function setTimeAndWait(page, t, hasVideo) {
  await page.evaluate((t) => window.__setTime(t), t);
  if (!hasVideo) return false;
  // poll the seeking flag with a Node-side timeout (600ms cap + warn)
  const t0 = Date.now();
  for (;;) {
    const seeking = await page.evaluate(() => {
      const vids = [...document.querySelectorAll('video.bgvid')];
      const act = vids.find((v) => v.style.opacity === '1');
      return act ? act.seeking : false;
    });
    if (!seeking) return false;
    if (Date.now() - t0 > FALLBACK_MS) return true;
    await new Promise((r) => setTimeout(r, 40));
  }
}

async function renderSegment(name, page, from, to, outSeg) {
  const ff = spawn('ffmpeg', ['-y', '-v', 'error',
    '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'veryfast', '-threads', '1',
    '-pix_fmt', 'yuv420p', '-r', String(FPS), outSeg],
    { stdio: ['pipe', 'ignore', 'inherit'] });
  children.push(ff);
  ff.stdin.on('error', () => {});
  try {
    let fallbacks = 0;
    const t0 = Date.now();
    for (let i = from; i < to; i++) {
      const t = Math.min(i / FPS, DUR - 0.001);
      const fb = await setTimeAndWait(page, t, page.__hasVideo);
      if (fb) {
        fallbacks++;
        if (fallbacks <= 5 || fallbacks % 50 === 0)
          console.warn(`[${name}] seek fallback used @ frame ${i} (${fallbacks} total)`);
      }
      const buf = await page.screenshot({ type: 'jpeg', quality: 88 });
      await new Promise((res) => { ff.stdin.write(buf) ? res() : ff.stdin.once('drain', res); });
      if ((i - from + 1) % 120 === 0)
        console.log(`[${name}] frame ${i + 1}/${END_F} (${((Date.now() - t0) / 60000).toFixed(1)} min)`);
    }
  } finally {
    ff.stdin.end();
    await new Promise((res) => { ff.on('close', res); ff.on('error', res); });
    children.splice(children.indexOf(ff), 1);
  }
  console.log(`[${name}] done: frames ${from}..${to - 1}`);
}

try {
  const segA = path.join(tmpDir, 'a.mp4');
  const segB = path.join(tmpDir, 'b.mp4');

  console.log(`PARALLEL RENDER: frames ${START_F}..${END_F} of ${N}` +
    (START_F > 0 || END_F < N ? ' (RANGE PREVIEW)' : '') +
    `, A=[${START_F},${MID}) B=[${MID},${END_F})`);
  // pages are created sequentially to avoid setup-time resource contention
  // (the RENDERING itself still runs in parallel below)
  const pageA = await makePage();
  console.log('PAGE A READY');
  const pageB = await makePage();
  console.log('PAGES READY');
  await Promise.all([
    renderSegment('A', pageA, START_F, MID, segA),
    renderSegment('B', pageB, MID, END_F, segB),
  ]);

  // concat without re-encode
  const listFile = path.join(tmpDir, 'list.txt');
  fs.writeFileSync(listFile, `file '${segA}'\nfile '${segB}'\n`);
  await execFileAsync('ffmpeg', ['-y', '-v', 'error', '-f', 'concat', '-safe', '0',
    '-i', listFile, '-c', 'copy', OUT]);
  console.log('RENDER DONE -> ' + OUT);
} finally {
  for (const c of children) { try { c.kill('SIGKILL'); } catch {} }
  await browser.close().catch(() => {});
  fs.rmSync(tmpDir, { recursive: true, force: true });
}
