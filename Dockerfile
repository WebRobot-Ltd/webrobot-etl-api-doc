# Dockerfile per WebRobot ETL API Documentation
# Build multi-stage per generare e servire documentazione HTML statica

# Stage 1: Build
FROM node:18-alpine AS builder

# Imposta working directory
WORKDIR /app

# Copia package files
COPY package*.json ./

# Installa dipendenze
RUN npm ci

# Copia sorgenti
COPY . .

# Build documentazione con redocly
RUN npm run build

# Verifica che il file sia stato generato
RUN ls -la redoc-static.html || (echo "❌ File redoc-static.html non trovato!" && exit 1)

# Stage 2: Production - Nginx
FROM nginx:alpine

# Copia HTML statico generato
COPY --from=builder /app/redoc-static.html /usr/share/nginx/html/index.html

# Configurazione nginx personalizzata (opzionale)
RUN echo 'server { \
    listen 80; \
    server_name _; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location /health { \
        access_log off; \
        return 200 "healthy\n"; \
        add_header Content-Type text/plain; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Esponi porta
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# Nginx avvia automaticamente, non serve CMD esplicito

