# Étape de build
FROM python:3.11-slim as builder

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
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Étape finale
FROM python:3.11-slim

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

# Créer le répertoire de cache et définir les permissions
RUN mkdir -p /.cache /root/.cache /user_conversations && chmod -R 777 /.cache /root/.cache /user_conversations

# Copier les roues de dépendances de l'étape précédente
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Installer les roues de dépendances
RUN pip install --no-cache /wheels/*

# Copier le reste des fichiers de l'application
COPY . .


# Créer un utilisateur non-root et définir les permissions
RUN useradd -m appuser && chown -R appuser:appuser /app /user_conversations /root/.cache /usr/local/lib/python3.11/site-packages /usr/local/bin /usr/local

USER appuser

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]