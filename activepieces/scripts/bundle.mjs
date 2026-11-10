// Builds the publishable package in dist/: one self-contained CommonJS bundle at
// dist/src/index.js plus a package.json with no runtime dependencies. This matches
// how Activepieces ships its own pieces: the engine installs one artifact and
// finds the export whose constructor is named "Piece", so names must survive
// minification (keepNames).
import { build } from 'esbuild';
import { copyFileSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const dist = join(root, 'dist');
const pkg = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));

rmSync(dist, { recursive: true, force: true });
mkdirSync(join(dist, 'src'), { recursive: true });

const result = await build({
  entryPoints: [join(root, 'src', 'index.ts')],
  outfile: join(dist, 'src', 'index.js'),
  bundle: true,
  platform: 'node',
  target: 'node20',
  format: 'cjs',
  minify: true,
  keepNames: true,
  treeShaking: true,
  metafile: true,
  logLevel: 'warning',
});

const outputs = Object.entries(result.metafile.outputs);
const bytes = outputs.reduce((sum, [, o]) => sum + o.bytes, 0);

writeFileSync(
  join(dist, 'package.json'),
  JSON.stringify(
    {
      name: pkg.name,
      version: pkg.version,
      description: pkg.description,
      license: pkg.license,
      repository: pkg.repository,
      homepage: pkg.homepage,
      keywords: pkg.keywords,
      main: './src/index.js',
      dependencies: {},
      files: ['src/index.js', 'package.json', 'README.md', 'LICENSE'],
    },
    null,
    2,
  ) + '\n',
);
copyFileSync(join(root, 'README.md'), join(dist, 'README.md'));
copyFileSync(join(root, '..', 'LICENSE'), join(dist, 'LICENSE'));

console.log(`bundled ${pkg.name}@${pkg.version}: dist/src/index.js ${bytes} bytes`);
