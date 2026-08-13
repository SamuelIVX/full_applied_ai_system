"""CLI runner for the VibeFinder 2.0 music recommender.

Runs six hardcoded preference profiles (A through F, including adversarial edge cases)
against ``data/songs.csv`` and prints ranked results. Must be run from the
repo root so the relative catalog path and import fallback resolve correctly.
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
    """Print the supplied recommendations for one profile in a formatted block.

    Args:
        label: Profile display name (e.g. ``"A — High-Energy Pop"``).
        user_prefs: Preference dict used for scoring (no ``name`` key).
        recommendations: ``(song, score, explanation)`` tuples from
            ``recommend_songs``.
    """
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
    """Load the catalog and print recommendations for every hardcoded profile.

    Must be run from the repo root so ``data/songs.csv`` resolves.

    Raises:
        FileNotFoundError: If ``data/songs.csv`` is missing.
        KeyError / ValueError / OSError: Propagated from ``load_songs``.
    """
    songs = load_songs("data/songs.csv")

    for profile in PROFILES:
        label = profile["name"]
        user_prefs = {k: v for k, v in profile.items() if k != "name"}
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_results(label, user_prefs, recommendations)


if __name__ == "__main__":
    main()
