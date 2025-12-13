---
title: WebRobot ETL API Documentation
version: 1.0.0
description: Comprehensive guides and API reference for building and managing ETL pipelines
---

# WebRobot ETL API Documentation

## Language / Lingua

- **English**: continue on this page (default) or go to `guides/`
- **Italiano**: vai a **[`it/index.md`](it/index.md)**

---

## Quick Start (EN)

Welcome to the WebRobot ETL API documentation. This site provides comprehensive guides and API reference for building and managing ETL pipelines.

## Quick Start

Get started with the WebRobot ETL API in minutes:

1. **Authentication**: Use API Keys for all requests
   ```bash
   curl -H "X-API-Key: your-api-key" https://api.webrobot.eu/api/webrobot/api/projects
   ```

2. **Create a Project**: Set up your first project
   ```bash
   curl -X POST https://api.webrobot.eu/api/webrobot/api/projects \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"name": "my-project", "description": "My first project"}'
   ```

3. **Build a Pipeline**: Follow our [step-by-step guide](guides/build-a-pipeline.md) to create your first ETL pipeline using YAML syntax

## Documentation Sections

### 📚 Guides
- **[Build a Pipeline](guides/build-a-pipeline.md)**: Guide to building ETL pipelines using YAML syntax, attribute resolvers, custom actions, and Python extensions
- **[Pipeline Stages Reference](guides/pipeline-stages.md)**: Complete reference of pipeline stages, YAML syntax, attribute resolvers, custom actions, and Python extensions
- **[Pipeline Examples](guides/pipeline-examples.md)**: Copy-pasteable YAML examples aligned with the current parser and stages
- **[EAN Image Sourcing Plugin](guides/ean-image-sourcing.md)**: EAN plugin pipeline + CloudCredential injection behavior
- **[Partner tecnici](guides/technical-partners.md)**: How to extend WebRobot (API plugins + ETL plugins + Python extensions)

### 📖 API Reference
- **[WebRobot ETL API](openapi.yaml)**: Complete OpenAPI specification with interactive documentation

## Features

- **Pipeline Management**: Create, update, and manage ETL pipelines programmatically via API
- **YAML Syntax**: Define pipelines using declarative YAML configuration
- **Attribute Resolvers**: Custom extraction methods for flexible data extraction
- **Custom Actions**: Extend browser interactions with custom action factories
- **Python Extensions**: Create custom Python row transform stages (`python_row_transform:<name>`)
- **Intelligent Stages**: LLM-powered stages for adaptive web scraping

## Base URLs

- **Production**: `https://api.webrobot.eu/api`
- **Development**: `http://localhost:8020/api`

## Authentication

All API requests require an API key in the `X-API-Key` header:

```
X-API-Key: {organization}:{key}
```

Example:
```
X-API-Key: your-organization:your-api-key
```

## Rate Limiting

Requests are limited to **1000 requests per minute** per API key.

## Support

For questions or issues:
- **Email**: support@webrobot.eu
- **Documentation**: [webrobot.eu](https://webrobot.eu)

---

**Version**: 1.0.0  
**Last Updated**: December 2025

