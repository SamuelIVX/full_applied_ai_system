from typing import Dict, Optional


GENRE_SIMILARITY: Dict[str, Dict[str, float]] = {
    "pop": {
        "pop": 1.0, "dance pop": 0.85, "indie pop": 0.80, "synthwave": 0.6,
        "r&b": 0.55, "hip hop": 0.45, "rock": 0.4, "electronic": 0.5,
    },
    "dance pop": {
        "pop": 0.85, "dance pop": 1.0, "indie pop": 0.75, "synthwave": 0.7,
        "electronic": 0.7, "hip hop": 0.55, "r&b": 0.6,
    },
    "indie pop": {
        "pop": 0.80, "indie pop": 1.0, "dance pop": 0.75, "synthwave": 0.5,
        "rock": 0.5, "folk": 0.45, "lofi": 0.4,
    },
    "rock": {
        "rock": 1.0, "metal": 0.7, "indie pop": 0.5, "pop": 0.4,
        "electronic": 0.3, "folk": 0.4,
    },
    "metal": {
        "metal": 1.0, "rock": 0.7, "electronic": 0.4, "pop": 0.2,
    },
    "lofi": {
        "lofi": 1.0, "ambient": 0.7, "jazz": 0.55, "folk": 0.45,
        "hip hop": 0.5, "indie pop": 0.4,
    },
    "ambient": {
        "ambient": 1.0, "lofi": 0.7, "electronic": 0.5, "classical": 0.4,
        "folk": 0.35,
    },
    "jazz": {
        "jazz": 1.0, "lofi": 0.55, "folk": 0.5, "r&b": 0.55,
        "blues": 0.65, "classical": 0.3,
    },
    "folk": {
        "folk": 1.0, "jazz": 0.5, "country": 0.6, "ambient": 0.35,
        "lofi": 0.45, "classical": 0.3,
    },
    "country": {
        "country": 1.0, "folk": 0.6, "r&b": 0.4, "pop": 0.35,
    },
    "electronic": {
        "electronic": 1.0, "synthwave": 0.8, "dance pop": 0.7, "house": 0.75,
        "metal": 0.4, "hip hop": 0.45, "pop": 0.5,
    },
    "synthwave": {
        "synthwave": 1.0, "electronic": 0.8, "pop": 0.6, "dance pop": 0.7,
        "rock": 0.4, "metal": 0.3, "indie pop": 0.45,
    },
    "hip hop": {
        "hip hop": 1.0, "r&b": 0.7, "pop": 0.5, "lofi": 0.5,
        "dance pop": 0.55, "electronic": 0.45,
    },
    "r&b": {
        "r&b": 1.0, "hip hop": 0.7, "pop": 0.55, "jazz": 0.5,
        "dance pop": 0.6, "folk": 0.35,
    },
    "world": {
        "world": 1.0, "reggae": 0.7, "folk": 0.5, "ambient": 0.4,
    },
    "reggae": {
        "reggae": 1.0, "world": 0.7, "folk": 0.5, "hip hop": 0.4,
    },
}


def get_genre_similarity(genre1: str, genre2: str) -> float:
    if genre1 == genre2:
        return 1.0
    
    g1_lower = genre1.lower()
    g2_lower = genre2.lower()
    
    if g1_lower in GENRE_SIMILARITY:
        return GENRE_SIMILARITY[g1_lower].get(g2_lower, 0.0)
    
    if g2_lower in GENRE_SIMILARITY:
        return GENRE_SIMILARITY[g2_lower].get(g1_lower, 0.0)
    
    for similar_genres in GENRE_SIMILARITY.values():
        if g1_lower in similar_genres or g2_lower in similar_genres:
            return 0.15
    
    return 0.0


def find_similar_genres(genre: str, threshold: float = 0.3) -> list:
    genre_lower = genre.lower()
    similar = []
    
    if genre_lower in GENRE_SIMILARITY:
        for g, score in GENRE_SIMILARITY[genre_lower].items():
            if score >= threshold and g != genre_lower:
                similar.append((g, score))
    
    similar.sort(key=lambda x: x[1], reverse=True)
    return similar