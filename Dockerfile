# Étape de build
FROM python:3.11-slim-bullseye as builder

# Créer un utilisateur non-root
RUN useradd -m appuser

# Définir des variables d'environnement pour désactiver CUDA et forcer le mode CPU
ENV CUDA_VISIBLE_DEVICES=""
ENV TRANSFORMERS_OFFLINE=1
ENV HF_DATASETS_OFFLINE=1
ENV TF_FORCE_CPU_ALLOW_GROWTH=true
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:32
ENV PATH="/home/appuser/.local/bin:${PATH}"

WORKDIR /app

# Copier seulement les fichiers nécessaires pour installer les dépendances
COPY --chown=appuser:appuser requirements.txt .

# Changer l'utilisateur pour les installations pip
USER appuser

# Installer les dépendances
RUN pip install --user --no-cache-dir wheel \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Étape finale
FROM python:3.11-slim-bullseye

# Créer le même utilisateur non-root
RUN useradd -m appuser

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
ENV PATH="/home/appuser/.local/bin:${PATH}"
ENV HF_HOME=/home/appuser/.cache/huggingface

WORKDIR /app

# Créer les répertoires nécessaires et définir les permissions
RUN mkdir -p /home/appuser/.cache /user_conversations \
    && chown -R appuser:appuser /app /user_conversations /home/appuser/.cache

# Copier les roues de dépendances de l'étape précédente
COPY --from=builder --chown=appuser:appuser /app/wheels /wheels
COPY --from=builder --chown=appuser:appuser /app/requirements.txt .

# Changer l'utilisateur pour les installations et l'exécution
USER appuser

# Installer les roues de dépendances
RUN pip install --user --no-cache-dir /wheels/*

# Copier le reste des fichiers de l'application
COPY --chown=appuser:appuser . .

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]