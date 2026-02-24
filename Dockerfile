# ─────────────────────────────────────────────────────────────
# Empathy Engine — Dockerfile
# Base: Python 3.11 slim (Debian Bookworm)
# ─────────────────────────────────────────────────────────────

FROM python:3.11-slim

# PYTHONDONTWRITEBYTECODE : stops Python writing .pyc files to disc
# PYTHONUNBUFFERED        : stops Python buffering stdout/stderr (logs appear immediately)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    OUTPUT_DIR=/app/output

# ─── System dependencies ──────────────────────────────────────
#
# ffmpeg      : required by pydub for reading/writing and pitch-shifting audio files
# espeak      : the speech synthesis engine that pyttsx3 drives on Linux
# libespeak1  : shared library that espeak links against
# espeak-data : voice data files espeak needs to produce audio
# alsa-utils  : ALSA command-line tools (aplay etc.) — helps pyttsx3 initialise
# libasound2  : ALSA runtime library
# libsndfile1 : audio file I/O library used internally by audio tools
# curl        : used by the Docker HEALTHCHECK to ping the Flask server
#
# We use --no-install-recommends to keep the image small.
# apt-get clean and rm -rf /var/lib/apt/lists/* remove the package cache
# so it doesn't bloat the final image layer.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    espeak \
    libespeak1 \
    espeak-data \
    alsa-utils \
    libasound2 \
    libsndfile1 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ─── Working directory ────────────────────────────────────────
WORKDIR /app

# ─── Python dependencies ──────────────────────────────────────
# Copy requirements.txt first so Docker can cache this layer independently.
# As long as requirements.txt doesn't change, pip install is skipped on rebuilds.
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    # Download TextBlob language corpora needed by the fallback emotion detector
    python -m textblob.download_corpora

# ─── App source code ──────────────────────────────────────────
COPY . .

# Copy and register the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create output directory where generated audio files are saved
RUN mkdir -p /app/output

# ─── Expose Flask port ────────────────────────────────────────
EXPOSE 5000

# ─── Health check ─────────────────────────────────────────────
# Docker pings GET / every 30 seconds.
# The container is marked unhealthy if this fails 3 times in a row.
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# ─── Entrypoint and default command ───────────────────────────
# ENTRYPOINT runs first on every container start (audio setup, dir creation).
# CMD is the default command passed to the entrypoint — starts the web server.
# Override CMD to run CLI commands instead (see docker-compose.yml).
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app/web_app.py"]
