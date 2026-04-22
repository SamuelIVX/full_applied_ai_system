from typing import Dict, Tuple, Optional


ENERGY_KEYWORDS = {
    "high": (0.7, 0.9), "upbeat": (0.7, 0.9), "energetic": (0.7, 0.9),
    "pump it up": (0.8, 1.0), "high energy": (0.7, 0.9), "intense": (0.7, 0.9),
    "low": (0.1, 0.4), "chill": (0.1, 0.4), "relaxed": (0.1, 0.4),
    "calm": (0.1, 0.4), "low energy": (0.1, 0.4), "laid back": (0.2, 0.4),
    "laid-back": (0.2, 0.4), "laidback": (0.2, 0.4),
    "moderate": (0.4, 0.6), "medium": (0.4, 0.6), "balanced": (0.4, 0.6),
    "midtempo": (0.4, 0.6), "mid-tempo": (0.4, 0.6),
    "fast": (0.8, 1.0), "fast-paced": (0.8, 1.0),
    "slow": (0.1, 0.3), "slow-paced": (0.1, 0.3),
    "running": (0.7, 0.9), "workout": (0.7, 0.9), "gym": (0.7, 0.9),
    "coding": (0.3, 0.5), "focused work": (0.3, 0.5), "morning run": (0.7, 0.9),
    "late night": (0.2, 0.4),
}


MOOD_KEYWORDS = {
    "happy": "happy", "feel-good": "happy", "bouncy": "happy", "joyful": "happy",
    "upbeat": "happy", "cheerful": "happy", "bright": "happy", "fun": "happy",
    "dark": "moody", "moody": "moody", "introspective": "moody", "sad": "moody",
    "melancholy": "moody", "melancholic": "moody", "gloomy": "moody", "somber": "moody",
    "chill": "chill", "relaxed": "chill", "laid back": "chill", "laid-back": "chill",
    "laidback": "chill", "easy": "chill", "laid-back vibes": "chill",
    "intense": "intense", "hard": "intense", "aggressive": "intense", "powerful": "intense",
    "heavy": "intense", "epic": "intense",
    "focused": "focused", "concentration": "focused", "work": "focused",
    "studying": "focused", "productivity": "focused", "productve": "focused",
    "peaceful": "peaceful", "calm": "peaceful", "serene": "peaceful", "ambient": "peaceful",
    "tranquil": "peaceful", "meditation": "peaceful", "meditative": "peaceful",
    "romantic": "romantic", "love": "romantic", "lover": "romantic",
    "groovy": "chill", "groove": "chill",
}


GENRE_SYNONYMS = {
    "pop": "pop", "dance pop": "dance pop", "indie": "indie pop", "indie pop": "indie pop",
    "hip hop": "hip hop", "rap": "hip hop", "hip-hop": "hip hop", "hiphop": "hip hop",
    "r&b": "r&b", "rb": "r&b", "rnb": "r&b",
    "electronic": "electronic", "edm": "electronic", "techno": "electronic",
    "house": "electronic", "trance": "electronic",
    "rock": "rock", "alt rock": "rock", "alternative rock": "rock",
    "metal": "metal", "heavy metal": "metal", "death metal": "metal",
    "lofi": "lofi", "lo-fi": "lofi", "lo fi": "lofi", "lofi hip hop": "lofi",
    "ambient": "ambient", "drone": "ambient", "noise": "ambient",
    "jazz": "jazz", "blues": "jazz", "smooth jazz": "jazz",
    "folk": "folk", "acoustic genre": "folk", "singer-songwriter": "folk",
    "country": "country", "americana": "country",
    "world music": "world",
    "reggae": "reggae", "dub": "reggae",
    "synthwave": "synthwave", "synth": "synthwave", "retrowave": "synthwave",
    "classical": "classical", "orchestral": "classical",
}


VALENCE_KEYWORDS = {
    "happy": 0.8, "joyful": 0.8, "positive": 0.8, "uplifting": 0.8, "bright": 0.8,
    "sad": 0.2, "melancholy": 0.2, "dark": 0.3, "depressing": 0.1, "somber": 0.2,
    "neutral": 0.5, "balanced": 0.5, "mixed": 0.5, "meh": 0.5,
}


ACOUSTIC_KEYWORDS = {
    "acoustic": 0.8, "unplugged": 0.9, "live": 0.7, "guitar": 0.8,
    "electronic": 0.2, "synth": 0.2, "produced": 0.3, "digital": 0.2,
    "organic": 0.8, "natural": 0.8, "raw": 0.7,
    "piano": 0.7, "violin": 0.7, "strings": 0.7,
}


def parse_preferences(text: str) -> Dict:
    text_lower = text.lower()
    result = {}
    
    genre_candidates = sorted(GENRE_SYNONYMS.items(), key=lambda x: len(x[0]), reverse=True)
    genre_found = None
    for synonym, canonical in genre_candidates:
        if synonym in text_lower:
            genre_found = canonical
            break
    if genre_found:
        result["genre"] = genre_found
    
    mood_found = None
    for keyword, mood in MOOD_KEYWORDS.items():
        if keyword in text_lower:
            mood_found = mood
            break
    if mood_found:
        result["mood"] = mood_found
    
    energy_candidates = sorted(ENERGY_KEYWORDS.items(), key=lambda x: len(x[0]), reverse=True)
    energy_found = None
    for keyword, (low, high) in energy_candidates:
        if keyword in text_lower:
            energy_found = (low + high) / 2
            break
    if energy_found is not None:
        result["energy"] = energy_found
    
    valence_found = None
    for keyword, valence in VALENCE_KEYWORDS.items():
        if keyword in text_lower:
            valence_found = valence
            break
    if valence_found is not None:
        result["valence"] = valence_found
    
    acoustic_found = None
    for keyword, acoustic in ACOUSTIC_KEYWORDS.items():
        if keyword in text_lower:
            acoustic_found = acoustic
            break
    if acoustic_found is not None:
        result["acousticness"] = acoustic_found
    
    if not result:
        result["raw_text"] = text
    
    return result


def extract_any_preference(text: str, pref_type: str) -> Optional[any]:
    parsed = parse_preferences(text)
    return parsed.get(pref_type)