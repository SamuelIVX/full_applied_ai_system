from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple


@dataclass
class ConversationState:
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
        for key, value in attributes.items():
            if key in self.current_profile and value is not None:
                if key == "energy" and self.current_profile.get("energy") is not None:
                    existing = self.current_profile["energy"]
                    self.current_profile[key] = (existing + value) / 2
                else:
                    self.current_profile[key] = value
        self._compute_confidence()
    
    def _compute_confidence(self) -> float:
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
        has_genre_or_mood = self.current_profile.get("genre") is not None or self.current_profile.get("mood") is not None
        has_energy = self.current_profile.get("energy") is not None
        return has_genre_or_mood or has_energy
    
    def get_active_preferences(self) -> Dict:
        return {k: v for k, v in self.current_profile.items() if v is not None}
    
    def reset(self) -> None:
        self.user_message_history = []
        self.current_profile = {k: None for k in self.current_profile}
        self.preference_confidence = 0.0
        self.clarification_needed = None
    
    def to_dict(self) -> Dict:
        return {
            "user_message_history": self.user_message_history,
            "current_profile": self.current_profile,
            "preference_confidence": self.preference_confidence,
            "clarification_needed": self.clarification_needed,
        }
    
    @classmethod
    def from_dict(cls, data: Dict, available_genres: List[str], catalog_energy_range: Tuple[float, float], catalog_moods: List[str]) -> "ConversationState":
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