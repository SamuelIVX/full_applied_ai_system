"""Backward-compat tests for the OOP ``Recommender`` wrapper.

Verifies ranked ``recommend`` output and non-empty ``explain_recommendation``
strings against a tiny in-memory catalog.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from src.recommender import Song, UserProfile, Recommender, score_song

def make_small_recommender() -> Recommender:
    """Build a two-song Recommender for ordering / explain smoke tests."""
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_score_song_reason_recovery_genre_match():
    from src.recommender import score_song
    song = {
        "genre": "pop", "mood": "happy", "energy": 0.8,
        "tempo_bpm": 120, "valence": 0.9, "danceability": 0.8, "acousticness": 0.2,
    }
    _score, reasons = score_song({"genre": "pop", "mood": "happy", "energy": 0.8}, song)
    assert any("genre match (pop)" in r for r in reasons)
    assert any("mood match (happy)" in r for r in reasons)


def test_score_song_reason_recovery_energy_proximity():
    from src.recommender import score_song
    song = {
        "genre": "pop", "mood": "happy", "energy": 0.85,
        "tempo_bpm": 120, "valence": 0.9, "danceability": 0.8, "acousticness": 0.2,
    }
    _score, reasons = score_song({"genre": "pop", "mood": "happy", "energy": 0.8}, song)
    assert any("energy" in r and "vs target" in r for r in reasons)


def test_recommend_songs_explanations_are_recoverable():
    from src.recommender import recommend_songs
    songs = [
        {
            "id": 1, "title": "A", "artist": "X", "genre": "pop", "mood": "happy",
            "energy": 0.8, "tempo_bpm": 120, "valence": 0.9, "danceability": 0.8, "acousticness": 0.2,
        },
        {
            "id": 2, "title": "B", "artist": "Y", "genre": "lofi", "mood": "chill",
            "energy": 0.4, "tempo_bpm": 80, "valence": 0.6, "danceability": 0.5, "acousticness": 0.9,
        },
    ]
    results = recommend_songs({"genre": "pop", "mood": "happy", "energy": 0.8}, songs, k=2)
    assert len(results) == 2
    for _, _, explanation in results:
        assert "genre match" in explanation or "genre mismatch" in explanation
        assert "mood match" in explanation or "mood mismatch" in explanation


def test_explain_recommendation_matches_score_song_reasons():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]
    _, score_reasons = score_song(
        {"genre": "pop", "mood": "happy", "energy": 0.8},
        song.__dict__,
    )
    explanation = rec.explain_recommendation(user, song)
    for reason in score_reasons:
        assert reason in explanation
