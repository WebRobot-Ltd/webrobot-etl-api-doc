// Patch @opentelemetry/resources to provide defaultResource export if missing.
// Some transitive deps expect `defaultResource` (removed in newer releases).
const fs = require('fs');
const path = require('path');

const target = path.resolve(
  'node_modules',
  '@opentelemetry',
  'resources',
  'build',
  'esm',
  'index.js',
);

try {
  let content = fs.readFileSync(target, 'utf8');
  if (!content.includes('defaultResource')) {
    const patch = `
// Patched: add defaultResource for compatibility
import { Resource } from './Resource.js';
export const defaultResource = Resource.empty();
`;
    content += patch;
    fs.writeFileSync(target, content, 'utf8');
    console.info('✅ Patched @opentelemetry/resources with defaultResource');
  } else {
    console.info('ℹ️ defaultResource already present, no patch applied');
  }
} catch (err) {
  console.error('❌ Failed to patch @opentelemetry/resources:', err);
  process.exit(1);
}

