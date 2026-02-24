import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.emotion_detector import detect_emotion
from app.mapping import get_voice_params
from app.tts_engine import generate_speech

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Empathy Engine</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Segoe UI', sans-serif;
      background:  #16213e;
      min-height: 100vh;
      color: #e0e0e0;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .container {
      background: rgba(255,255,255,0.05);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 20px;
      padding: 40px;
      max-width: 680px;
      width: 100%;
      backdrop-filter: blur(10px);
    }
    h1 { font-size: 2rem; margin-bottom: 8px; text-align: center; }
    .subtitle { text-align: center; color: #888; margin-bottom: 30px; font-size: 0.95rem; }
    textarea {
      width: 100%;
      height: 120px;
      background: rgba(0,0,0,0.3);
      border: 1px solid rgba(255,255,255,0.15);
      border-radius: 12px;
      color: #fff;
      font-size: 1rem;
      padding: 16px;
      resize: vertical;
      outline: none;
      transition: border-color 0.2s;
    }
    textarea:focus { border-color: #7c6af7; }
    button {
      width: 100%;
      margin-top: 16px;
      padding: 14px;
      background: #7c6af7;
      color: white;
      font-size: 1.1rem;
      font-weight: 600;
      border: none;
      border-radius: 12px;
      cursor: pointer;
      transition: opacity 0.2s, transform 0.1s;
    }
    button:hover { opacity: 0.9; transform: translateY(-1px); }
    button:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
    .result { margin-top: 28px; display: none; }
    .emotion-card {
      background: rgba(255,255,255,0.07);
      border-radius: 14px;
      padding: 20px;
      margin-bottom: 16px;
    }
    .emotion-label {
      font-size: 1.5rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 2px;
    }
    .positive { color: #4ade80; }
    .negative { color: #f87171; }
    .neutral  { color: #94a3b8; }
    .confidence-bar-wrap {
      background: rgba(255,255,255,0.1);
      border-radius: 999px;
      height: 8px;
      margin: 10px 0;
      overflow: hidden;
    }
    .confidence-bar {
      height: 100%;
      border-radius: 999px;
      background: #7c6af7;
      transition: width 0.5s ease;
    }
    .params-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      margin-top: 12px;
    }
    .param-box {
      background: rgba(0,0,0,0.2);
      border-radius: 10px;
      padding: 12px;
      text-align: center;
    }
    .param-value { font-size: 1.3rem; font-weight: 700; color: #c4b5fd; }
    .param-label { font-size: 0.75rem; color: #888; margin-top: 4px; }
    audio { width: 100%; margin-top: 12px; border-radius: 12px; }
    .error { color: #f87171; margin-top: 12px; font-size: 0.9rem; }
    .loading { text-align: center; color: #888; margin-top: 12px; }
    .method-tag {
      display: inline-block;
      background: rgba(124,106,247,0.2);
      border: 1px solid rgba(124,106,247,0.3);
      border-radius: 20px;
      padding: 2px 12px;
      font-size: 0.8rem;
      color: #a78bfa;
      margin-top: 8px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Empathy Engine</h1>
    <p class="subtitle">AI-powered emotional Text-to-Speech system</p>

    <textarea id="inputText" placeholder="Type something emotional... e.g. 'I'm so excited about today!' or 'I feel really lost right now.'"></textarea>
    <button id="synthesizeBtn" onclick="synthesize()"> Generate Speech</button>

    <div class="loading" id="loading" style="display:none;"> Analyzing emotion and generating audio...</div>
    <div class="error" id="errorBox"></div>

    <div class="result" id="result">
      <div class="emotion-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <div>
            <div style="font-size:0.85rem; color:#888; margin-bottom:4px;">DETECTED EMOTION</div>
            <div class="emotion-label" id="emotionLabel">—</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:0.85rem; color:#888;">CONFIDENCE</div>
            <div style="font-size:1.5rem; font-weight:700;" id="confidenceText">—</div>
          </div>
        </div>
        <div class="confidence-bar-wrap">
          <div class="confidence-bar" id="confidenceBar" style="width:0%"></div>
        </div>
        <div><span class="method-tag" id="methodTag">—</span></div>

        <div class="params-grid" style="margin-top:16px;">
          <div class="param-box">
            <div class="param-value" id="rateVal">—</div>
            <div class="param-label">SPEECH RATE (wpm)</div>
          </div>
          <div class="param-box">
            <div class="param-value" id="volumeVal">—</div>
            <div class="param-label">VOLUME</div>
          </div>
          <div class="param-box">
            <div class="param-value" id="pitchVal">—</div>
            <div class="param-label">PITCH SHIFT (st)</div>
          </div>
        </div>
      </div>

      <div style="font-size:0.85rem; color:#888; margin-bottom:8px;">GENERATED AUDIO</div>
      <audio id="audioPlayer" controls></audio>
    </div>
  </div>

  <script>
    async function synthesize() {
      const text = document.getElementById('inputText').value.trim();
      if (!text) { alert('Please enter some text!'); return; }

      const btn = document.getElementById('synthesizeBtn');
      const loading = document.getElementById('loading');
      const errorBox = document.getElementById('errorBox');
      const result = document.getElementById('result');

      btn.disabled = true;
      loading.style.display = 'block';
      errorBox.textContent = '';
      result.style.display = 'none';

      try {
        const res = await fetch('/api/synthesize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text })
        });
        const data = await res.json();

        if (!res.ok || data.error) {
          throw new Error(data.error || 'Server error');
        }

        // Update emotion display
        const emo = data.emotion;
        const label = document.getElementById('emotionLabel');
        label.textContent = emo.toUpperCase();
        label.className = 'emotion-label ' + emo;

        document.getElementById('confidenceText').textContent = (data.confidence * 100).toFixed(0) + '%';
        document.getElementById('confidenceBar').style.width = (data.confidence * 100) + '%';
        document.getElementById('methodTag').textContent = ' ' + data.method;

        document.getElementById('rateVal').textContent = data.params.rate;
        document.getElementById('volumeVal').textContent = data.params.volume.toFixed(2);
        document.getElementById('pitchVal').textContent = (data.params.pitch >= 0 ? '+' : '') + data.params.pitch.toFixed(1);

        // Set audio source
        document.getElementById('audioPlayer').src = data.audio_url + '?t=' + Date.now();

        result.style.display = 'block';
      } catch (err) {
        errorBox.textContent = 'Error: ' + err.message;
      } finally {
        btn.disabled = false;
        loading.style.display = 'none';
      }
    }

    // Allow Enter+Shift to submit
    document.addEventListener('DOMContentLoaded', () => {
      document.getElementById('inputText').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); synthesize(); }
      });
    });
  </script>
</body>
</html>"""


def create_app():
    
    from flask import Flask, request, jsonify, send_file, Response


    app = Flask(__name__)
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    @app.route("/")
    def index():
        return Response(HTML_PAGE, mimetype="text/html")

    @app.route("/api/synthesize", methods=["POST"])
    def api_synthesize():
        """
        Body: { "text": "your input text" }
        """
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' in request body"}), 400

        text = data["text"].strip()
        if not text:
            return jsonify({"error": "Text cannot be empty"}), 400

        try:
            emotion_result = detect_emotion(text)
            emotion = emotion_result["emotion"]
            confidence = emotion_result["confidence"]

            params = get_voice_params(emotion, confidence)
            audio_path = generate_speech(text, params, OUTPUT_DIR)

            if not audio_path:
                return jsonify({"error": "Speech generation failed"}), 500

            audio_filename = os.path.basename(audio_path)

            return jsonify({
                "emotion": emotion,
                "confidence": confidence,
                "method": emotion_result["method"],
                "scores": emotion_result["scores"],
                "params": params,
                "audio_url": f"/audio/{audio_filename}"
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/audio/<filename>")
    def serve_audio(filename):
        """Serve generated audio files."""
        file_path = os.path.join(OUTPUT_DIR, filename)
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404
        mime = "audio/mpeg" if filename.endswith(".mp3") else "audio/wav"
        return send_file(file_path, mimetype=mime)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
