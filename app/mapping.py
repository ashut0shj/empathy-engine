import json
import os

DEFAULT_PARAMS = {
    "rate": 175,       
    "volume": 0.9,   
    "pitch": 0,     
    "pause_factor": 1.0  
}

EMOTION_VOICE_MAP = {
    "positive": {
        "rate": 210,       
        "volume": 1.0,    
        "pitch": 2,      
        "pause_factor": 0.8 
    },
    "negative": {
        "rate": 135,     
        "volume": 0.75,   
        "pitch": -3,        
        "pause_factor": 1.4 
    },
    "neutral": {
        "rate": 175,  
        "volume": 0.9,   
        "pitch": 0,      
        "pause_factor": 1.0 
    }
}


def load_config(config_path: str = None) -> dict:
    """
    Optionally load voice parameter overrides from a JSON config file.
    Falls back to built-in EMOTION_VOICE_MAP if file not found.
    """
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                custom = json.load(f)
            print(f"Loaded custom voice config from {config_path}")
            return custom
        except Exception as e:
            print(f"Could not load config ({e}), using defaults.")
    return EMOTION_VOICE_MAP


def get_voice_params(emotion: str, confidence: float = 1.0, config_path: str = None) -> dict:
    """
    Get voice parameters for a given emotion.

    Args:
        emotion:     One of "positive", "negative", "neutral"
        confidence:  Float [0, 1] from the emotion detector
        config_path: Optional path to a JSON config override file

    Returns:
        dict with keys: rate, volume, pitch, pause_factor
    """
    voice_map = load_config(config_path)
    emotion = emotion.lower().strip()

    target = voice_map.get(emotion, EMOTION_VOICE_MAP["neutral"]).copy()
    neutral = EMOTION_VOICE_MAP["neutral"]

    blended = {}
    for key in ["rate", "volume", "pitch", "pause_factor"]:
        target_val = target.get(key, neutral[key])
        neutral_val = neutral[key]
        blended[key] = neutral_val + confidence * (target_val - neutral_val)

    blended["rate"] = int(round(blended["rate"]))
    blended["volume"] = round(blended["volume"], 3)
    blended["pitch"] = round(blended["pitch"], 2)
    blended["pause_factor"] = round(blended["pause_factor"], 2)

    return blended

