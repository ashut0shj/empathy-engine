#!/bin/sh
# ─────────────────────────────────────────────────────────────
# entrypoint.sh
#
# Container startup script. Runs before the main CMD.
# Handles audio driver setup on headless Linux (no sound card).
# ─────────────────────────────────────────────────────────────

set -e

# pyttsx3 on Linux tries to initialise a real audio device via ALSA.
# Inside a Docker container there is no sound card, so we create a
# virtual null sink using the ALSA loopback. This lets pyttsx3 initialise
# successfully and write audio to a file even without hardware.
# If this fails silently, gTTS is used as fallback anyway.
if [ ! -f /proc/asound/version ]; then
    # Load ALSA loopback kernel module if available
    modprobe snd-dummy 2>/dev/null || true
fi

# Make sure the output directory exists and is writable
mkdir -p "${OUTPUT_DIR:-/app/output}"

# Hand off to whatever CMD was passed (web server or CLI command)
exec "$@"
