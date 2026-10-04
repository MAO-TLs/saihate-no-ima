// Local-only static preview of the exact eventual GitHub Pages mount.
import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {extname, resolve, sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {previewRoute} from './preview-routing.mjs';
import {SITE_BASE_PATH} from '../site-target.mjs';
const root = fileURLToPath(new URL('../dist/client/', import.meta.url));
const types = {'.html':'text/html; charset=utf-8', '.js':'text/javascript; charset=utf-8', '.css':'text/css; charset=utf-8', '.json':'application/json; charset=utf-8', '.png':'image/png', '.jpg':'image/jpeg', '.webp':'image/webp', '.svg':'image/svg+xml', '.woff2':'font/woff2', '.rsc':'text/x-component'};
const server = createServer(async (request, response) => {
  if (!['GET','HEAD'].includes(request.method)) { response.writeHead(405); response.end(); return; }
  const route = previewRoute(request.url ?? '/');
  if (route.redirect) { response.writeHead(302, {Location:route.redirect}); response.end(); return; }
  if (route.status) { response.writeHead(route.status); response.end(); return; }
  try {
    const path = resolve(root, route.file);
    if (!path.startsWith(root.endsWith(sep) ? root : `${root}${sep}`)) { response.writeHead(400); response.end(); return; }
    const bytes = await readFile(path);
    response.writeHead(200, {'Content-Type':types[extname(route.file)] ?? 'application/octet-stream', 'Content-Length':bytes.length, 'Cache-Control':'no-store'});
    response.end(request.method === 'HEAD' ? undefined : bytes);
  } catch { response.writeHead(404); response.end('Not found'); }
});
server.listen(4323, '127.0.0.1', () => console.log(`Local release preview: http://127.0.0.1:4323${SITE_BASE_PATH}/`));
