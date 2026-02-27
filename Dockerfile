# ── Build stage ───────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Dependências do sistema para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Runtime stage ─────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Dependência de runtime do psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copia pacotes instalados do build stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copia código da aplicação
COPY . .

# Permissão no entrypoint
RUN chmod +x entrypoint.sh

# Usuário não-root para segurança
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
