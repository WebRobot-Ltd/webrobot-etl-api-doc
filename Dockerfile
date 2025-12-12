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

# Crea directory necessarie per nginx (cache, temp, etc.)
# Nota: /var/run/secrets è montato da Kubernetes e non può essere modificato
RUN mkdir -p /var/cache/nginx/client_temp \
    /var/cache/nginx/proxy_temp \
    /var/cache/nginx/fastcgi_temp \
    /var/cache/nginx/uwsgi_temp \
    /var/cache/nginx/scgi_temp \
    /var/run/nginx && \
    chown -R nginx:nginx /var/cache/nginx /var/run/nginx

# Configurazione nginx personalizzata
# Configura nginx per usare directory scrivibili
RUN echo 'pid /var/run/nginx/nginx.pid; \
events { \
    worker_connections 1024; \
} \
http { \
    client_body_temp_path /tmp/client_temp; \
    proxy_temp_path /tmp/proxy_temp; \
    fastcgi_temp_path /tmp/fastcgi_temp; \
    uwsgi_temp_path /tmp/uwsgi_temp; \
    scgi_temp_path /tmp/scgi_temp; \
    server { \
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
    } \
}' > /etc/nginx/nginx.conf

# Esponi porta
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# Nginx avvia automaticamente, non serve CMD esplicito

