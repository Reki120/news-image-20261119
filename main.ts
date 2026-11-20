/**
 * news-image-20261119 entrypoint (Node 22, standard library only).
 *
 * The front page is pre-rendered by draw_entry.py into entry.png next to
 * this file. This program validates that PNG thoroughly before copying it
 * to $MAKEFUN_OUTPUT_DIR (default /output):
 *   - PNG signature (8 magic bytes)
 *   - IHDR chunk: length 13, width/height exactly 1024x1024
 *   - IHDR CRC-32 matches the stored value (catches truncated/corrupt files)
 *   - bit depth 8 and colour type 2 (RGB) or 6 (RGBA)
 *   - file size under the 1 MiB entry gate
 * The copy is atomic (temp file + rename) and the result is re-checked:
 * size must equal the source size. Any failure exits non-zero with a
 * clear message on stderr instead of publishing a broken image.
 */
import { copyFileSync, mkdirSync, readFileSync, renameSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const EXPECTED_WIDTH = 1024;
const EXPECTED_HEIGHT = 1024;
const MAX_BYTES = 1024 * 1024;

// CRC-32 (IEEE 802.3) table, built once at startup.
const CRC_TABLE: number[] = [];
for (let n = 0; n < 256; n++) {
  let c = n;
  for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  CRC_TABLE[n] = c >>> 0;
}

function crc32(buf: Buffer): number {
  let crc = 0xffffffff;
  for (const byte of buf) crc = CRC_TABLE[(crc ^ byte) & 0xff] ^ (crc >>> 8);
  return (crc ^ 0xffffffff) >>> 0;
}

function fail(message: string): never {
  console.error(`entry: ${message}`);
  process.exit(1);
}

function main(): void {
  const here = dirname(fileURLToPath(import.meta.url));
  const source = join(here, "entry.png");
  const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
  const dest = join(outDir, "entry.png");

  let png: Buffer;
  try {
    png = readFileSync(source);
  } catch {
    fail(`cannot read ${source} (run: python3 draw_entry.py)`);
  }

  if (png.length < 33) fail(`entry.png is only ${png.length} bytes, not a PNG`);
  if (!png.subarray(0, 8).equals(PNG_SIGNATURE)) {
    fail("entry.png has a bad PNG signature");
  }
  const ihdrLen = png.readUInt32BE(8);
  const ihdrType = png.subarray(12, 16).toString("latin1");
  if (ihdrLen !== 13 || ihdrType !== "IHDR") {
    fail(`first chunk is ${ihdrType} (${ihdrLen} bytes), expected IHDR (13)`);
  }
  const ihdrData = png.subarray(16, 29);
  const storedCrc = png.readUInt32BE(29);
  const actualCrc = crc32(Buffer.concat([Buffer.from("IHDR"), ihdrData]));
  if (storedCrc !== actualCrc) {
    fail(
      `IHDR CRC mismatch (stored 0x${storedCrc.toString(16)}, ` +
        `computed 0x${actualCrc.toString(16)}): file is corrupt or truncated`,
    );
  }
  const width = png.readUInt32BE(16);
  const height = png.readUInt32BE(20);
  if (width !== EXPECTED_WIDTH || height !== EXPECTED_HEIGHT) {
    fail(`entry.png is ${width}x${height}, expected ${EXPECTED_WIDTH}x${EXPECTED_HEIGHT}`);
  }
  const bitDepth = png[24];
  const colourType = png[25];
  if (bitDepth !== 8 || (colourType !== 2 && colourType !== 6)) {
    fail(`unexpected PNG format: bit depth ${bitDepth}, colour type ${colourType}`);
  }
  if (png.length >= MAX_BYTES) {
    fail(`entry.png is ${png.length} bytes, over the 1 MiB gate`);
  }

  mkdirSync(outDir, { recursive: true });
  const tmp = join(outDir, `.entry.png.${process.pid}.tmp`);
  copyFileSync(source, tmp);
  renameSync(tmp, dest);
  const copied = statSync(dest).size;
  if (copied !== png.length) {
    fail(`copied ${copied} bytes but source is ${png.length} bytes`);
  }
  console.log(`entry: ${width}x${height} PNG, ${png.length} bytes -> ${dest}`);
}

main();
