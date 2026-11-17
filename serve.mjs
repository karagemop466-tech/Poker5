// Minimal static preview server for the generated site (no dependencies).
// Run: node serve.mjs [port]     Binds 0.0.0.0 so the preview proxy can reach it.
import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { extname, join, normalize } from "node:path";

const port = Number(process.argv[2] || process.env.PORT || 4173);
const root = process.cwd();
const types = {
  ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
};

createServer(async (req, res) => {
  try {
    let p = decodeURIComponent(new URL(req.url, "http://x").pathname);
    if (p === "/") p = "/index.html";
    let file = normalize(join(root, p));
    if (!file.startsWith(root)) { res.writeHead(403).end("forbidden"); return; }
    const s = await stat(file).catch(() => null);
    if (s && s.isDirectory()) file = join(file, "index.html");
    const body = await readFile(file);
    res.writeHead(200, { "content-type": types[extname(file)] || "application/octet-stream",
                         "cache-control": "no-store" });
    res.end(body);
  } catch {
    res.writeHead(404, { "content-type": "text/html; charset=utf-8" });
    res.end("<h1>404</h1><p>Not found. <a href='/'>Home</a></p>");
  }
}).listen(port, "0.0.0.0", () => console.log(`Poker5 preview on http://0.0.0.0:${port}`));
