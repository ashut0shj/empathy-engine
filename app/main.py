"""
main.py
-------
The Empathy Engine - main entry point (CLI interface).

Usage:
  python app/main.py
  python app/main.py --text "I'm so happy today!"
  python app/main.py --text "I feel terrible" --output output/
  python app/main.py --interactive

Flow:
  1. Accept text from CLI arg or interactive prompt
  2. Detect emotion from the text
  3. Map emotion -> voice parameters
  4. Generate speech audio
  5. Save audio to output/ folder
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.emotion_detector import detect_emotion
from app.mapping import get_voice_params, describe_params
from app.tts_engine import generate_speech


def print_banner():
    print("\n" + "=" * 55)
    print("  🎙️  The Empathy Engine - Emotional TTS System")
    print("=" * 55)


def run_pipeline(text: str, output_dir: str = "output", config_path: str = None, verbose: bool = True) -> dict:
    """
    Run the full emotion -> speech pipeline on a given text.

    Args:
        text:        Input text to process
        output_dir:  Where to save the output audio
        config_path: Optional path to voice config JSON
        verbose:     Whether to print step-by-step info

    Returns:
        dict with keys: emotion, confidence, params, audio_path
    """
    if verbose:
        print(f"Input text: \"{text}\"")

    if verbose:
        print("\nDetecting emotion")

    emotion_result = detect_emotion(text)
    emotion = emotion_result["emotion"]
    confidence = emotion_result["confidence"]
    method = emotion_result["method"]

    if verbose:
        print(f"  Emotion:    {emotion.upper()}")
        print(f"  Confidence: {confidence:.1%}")
        print(f"  Method:     {method}")
        print(f"  Raw scores: {emotion_result['scores']}")

    if verbose:
        print("\nMapping to voice parameters")
    params = get_voice_params(emotion, confidence, config_path)

    if verbose:
        print(describe_params(emotion, params))

    if verbose:
        print("\nGenerating speech")

    audio_path = generate_speech(text, params, output_dir)

    result = {
        "emotion": emotion,
        "confidence": confidence,
        "method": method,
        "params": params,
        "audio_path": audio_path
    }

    if verbose and audio_path:
        print(f"Audio saved to: {audio_path}")

    return result


def interactive_mode(output_dir: str, config_path: str = None):
    """
    Run continuous interactive CLI session.
    User types text, engine generates speech, repeat.
    """
    print_banner()
    print("\n  Interactive mode - type text and press Enter.")
    print("  Type 'quit' or press Ctrl+C to exit.\n")

    while True:
        try:
            text = input("Enter text: ").strip()
            if not text:
                continue
            if text.lower() in ("quit", "exit", "q"):
                break
            run_pipeline(text, output_dir, config_path)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="The Empathy Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app/main.py --text "I'm absolutely thrilled about this!"
  python app/main.py --text "Everything feels so heavy and sad."
  python app/main.py --text "The report will be ready by Friday."
  python app/main.py --interactive
  python app/main.py --text "Hello!" --output ./my_audio
        """
    )

    parser.add_argument(
        "--text", "-t",
        type=str,
        help="Text to convert to expressive speech"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="output",
        help="Output directory for audio files (default: output/)"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Start interactive mode (type multiple texts)"
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        default=None,
        help="Path to custom voice config JSON (optional)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress verbose output"
    )

    args = parser.parse_args()

    if args.interactive:
        interactive_mode(args.output, args.config)
    elif args.text:
        print_banner()
        result = run_pipeline(args.text, args.output, args.config, verbose=not args.quiet)
        if not result["audio_path"]:
            sys.exit(1)
    else:
        print_banner()
        print("\nNo input provided. Starting interactive mode...\n")
        interactive_mode(args.output, args.config)


if __name__ == "__main__":
    main()
