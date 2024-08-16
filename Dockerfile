# Étape de build
FROM python:3.11-slim-bullseye as builder

# Définir des variables d'environnement pour désactiver CUDA et forcer le mode CPU
ENV CUDA_VISIBLE_DEVICES=""
ENV TRANSFORMERS_OFFLINE=1
ENV HF_DATASETS_OFFLINE=1
ENV TF_FORCE_CPU_ALLOW_GROWTH=true
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:32

WORKDIR /app

# Copier seulement les fichiers nécessaires pour installer les dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Étape finale
FROM python:3.11-slim-bullseye

# Redéfinir les variables d'environnement dans l'image finale
ENV CUDA_VISIBLE_DEVICES=""
ENV TRANSFORMERS_OFFLINE=1
ENV HF_DATASETS_OFFLINE=1
ENV TF_FORCE_CPU_ALLOW_GROWTH=true
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:32
ENV USERNAME=${USERNAME}
ENV TOKEN_ID=${TOKEN_ID}
ENV CLIENT_ID=${CLIENT_ID}
ENV CLIENT_SECRET=${CLIENT_SECRET}
ENV REFRESH_TOKEN=${REFRESH_TOKEN}
ENV SMTP_PASSWORD=${SMTP_PASSWORD}

WORKDIR /app

# Créer un utilisateur non-root plus tôt dans l'étape finale
RUN useradd -m appuser && mkdir -p /app /user_conversations /root/.cache/huggingface && chown -R appuser:appuser /app /user_conversations /root/.cache/huggingface

# Passer à l'utilisateur non-root
USER appuser

# Copier les roues de dépendances de l'étape précédente
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Créer un environnement virtuel et installer les roues de dépendances
RUN python -m venv /app/venv \
    && /app/venv/bin/pip install --no-cache /wheels/* \
    && rm -rf /wheels

# Mettre à jour le PATH pour utiliser l'environnement virtuel
ENV PATH="/app/venv/bin:$PATH"

# Copier le reste des fichiers de l'application
COPY . .

# Définir la variable d'environnement pour Hugging Face cache
ENV HF_HOME=/root/.cache/huggingface

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
