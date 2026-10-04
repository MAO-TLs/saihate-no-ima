import test from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { relative, isAbsolute } from 'node:path';
import { Scanner } from '@tailwindcss/oxide';
import config from '../postcss.config.mjs';

test('Tailwind explicitly scans only authored app sources, never the default project root', () => {
  const app = fileURLToPath(new URL('../app/', import.meta.url));
  assert.deepEqual(config.plugins, {
    '@tailwindcss/postcss': { base: app },
  });
  assert.equal(isAbsolute(config.plugins['@tailwindcss/postcss'].base), true);
});

test('the configured Tailwind scanner excludes generated output, payloads and private evidence', () => {
  const base = config.plugins['@tailwindcss/postcss'].base;
  const scanner = new Scanner({ sources: [{ base, pattern: '**/*', negated: false }] });
  scanner.scan();
  assert.ok(scanner.files.length > 0);
  assert.ok(scanner.files.some(file => file.endsWith('ScriptBrowser.tsx')));
  for (const file of scanner.files) {
    const path = relative(base, file);
    assert.equal(isAbsolute(path), false);
    assert.equal(path === '..' || path.startsWith('../'), false, file);
    assert.doesNotMatch(path, /(?:^|\/)(?:dist|public|evidence|node_modules|private)(?:\/|$)/);
  }
});
