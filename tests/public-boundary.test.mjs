import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, readdirSync} from 'node:fs';
import {join} from 'node:path';
const root = new URL('../', import.meta.url);
const walk = path => readdirSync(new URL(path, root), {withFileTypes:true}).flatMap(entry => entry.isDirectory() ? walk(`${path}/${entry.name}`) : [`${path}/${entry.name}`]);
test('public source has no audit route, navigation or private working exports', () => {
  const allowed = new Set(['README.md','app','public','scripts','tests','package.json','package-lock.json','next.config.ts','postcss.config.mjs','tsconfig.json','vite.config.ts','site-target.mjs','site-target.d.mts']);
  for (const entry of readdirSync(root)) {
    if (entry.startsWith('.') || ['node_modules','dist','tsconfig.tsbuildinfo'].includes(entry)) continue;
    assert.ok(allowed.has(entry), entry);
  }
  const files = [...walk('app'), ...walk('public'), ...walk('scripts')];
  for (const file of files) {
    assert.doesNotMatch(file, /(?:^|\/)(?:audit|evidence|private)(?:\/|$)|verification|freeze/i);
    if (!/\.(?:tsx?|mts|mjs|json|txt)$/.test(file)) continue;
    const text = readFileSync(new URL(file, root), 'utf8');
    assert.doesNotMatch(text, /\/Users\/fletcher|\/private\/tmp|\.codex\/|href=["'](?:\.\.\/|\.\/)?audit/);
  }
});
