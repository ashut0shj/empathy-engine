# Empathy Engine

A command-line and web application that reads text, detects its emotional tone, and generates speech audio that sounds different depending on whether the text is positive, negative, or neutral. Happy text is spoken faster and at a higher pitch. Sad text is spoken slower and quieter. Neutral text uses default voice settings.

---

## Technology Used

- **VADER** (vaderSentiment) - emotion detection from text. Primary choice.
- **TextBlob** - fallback emotion detection if VADER is unavailable.
- **pyttsx3** - offline text-to-speech engine. Controls speech rate and volume natively.
- **gTTS** (Google Text-to-Speech) - fallback TTS if pyttsx3 fails. Requires internet.
- **pydub** - post-processes the generated audio to apply pitch shifting, since pyttsx3 does not support pitch natively.
- **ffmpeg** - required by pydub for encoding and decoding audio files.
- **espeak** - the Linux speech synthesis engine that pyttsx3 uses inside the container.
- **Flask** - lightweight web server for the browser interface and REST API.
- **Docker** - packages the entire application, all system dependencies, and all Python libraries into a single portable image.

---

## Project Structure

```
empathy-engine/
├── app/
│   ├── emotion_detector.py   # Emotion detection (VADER + TextBlob fallback)
│   ├── mapping.py            # Emotion to voice parameter mapping
│   ├── tts_engine.py         # TTS generation (pyttsx3 + gTTS fallback)
│   ├── main.py               # CLI entry point
│   └── web_app.py            # Flask web interface and REST API
├── config/
│   └── voice_config.json     # Tunable voice parameters
├── output/                   # Generated audio files land here
├── demo_script.py            # Runs 5 examples and prints a summary table
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container build instructions
├── docker-compose.yml        # Service definitions for web and CLI
├── entrypoint.sh             # Container startup script
├── .dockerignore             # Files excluded from the Docker build
└── README.md
```

---

## Running with Docker (recommended)

This is the easiest way to run the app. Docker installs ffmpeg, espeak, all Python libraries, and everything else automatically inside the container. You do not need to install anything manually except Docker itself.

### Prerequisites

Install Docker Desktop: https://docs.docker.com/get-docker/

Verify it is working:

```bash
docker --version
docker compose version
```

### Build and start the web interface

```bash
git clone https://github.com/ashut0shj/empathy-engine.git
cd empathy-engine

docker compose up --build
```

The first build takes a few minutes because it downloads the base image, installs ffmpeg, espeak, and all Python packages. Subsequent starts are fast because Docker caches the layers.

Once running, open http://localhost:5000 in your browser.

To stop:

```bash
docker compose down
```

### Run a single text from the CLI

```bash
docker compose run --rm cli python app/main.py --text "I am absolutely thrilled about this!"
docker compose run --rm cli python app/main.py --text "Everything feels hopeless and grey."
docker compose run --rm cli python app/main.py --text "The file has been saved to disk."
```

Generated audio files are saved to the `output/` folder on your host machine.

### Run the demo

```bash
docker compose run --rm cli python demo_script.py --no-audio
```

### Interactive CLI mode

```bash
docker compose run --rm -it cli python app/main.py --interactive
```

Type text and press Enter. Type `quit` to exit.

### Call the REST API

With the web server running:

```bash
curl -X POST http://localhost:5000/api/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "I cannot believe how wonderful today has been!"}'
```

Response:

```json
{
  "emotion": "positive",
  "confidence": 0.94,
  "method": "VADER",
  "scores": {"neg": 0.0, "neu": 0.21, "pos": 0.79, "compound": 0.87},
  "params": {"rate": 210, "volume": 1.0, "pitch": 2.0, "pause_factor": 0.8},
  "audio_url": "/audio/empathy_output_20240224_153045.wav"
}
```

---

## Running without Docker (local setup)

### Prerequisites

- Python 3.8 or higher
- ffmpeg installed on your system

Install ffmpeg:

- macOS: `brew install ffmpeg espeak`
- Ubuntu/Debian: `sudo apt install ffmpeg espeak libespeak1`
- Windows: Download from https://ffmpeg.org and add to PATH

### Install Python dependencies

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt
python -m textblob.download_corpora
```

### Run

```bash
# Web interface
python app/web_app.py

# CLI
python app/main.py --text "I am so happy today!"
python app/main.py --interactive
```

---

## Custom Voice Parameters

Edit `config/voice_config.json` to change how the voice sounds for each emotion:

- `rate` - words per minute. Higher is faster.
- `volume` - between 0.0 and 1.0.
- `pitch` - semitone shift. Positive is higher, negative is lower.

Pass the config file explicitly:

```bash
python app/main.py --text "Hello" --config config/voice_config.json
```

---

## Design Notes

### Emotion detection

VADER was chosen over a HuggingFace transformer model for two reasons. First, it requires no model download and works offline. Second, it starts up instantly. VADER gives a compound score between -1.0 and 1.0. Scores above 0.05 are classified as positive, below -0.05 as negative, and anything in between as neutral. TextBlob uses the same threshold logic and serves as a drop-in fallback.

### Emotion to voice mapping

| Emotion  | Rate     | Volume | Pitch       |
|----------|----------|--------|-------------|
| Positive | 210 wpm  | 1.00   | +2 semitones |
| Negative | 135 wpm  | 0.75   | -3 semitones |
| Neutral  | 175 wpm  | 0.90   | 0 semitones  |

Parameters are blended with the neutral defaults based on the confidence score. If VADER is 90% confident the text is positive, the final rate is: neutral_rate + 0.9 * (positive_rate - neutral_rate). This prevents over-modulation when the detector is uncertain.

### Pitch shifting

pyttsx3 controls rate and volume but has no pitch API. Pitch is applied after audio generation by changing the sample rate of the WAV file using pydub. Raising the sample rate makes the audio sound higher in pitch. This requires ffmpeg, which is installed in the Dockerfile.

### TTS fallback chain

pyttsx3 is tried first because it works offline via espeak. If it fails, gTTS is used. gTTS only supports normal and slow speed, so negative emotion maps to slow and everything else maps to normal. Pitch shifting still applies to gTTS output.

### Docker and audio

pyttsx3 on Linux initialises via ALSA, which normally requires a sound card. Inside a headless Docker container there is no audio hardware. The entrypoint script attempts to load the ALSA loopback module. If that fails, the code catches the error and falls through to gTTS. Either way, audio is written to a file rather than played through speakers, so the container works correctly regardless.

---

## Bonus Points Covered

- Flask web interface with text input and in-browser audio playback
- Emotion confidence score in CLI output, web UI, and API response
- REST API endpoint returning structured JSON
- JSON config file for adjusting voice parameters without touching code
- Full Docker containerisation with ffmpeg, espeak, and all dependencies pre-installed
