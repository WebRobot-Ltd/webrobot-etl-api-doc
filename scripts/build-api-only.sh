#!/bin/bash
# Build script for API-only documentation (without docs mode)
# This is used when build-docs doesn't support docs mode

# Temporarily comment out docs section
sed -i.bak 's/^docs:/#docs:/' .redocly.yaml
sed -i.bak 's/^  root:/#  root:/' .redocly.yaml
sed -i.bak 's/^  sidebars:/#  sidebars:/' .redocly.yaml

# Run build
npm run build-docs

# Restore original config
mv .redocly.yaml.bak .redocly.yaml

