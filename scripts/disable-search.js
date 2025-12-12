// Disable Redocly Realm search plugin by replacing it with a no-op implementation.
// This prevents the search-indexer crash on missing descriptions.
const fs = require('fs');
const path = require('path');

const target = path.resolve(
  'node_modules',
  '@redocly',
  'realm',
  'dist',
  'server',
  'plugins',
  'search',
  'index.js',
);

const stub = `export async function searchPlugin() {
  return {
    async afterRoutesCreated() {
      console.info("Search plugin disabled (no-op)");
      return;
    },
    id: "search"
  };
}
`;

try {
  fs.writeFileSync(target, stub, 'utf8');
  console.info('✅ Search plugin stub written to', target);
} catch (err) {
  console.error('❌ Failed to write search plugin stub:', err);
  process.exit(1);
}

