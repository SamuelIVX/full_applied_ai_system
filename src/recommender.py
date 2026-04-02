from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Song objects ranked by score for the given UserProfile."""
        user_prefs = {
            "genre":  user.favorite_genre.lower(),
            "mood":   user.favorite_mood.lower(),
            "energy": user.target_energy,
        }
        song_dicts = [s.__dict__ for s in self.songs]
        results = recommend_songs(user_prefs, song_dicts, k)
        # Return only the Song objects in ranked order
        scored_ids = [r[0]["id"] for r in results]
        song_map = {s.id: s for s in self.songs}
        return [song_map[sid] for sid in scored_ids]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a pipe-delimited string describing why song was recommended for user."""
        user_prefs = {
            "genre":  user.favorite_genre.lower(),
            "mood":   user.favorite_mood.lower(),
            "energy": user.target_energy,
        }
        _, reasons = score_song(user_prefs, song.__dict__)
        return " | ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with correctly typed numeric fields."""
    import csv

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":            int(row["id"]),
                "title":         row["title"],
                "artist":        row["artist"],
                "genre":         row["genre"].strip().lower(),
                "mood":          row["mood"].strip().lower(),
                "energy":        float(row["energy"]),
                "tempo_bpm":     float(row["tempo_bpm"]),
                "valence":       float(row["valence"]),
                "danceability":  float(row["danceability"]),
                "acousticness":  float(row["acousticness"]),
            })
    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user_prefs (0.0–1.0) and return (score, reason_strings)."""
    score = 0.0
    reasons = []

    # --- Weights ---
    # EXPERIMENT: genre halved (0.40→0.20), energy doubled (0.15→0.30),
    #             valence absorbs leftover +0.05 (0.10→0.15)
    # Original:   genre=0.40, mood=0.30, energy=0.15, valence=0.10, acousticness=0.05
    # Experiment: genre=0.20, mood=0.30, energy=0.30, valence=0.15, acousticness=0.05
    # Sum check:  0.20 + 0.30 + 0.30 + 0.15 + 0.05 = 1.00 ✓
    W_GENRE        = 0.20
    W_MOOD         = 0.30
    W_ENERGY       = 0.30
    W_VALENCE      = 0.15
    W_ACOUSTICNESS = 0.05

    # --- Genre match ---
    if song["genre"] == user_prefs.get("genre", "").lower():
        score += W_GENRE
        reasons.append(f"genre match ({song['genre']}) +{W_GENRE:.2f}")
    else:
        reasons.append(f"genre mismatch ({song['genre']} ≠ {user_prefs.get('genre', '?')}) +0.00")

    # --- Mood match ---
    if song["mood"] == user_prefs.get("mood", "").lower():
        score += W_MOOD
        reasons.append(f"mood match ({song['mood']}) +{W_MOOD:.2f}")
    else:
        reasons.append(f"mood mismatch ({song['mood']} ≠ {user_prefs.get('mood', '?')}) +0.00")

    # --- Energy proximity ---
    if "energy" in user_prefs:
        energy_proximity = 1.0 - abs(user_prefs["energy"] - song["energy"])
        contribution = round(energy_proximity * W_ENERGY, 3)
        score += contribution
        reasons.append(
            f"energy {song['energy']:.2f} vs target {user_prefs['energy']:.2f} → +{contribution:.3f}"
        )

    # --- Valence proximity ---
    if "valence" in user_prefs:
        valence_proximity = 1.0 - abs(user_prefs["valence"] - song["valence"])
        contribution = round(valence_proximity * W_VALENCE, 3)
        score += contribution
        reasons.append(
            f"valence {song['valence']:.2f} vs target {user_prefs['valence']:.2f} → +{contribution:.3f}"
        )

    # --- Acousticness proximity ---
    if "acousticness" in user_prefs:
        acousticness_proximity = 1.0 - abs(user_prefs["acousticness"] - song["acousticness"])
        contribution = round(acousticness_proximity * W_ACOUSTICNESS, 3)
        score += contribution
        reasons.append(
            f"acousticness {song['acousticness']:.2f} vs target {user_prefs['acousticness']:.2f} → +{contribution:.3f}"
        )

    return round(score, 4), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all songs, sort highest-to-lowest, and return the top-k as (song, score, explanation) tuples."""
    # Score every song and pack results into (song, score, explanation) tuples
    scored = [
        (song, score, " | ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]

    # sorted() returns a new list ranked highest score first
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)

    return ranked[:k]
