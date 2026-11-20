// news-image-20261119 entry: copies the pre-rendered entry.png beside this
// file to the output directory. Node 22, standard library only, no network.
// The image is drawn by draw_entry.py (Python/Pillow) and committed as
// entry.png; this program's only job is to place those exact bytes at
// <output>/entry.png, identically on every run.
//
// Run locally:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const source = new URL('./entry.png', import.meta.url);
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const target = join(outDir, 'entry.png');

if (!existsSync(source)) {
  throw new Error('entry.png is missing beside main.ts');
}

// Validate the committed image before copying it: a real PNG must start
// with the 8-byte PNG signature and carry a 1024x1024 IHDR, matching the
// front-page layout draw_entry.py produces. Fail loudly here rather than
// shipping a corrupt or wrong-sized file to grading.
const header = readFileSync(source).subarray(0, 33);
const PNG_SIG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!header.subarray(0, 8).equals(PNG_SIG)) {
  throw new Error('entry.png is not a PNG file (bad signature)');
}
if (header.toString('ascii', 12, 16) !== 'IHDR') {
  throw new Error('entry.png has no IHDR chunk where a PNG must');
}
const width = header.readUInt32BE(16);
const height = header.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  throw new Error(`entry.png is ${width}x${height}, expected 1024x1024`);
}
mkdirSync(outDir, { recursive: true });
copyFileSync(source, target);

// The gate takes at most 1 MiB; fail loudly here rather than at grading time
// if the committed image ever grows past it.
const bytes = statSync(target).size;
if (bytes === 0 || bytes > 1_048_576) {
  throw new Error(`entry.png is ${bytes} bytes, outside the 1..1048576 gate range`);
}
console.log(`entry.png written to ${target} (${bytes} bytes)`);
