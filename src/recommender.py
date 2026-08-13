"""Core content-based music recommender for VibeFinder 2.0.

Scores catalog songs against user preferences with a weighted heuristic
(genre/mood exact match + energy/valence/acousticness proximity). Provides
both functional helpers and a thin OOP wrapper required by the coursework tests.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """Catalog song with numeric audio features used by scoring.

    Required by tests/test_recommender.py.
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
    """User taste preferences for the OOP Recommender API.

    Required by tests/test_recommender.py.
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """OOP wrapper around recommend_songs / score_song.

    Required by tests/test_recommender.py.
    """
    def __init__(self, songs: List[Song]):
        """Store the in-memory song catalog.

        Args:
            songs: Song objects to rank; converted to dicts for scoring.
        """
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Song objects ranked by score for the given UserProfile.

        Args:
            user: Taste profile (genre, mood, target energy).
            k: Maximum number of songs to return.

        Returns:
            Song objects in descending score order (length ≤ k).

        Example:
            >>> rec.recommend(UserProfile("pop", "happy", 0.8, False), k=2)
            [<Song id=1 ...>, ...]
        """
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
        """Return a pipe-delimited string describing why song was recommended for user.

        Args:
            user: Taste profile used for scoring.
            song: Catalog song to explain.

        Returns:
            Human-readable reason fragments joined by `` | ``.
        """
        user_prefs = {
            "genre":  user.favorite_genre.lower(),
            "mood":   user.favorite_mood.lower(),
            "energy": user.target_energy,
        }
        _, reasons = score_song(user_prefs, song.__dict__)
        return " | ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with correctly typed numeric fields.

    Args:
        csv_path: Path to the catalog CSV (stdlib ``csv``, not pandas).

    Returns:
        One dict per row with lowered genre/mood and float numeric fields.

    Raises:
        FileNotFoundError: If ``csv_path`` does not exist.
        KeyError / ValueError: If a required column is missing or not numeric.
    """
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
    """Score one song against user_prefs (0.0–1.0) and return (score, reason_strings).

    Genre and mood use exact string equality. Energy, valence, and acousticness
    use proximity ``1 - |Δ|`` when those keys are present in ``user_prefs``.
    Genre similarity from ``genre_similarity`` is not applied here.

    Args:
        user_prefs: Preference dict (keys may include genre, mood, energy,
            valence, acousticness).
        song: Catalog song dict with the same feature keys.

    Returns:
        ``(rounded_score, reasons)`` where reasons are human-readable fragments.

    Example:
        >>> score, reasons = score_song({"genre": "pop", "energy": 0.8}, song)
        >>> 0.0 <= score <= 1.0
        True
    """
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
    """Score all songs, sort highest-to-lowest, and return the top-k as (song, score, explanation) tuples.

    Args:
        user_prefs: Preference dict passed through to ``score_song``.
        songs: Full catalog as dicts (typically from ``load_songs``).
        k: Maximum number of results to return.

    Returns:
        Up to ``k`` tuples of ``(song_dict, score, pipe_joined_explanation)``.
    """
    # Score every song and pack results into (song, score, explanation) tuples
    scored = [
        (song, score, " | ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]

    # sorted() returns a new list ranked highest score first
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)

    return ranked[:k]
