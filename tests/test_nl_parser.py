import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from nl_parser import parse_preferences, ENERGY_KEYWORDS, MOOD_KEYWORDS, GENRE_SYNONYMS, VALENCE_KEYWORDS, ACOUSTIC_KEYWORDS


class TestEnergyParsing:
    def test_high_energy_keywords(self):
        for keyword in ["upbeat", "energetic", "high energy", "pump it up", "intense"]:
            result = parse_preferences(f"I want something {keyword}")
            assert result.get("energy") is not None
            assert result["energy"] >= 0.7
    
    def test_low_energy_keywords(self):
        for keyword in ["chill", "relaxed", "low energy", "calm", "laid back"]:
            result = parse_preferences(f"I want something {keyword}")
            assert result.get("energy") is not None
            assert result["energy"] <= 0.4
    
    def test_moderate_energy_keywords(self):
        for keyword in ["moderate", "medium", "balanced"]:
            result = parse_preferences(f"I want something {keyword}")
            assert result.get("energy") is not None
            assert 0.4 <= result["energy"] <= 0.6
    
    def test_context_keywords(self):
        result = parse_preferences("I want something for my morning run")
        assert result.get("energy") is not None
        assert result["energy"] >= 0.7
        
        result = parse_preferences("Music for late night coding")
        assert result.get("energy") is not None
        assert result["energy"] <= 0.5


class TestMoodParsing:
    def test_happy_mood(self):
        for keyword in ["happy", "feel-good", "bouncy", "joyful"]:
            result = parse_preferences(f"I want something {keyword}")
            assert result.get("mood") == "happy"
    
    def test_moody_mood(self):
        for keyword in ["dark", "moody", "introspective", "sad"]:
            result = parse_preferences(f"I want something {keyword}")
            assert result.get("mood") == "moody"
    
    def test_chill_mood(self):
        for keyword in ["chill", "relaxed", "laid back"]:
            result = parse_preferences(f"I want something {keyword}")
            assert result.get("mood") == "chill"
    
    def test_intense_mood(self):
        for keyword in ["intense", "hard", "aggressive"]:
            result = parse_preferences(f"I want something {keyword}")
            assert result.get("mood") == "intense"


class TestGenreParsing:
    def test_exact_genres(self):
        for genre in ["pop", "rock", "metal", "lofi", "jazz"]:
            result = parse_preferences(f"I want to listen to {genre}")
            assert result.get("genre") == genre
    
    def test_genre_synonyms(self):
        test_cases = [
            ("dance pop", "dance pop"),
            ("indie", "indie pop"),
            ("hip hop", "hip hop"),
            ("rap", "hip hop"),
            ("r&b", "r&b"),
            ("electronic", "electronic"),
            ("edm", "electronic"),
            ("synthwave", "synthwave"),
        ]
        for input_genre, expected in test_cases:
            result = parse_preferences(f"I want {input_genre} music")
            assert result.get("genre") == expected
    
    def test_complex_genre_phrases(self):
        result = parse_preferences("I want dance pop with high energy")
        assert result.get("genre") == "dance pop"
        assert result.get("energy") is not None


class TestValenceParsing:
    def test_positive_valence(self):
        for keyword in ["happy", "joyful", "positive", "uplifting"]:
            result = parse_preferences(f"I want something {keyword}")
            assert result.get("valence") is not None
            assert result["valence"] >= 0.7
    
    def test_negative_valence(self):
        for keyword in ["sad", "melancholy", "dark"]:
            result = parse_preferences(f"I want something {keyword}")
            assert result.get("valence") is not None
            assert result["valence"] <= 0.4


class TestAcousticnessParsing:
    def test_acoustic_keywords(self):
        for keyword in ["acoustic", "unplugged", "live", "guitar"]:
            result = parse_preferences(f"I want something {keyword}")
            assert result.get("acousticness") is not None
    
    def test_electronic_keywords(self):
        for keyword in ["electronic", "synth", "produced", "digital"]:
            result = parse_preferences(f"I want something {keyword}")
            assert result.get("acousticness") is not None


class TestComplexPhrases:
    def test_morning_run_phrase(self):
        result = parse_preferences("I want something upbeat for my morning run")
        assert result.get("energy") is not None
        assert result["energy"] >= 0.7
    
    def test_night_coding_phrase(self):
        result = parse_preferences("Chill music for late night coding")
        assert result.get("energy") is not None
        assert result.get("mood") in ["chill", "focused"]
    
    def test_gym_intense_phrase(self):
        result = parse_preferences("Something dark and intense for the gym")
        assert result.get("energy") is not None
        assert result.get("mood") in ["intense", "moody"]
    
    def test_combined_preferences(self):
        result = parse_preferences("I want happy upbeat pop music with high energy")
        assert result.get("genre") == "pop"
        assert result.get("mood") == "happy"
        assert result.get("energy") is not None


class TestNoMatch:
    def test_unrecognized_text_returns_raw(self):
        result = parse_preferences("hello world random text")
        assert result.get("raw_text") is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])