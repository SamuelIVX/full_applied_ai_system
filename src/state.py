"""Conversation state and confidence heuristic for VibeFinder 2.0.

Tracks the evolving preference profile across chat turns, computes a
confidence score used to decide when to ask clarifying questions, and
supports JSON (de)serialization for Streamlit session persistence.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple


@dataclass
class ConversationState:
    """Mutable chat + preference profile for one recommender session.

    Confidence is ``specified_fields / 5``, then adjusted ±0.1 for genre
    catalog membership and +0.05 for known mood, clamped to [0, 1].
    Repeated energy inputs are averaged rather than overwritten.
    """
    user_message_history: List[Dict] = field(default_factory=list)
    current_profile: Dict = field(default_factory=lambda: {
        "genre": None, "mood": None, "energy": None,
        "valence": None, "acousticness": None
    })
    preference_confidence: float = 0.0
    clarification_needed: Optional[str] = None
    available_genres: List[str] = field(default_factory=list)
    catalog_energy_range: Tuple[float, float] = (0.0, 1.0)
    catalog_moods: List[str] = field(default_factory=list)
    
    def update_profile(self, attributes: Dict) -> None:
        """Merge parsed attributes into the current profile and recompute confidence.

        Args:
            attributes: Preference fields from the NL parser (or manual UI).
                ``None`` values are ignored. Energy is averaged with any
                existing energy value.
        """
        for key, value in attributes.items():
            if key in self.current_profile and value is not None:
                if key == "energy" and self.current_profile.get("energy") is not None:
                    existing = self.current_profile["energy"]
                    self.current_profile[key] = (existing + value) / 2
                else:
                    self.current_profile[key] = value
        self._compute_confidence()
    
    def _compute_confidence(self) -> float:
        """Recompute and store preference_confidence from the current profile.

        Returns:
            The updated confidence in [0.0, 1.0].
        """
        specified = sum(1 for v in self.current_profile.values() if v is not None)
        base = specified / 5.0
        
        genre = self.current_profile.get("genre")
        if genre and genre in self.available_genres:
            base += 0.1
        elif genre and genre not in self.available_genres:
            base -= 0.1
        
        mood = self.current_profile.get("mood")
        if mood and mood in self.catalog_moods:
            base += 0.05
        
        self.preference_confidence = max(0.0, min(1.0, base))
        return self.preference_confidence
    
    def get_clarification_question(self) -> Optional[str]:
        """Return a follow-up question when confidence is below 0.6.

        Prioritizes missing genre, then mood, energy, then valence.
        Returns None when confidence is high enough or no gaps remain.

        Returns:
            Clarification prompt string, or ``None`` if none needed.
        """
        if self.preference_confidence >= 0.6:
            return None
        
        gaps = [k for k, v in self.current_profile.items() if v is None]
        
        if not gaps:
            return None
        
        if "genre" in gaps:
            return "What genre or style of music are you in the mood for? (pop, lofi, rock, metal, etc.)"
        if "mood" in gaps:
            return "How would you describe the vibe you want? (happy, chill, intense, moody, focused, etc.)"
        if "energy" in gaps:
            return "Do you want something high energy to pump you up, or more low key and chill?"
        if "valence" in gaps:
            return "Should the music feel more happy/positive or sad/melancholy?"
        
        return None
    
    def has_minimum_preferences(self) -> bool:
        """Return True if genre/mood or energy is set (enough to recommend).

        Returns:
            Whether the profile has at least one actionable preference.
        """
        has_genre_or_mood = self.current_profile.get("genre") is not None or self.current_profile.get("mood") is not None
        has_energy = self.current_profile.get("energy") is not None
        return has_genre_or_mood or has_energy
    
    def get_active_preferences(self) -> Dict:
        """Return profile fields that are currently set (non-None).

        Returns:
            Sparse preference dict suitable for ``recommend_songs``.
        """
        return {k: v for k, v in self.current_profile.items() if v is not None}
    
    def reset(self) -> None:
        """Clear message history, profile values, confidence, and clarification."""
        self.user_message_history = []
        self.current_profile = {k: None for k in self.current_profile}
        self.preference_confidence = 0.0
        self.clarification_needed = None
    
    def to_dict(self) -> Dict:
        """Serialize session fields needed for JSON persistence.

        Returns:
            Dict with history, profile, confidence, and clarification only
            (catalog metadata is re-supplied on load).
        """
        return {
            "user_message_history": self.user_message_history,
            "current_profile": self.current_profile,
            "preference_confidence": self.preference_confidence,
            "clarification_needed": self.clarification_needed,
        }
    
    @classmethod
    def from_dict(cls, data: Dict, available_genres: List[str], catalog_energy_range: Tuple[float, float], catalog_moods: List[str]) -> "ConversationState":
        """Rebuild ConversationState from a persisted dict plus catalog metadata.

        Args:
            data: Output of ``to_dict`` (or equivalent JSON).
            available_genres: Genres present in the loaded catalog.
            catalog_energy_range: ``(min_energy, max_energy)`` from the catalog.
            catalog_moods: Moods present in the loaded catalog.

        Returns:
            Hydrated ConversationState ready for the Streamlit session.
        """
        state = cls(
            available_genres=available_genres,
            catalog_energy_range=catalog_energy_range,
            catalog_moods=catalog_moods
        )
        state.user_message_history = data.get("user_message_history", [])
        state.current_profile = data.get("current_profile", {})
        state.preference_confidence = data.get("preference_confidence", 0.0)
        state.clarification_needed = data.get("clarification_needed")
        return state
