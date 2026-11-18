// News-image entry for 18 November 2026 (Node 22, standard library only).
//
// The picture itself was drawn at build time by draw.py and ships as
// entry.png beside this file. This program only moves those exact bytes
// into the grading output directory, so the run is deterministic: no
// network, no clock, no randomness, and two runs write identical files.
//
// Run locally with:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const source = join(here, "entry.png");
const target = join(outDir, "entry.png");

mkdirSync(outDir, { recursive: true });
const bytes = readFileSync(source);
writeFileSync(target, bytes);
