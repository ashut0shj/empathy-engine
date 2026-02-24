"""
demo_script.py
--------------
Demonstrates the Empathy Engine with multiple emotion examples.
Run this to see (and hear) how the engine handles different emotional tones.

Usage:
  python demo_script.py
  python demo_script.py --no-audio   (skip audio generation, just show detection)
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.emotion_detector import detect_emotion
from app.mapping import get_voice_params, describe_params
from app.tts_engine import generate_speech

# Demo sentences covering different emotional tones
DEMO_TEXTS = [
    {
        "label": "😄 Happy/Positive",
        "text": "I just got the job! This is the best day of my life — I'm absolutely thrilled and couldn't be more excited!"
    },
    {
        "label": "😢 Sad/Negative",
        "text": "I don't know what to do anymore. Everything feels so heavy and hopeless. I miss the way things used to be."
    },
    {
        "label": "😐 Neutral",
        "text": "The quarterly report has been submitted. The meeting is scheduled for Thursday at 2pm in conference room B."
    },
    {
        "label": "😡 Angry/Negative",
        "text": "This is completely unacceptable. I've been waiting for three hours and nobody has helped me. This is the worst service I've ever experienced!"
    },
    {
        "label": "🤩 Enthusiastic/Positive",
        "text": "Wow, this technology is incredible! I never imagined something like this would be possible — it's truly revolutionary!"
    },
]


def run_demo(generate_audio: bool = True):
    print("\n" + "=" * 60)
    print("  🎙️  Empathy Engine — Full Demo")
    print("=" * 60)
    print(f"  Generating audio: {'Yes' if generate_audio else 'No (--no-audio mode)'}")
    print("=" * 60)

    output_dir = "output"
    results = []

    for i, demo in enumerate(DEMO_TEXTS, 1):
        print(f"\n{'─' * 60}")
        print(f"  Demo {i}/5: {demo['label']}")
        print(f"{'─' * 60}")
        print(f"  📝 Text: \"{demo['text'][:70]}...\"" if len(demo['text']) > 70 else f"  📝 Text: \"{demo['text']}\"")

        # Detect emotion
        emotion_result = detect_emotion(demo['text'])
        emotion = emotion_result['emotion']
        confidence = emotion_result['confidence']

        print(f"\n  🔍 Detection:")
        print(f"     Emotion:    {emotion.upper()}")
        print(f"     Confidence: {confidence:.1%}")
        print(f"     Method:     {emotion_result['method']}")

        # Get voice params
        params = get_voice_params(emotion, confidence)
        print(f"\n  🎛️  Voice Parameters:")
        print(f"     Rate:   {params['rate']} wpm")
        print(f"     Volume: {params['volume']}")
        print(f"     Pitch:  {params['pitch']:+.1f} semitones")

        # Generate audio (optional)
        audio_path = ""
        if generate_audio:
            audio_path = generate_speech(demo['text'], params, output_dir)

        results.append({
            "label": demo['label'],
            "emotion": emotion,
            "confidence": confidence,
            "params": params,
            "audio_path": audio_path
        })

    # Summary table
    print("\n\n" + "=" * 60)
    print("  📊 Summary")
    print("=" * 60)
    print(f"  {'Category':<28} {'Emotion':<12} {'Conf.':<8} {'Rate':<8} {'Pitch'}")
    print("  " + "-" * 55)
    for r in results:
        print(
            f"  {r['label']:<28} {r['emotion'].upper():<12} "
            f"{r['confidence']:<8.0%} {r['params']['rate']:<8} {r['params']['pitch']:+.1f}st"
        )

    if generate_audio:
        print(f"\n  🎵 Audio files saved to: ./{output_dir}/")
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Empathy Engine Demo")
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Skip audio generation (faster, shows emotion detection only)"
    )
    args = parser.parse_args()
    run_demo(generate_audio=not args.no_audio)
