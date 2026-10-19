# Usa a versão estável do Debian 12 (bookworm)
FROM python:3.11-slim-bookworm

WORKDIR /app

# Instala as dependências do sistema para o WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libharfbuzz0b \
    libgdk-pixbuf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Instala as dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto
COPY . .

# Comando para iniciar a API
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT