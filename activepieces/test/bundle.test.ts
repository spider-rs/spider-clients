import { existsSync, readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';

// Runs after `npm run build`. Checks the publishable artifact the way the
// Activepieces engine reads it: one CommonJS file with an export whose
// constructor is named "Piece", and a manifest with no runtime dependencies.
const dist = join(__dirname, '..', 'dist');
const bundle = join(dist, 'src', 'index.js');

describe.skipIf(!existsSync(bundle))('bundled package', () => {
  it('has a manifest with no runtime dependencies', () => {
    const manifest = JSON.parse(readFileSync(join(dist, 'package.json'), 'utf8'));
    expect(manifest.name).toBe('@spider-cloud/piece-spider');
    expect(manifest.main).toBe('./src/index.js');
    expect(manifest.dependencies).toEqual({});
    expect(manifest.private).toBeUndefined();
  });

  it('exports a Piece with the four actions and the custom API call', () => {
    const mod = createRequire(__filename)(bundle);
    const piece = Object.values(mod).find(
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (value: any) => value?.constructor?.name === 'Piece',
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    ) as any;
    expect(piece).toBeDefined();
    expect(Object.keys(piece.actions()).sort()).toEqual(
      ['crawl', 'custom_api_call', 'links', 'scrape', 'search'],
    );
    expect(piece.metadata().minimumSupportedRelease).toBe('0.82.0');
  });
});
