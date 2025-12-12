# WebRobot ETL API Documentation

API documentation generated with [Redocly](https://redocly.com/) and [Redoc](https://github.com/Redocly/redoc).

## Setup

### Redocly CLI Installation

```bash
npm install -g @redocly/cli
```

### Local Development

To view the documentation locally:

```bash
# Start the development server
redocly preview-docs

# Or with Redoc standalone
npx redoc-cli serve openapi.yaml --port 8080
```

### Build

To generate static documentation:

```bash
# Build with Redocly
redocly build-docs

# Or with Redoc standalone
npx redoc-cli bundle openapi.yaml -o dist/index.html
```

## Updating OpenAPI Spec

The OpenAPI specification can be extracted from the running API:

```bash
# From local API
curl http://localhost:8020/api/openapi.json > openapi.json

# From production API
curl https://api.webrobot.eu/api/openapi.json > openapi.json

# Convert JSON to YAML (if needed)
npx js-yaml openapi.json > openapi.yaml
```

## Structure

- `openapi.yaml` - Main OpenAPI specification
- `redocly.yaml` - Redocly configuration
- `decorators/` - Custom decorators (optional)
- `dist/` - Build output (generated)

## Deployment

### GitHub Pages (Recommended)

The documentation is automatically deployed to GitHub Pages via GitHub Actions when pushing to `main` or `master`.

**Setup:**
1. Go to Settings > Pages in the GitHub repository
2. Select "GitHub Actions" as the source
3. The `.github/workflows/deploy.yml` workflow will automatically generate the documentation

**URL:** https://docs.webrobot.eu (if CNAME is configured)

### Redocly Cloud

⚠️ **Note:** Redocly Cloud currently has an internal bug (`resourceFromAttributes is not a function`) that prevents the build. 
We are using GitHub Pages as an alternative.

### Other Options

- **Netlify**: Connect the repository to Netlify
- **Vercel**: Connect the repository to Vercel

## References

- [Redocly Documentation](https://redocly.com/docs/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Redoc GitHub](https://github.com/Redocly/redoc)

