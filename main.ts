// news-image-20261119 entry: copies the pre-rendered entry.png beside this
// file to the output directory. Node 22, standard library only, no network.
// The image is drawn by draw_entry.py (Python/Pillow) and committed as
// entry.png; this program's only job is to place those exact bytes at
// <output>/entry.png, identically on every run.
//
// Run locally:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const source = new URL('./entry.png', import.meta.url);
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const target = join(outDir, 'entry.png');

if (!existsSync(source)) {
  throw new Error('entry.png is missing beside main.ts');
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
