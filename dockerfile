FROM python:3.11-slim

WORKDIR /app

# Installa le dipendenze di sistema e pulisci i file temporanei
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# 2. Copia i requisiti e installali nell'ambiente virtuale
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# 3. Crea le cartelle per la cache locale di Hugging Face e i dati
RUN mkdir -p /root/.cache/huggingface /app/data

# 4. Copia il resto del codice del progetto
COPY . .

# 5. Configura il comando di avvio (cambiato in main.py per convenzione)
CMD ["python", "main.py"]