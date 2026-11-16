import { cp, mkdir, rm, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const outputDir = path.join(projectRoot, 'dist');
const siteFiles = [
  'index.html',
  'sources.html',
  'app.mjs',
  'sources.mjs',
  'data.mjs',
  'styles.css',
];

for (const file of siteFiles) {
  const info = await stat(path.join(projectRoot, file)).catch(() => null);
  if (!info?.isFile()) throw new Error(`Required site file is missing: ${file}`);
}

await rm(outputDir, { recursive: true, force: true });
await mkdir(outputDir, { recursive: true });
for (const file of siteFiles) {
  await cp(path.join(projectRoot, file), path.join(outputDir, file));
}

console.log(`Static site built to ${path.relative(projectRoot, outputDir)}/ (${siteFiles.length} files).`);
