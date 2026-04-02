"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    from recommender import load_songs, recommend_songs
except ModuleNotFoundError:
    from src.recommender import load_songs, recommend_songs


PROFILES = [
    # --- Standard profiles ---
    {
        "name":         "A — High-Energy Pop",
        "genre":        "pop",
        "mood":         "happy",
        "energy":       0.85,
        "valence":      0.80,
        "acousticness": 0.10,
    },
    {
        "name":         "B — Chill Lofi",
        "genre":        "lofi",
        "mood":         "chill",
        "energy":       0.38,
        "valence":      0.60,
        "acousticness": 0.80,
    },
    {
        "name":         "C — Deep Intense Rock",
        "genre":        "metal",
        "mood":         "intense",
        "energy":       0.95,
        "valence":      0.35,
        "acousticness": 0.05,
    },
    # --- Adversarial / edge-case profiles ---
    {
        "name":         "D — Conflict: High Energy + Chill Mood",
        # Energy says "pump it up" but mood says "calm down" — scorer must juggle both
        "genre":        "lofi",
        "mood":         "chill",
        "energy":       0.92,
        "valence":      0.55,
        "acousticness": 0.70,
    },
    {
        "name":         "E — Unknown Genre (no catalog match)",
        # 'classical' doesn't exist in songs.csv — genre weight always 0
        "genre":        "classical",
        "mood":         "peaceful",
        "energy":       0.30,
        "valence":      0.70,
        "acousticness": 0.90,
    },
    {
        "name":         "F — Dead-Center Numeric (energy 0.5, valence 0.5)",
        # Sits equidistant from every song — tests whether ties break sensibly
        "genre":        "ambient",
        "mood":         "focused",
        "energy":       0.50,
        "valence":      0.50,
        "acousticness": 0.50,
    },
]


def print_results(label: str, user_prefs: dict, recommendations: list) -> None:
    """Print one profile's top-5 results in a formatted block."""
    profile_summary = (
        f"genre={user_prefs.get('genre','?')}  "
        f"mood={user_prefs.get('mood','?')}  "
        f"energy={user_prefs.get('energy','?')}"
    )
    print("\n" + "=" * 62)
    print(f"  PROFILE {label}")
    print(f"  {profile_summary}")
    print("=" * 62)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        bar = "#" * int(score * 20)
        print(f"\n  #{rank}  {song['title']}  ({song['artist']})")
        print(f"       Score : {score:.2f}  [{bar:<20}]")
        print(f"       Genre : {song['genre']}   Mood: {song['mood']}")
        print("       Why   :")
        for reason in explanation.split(" | "):
            print(f"               - {reason}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")

    for profile in PROFILES:
        label = profile["name"]
        user_prefs = {k: v for k, v in profile.items() if k != "name"}
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_results(label, user_prefs, recommendations)


if __name__ == "__main__":
    main()
