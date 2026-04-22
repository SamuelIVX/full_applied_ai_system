# 🎧 VibeFinder 2.0 — Conversational Music Recommender

## Project Summary (Original)

VibeFinder began as a content-based music recommendation simulation that scores songs against user preferences and returns ranked results with plain-language explanations. It implements a weighted scoring algorithm using genre, mood, and audio features (energy, valence, acousticness) to find songs matching a specific "vibe."

The original CLI system accepts structured inputs (genre, mood, energy levels) and outputs sorted recommendations with detailed breakdowns of why each song scored the way it did.

---

## VibeFinder 2.0 — Conversational Interface

### What This Project Does

VibeFinder 2.0 extends the original recommender with a **conversational AI interface** that accepts natural language descriptions of musical preferences. Users can describe what they want in plain English ("I want upbeat pop music for my morning run"), and the system:

1. Parses preferences from free text using rule-based keyword matching
2. Tracks conversation history and builds a user profile
3. Triggers clarification questions when preferences are underspecified (confidence < 60%)
4. Scores all songs using the weighted algorithm
5. Warns about edge cases (unknown genres, conflicting preferences, extreme values)
6. Returns ranked recommendations with confidence scores and explanations
7. Persists session state across browser refreshes

### Why This Matters

This project demonstrates how to build an accessible AI system that:
- Accepts natural, conversational input (not just dropdowns and sliders)
- Provides transparency (confidence scores, explanations, warnings)
- Handles edge cases gracefully (unknown genres, conflicting preferences)
- Maintains backward compatibility with the original CLI

For employers: This shows I can take a working algorithm and wrap it in a user-friendly interface while maintaining the core logic.

---

## Architecture Overview

See [assets/system_diagram.md](assets/system_diagram.md) for the full visual diagram.

### System Flow

```
User Input (Natural Language / Quick Buttons / Manual Sliders)
    ↓
NL Parser (src/nl_parser.py) — Extract preferences from text
    ↓
Conversation State Manager (src/state.py) — Track profile + confidence
    ↓
[Confidence < 60%?] → Clarification Loop OR Continue
    ↓
Genre Similarity Lookup (src/genre_similarity.py) — Partial credit for near-genres
    ↓
Recommender Engine (src/recommender.py) — Score songs
    ↓
Edge Case Detector (src/app.py) — Generate warnings
    ↓
Streamlit UI — Display results with confidence scores
```

### Key Components

| Component | File | Purpose |
|---|---|---|
| NL Parser | `src/nl_parser.py` | Rule-based keyword extraction |
| Conversation State | `src/state.py` | Profile tracking + confidence scoring |
| Genre Similarity | `src/genre_similarity.py` | Partial credit for near-genres |
| Recommender | `src/recommender.py` | Core scoring algorithm (unchanged from v1.0) |
| Streamlit App | `src/app.py` | Web interface + edge case detection |

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- Terminal access

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/applied-ai-system-final
cd applied-ai-system-final

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate      # Mac/Linux
# .venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install testing and Streamlit
pip install pytest streamlit

# 5. Run the CLI version (original)
python src/main.py

# 6. Run the Conversational Interface (new)
streamlit run src/app.py
```

The Streamlit app will open at `http://localhost:8501`.

---

## Sample Interactions

### Example 1: Natural Language Input

**Input:**
> "I want something upbeat for my morning run"

**System Response:**
```
Profile: Genre=pop, Mood=happy, Energy=80%
Confidence: High (75%)

🎵 Recommendations:
#1 Sunrise City — Neon Echo (Score: 98%)
   Genre: pop, Mood: happy, Energy: 82%
   Why: genre match (pop) +0.20 | mood match (happy) +0.30 ...

#2 Neon Carnival — Pixel Rush (Score: 77%)
   Genre: dance pop, Mood: happy, Energy: 88%
```

### Example 2: Quick Start Button

**Input:** Click ☀️ Morning Run button

**System Response:**
```
Got it! Finding upbeat tracks with high energy for your run.

🎵 Recommendations:
#1 Sunrise City (Neon Echo) — 98%
#2 Neon Carnival (Pixel Rush) — 77%
```

### Example 3: Unknown Genre

**Input:**
> "I want classical music"

**System Response:**
```
⚠️ Warning: No exact matches for 'classical' — showing closest alternatives

Profile: Genre=classical, Mood=Unknown
Confidence: Low (10%)

🎵 Recommendations:
#1 River Hymn — Clara Voss (Score: 59%)
   Genre: folk, Mood: peaceful
```

### Example 4: Conflicting Preferences

**Input:**
> "Something high energy but chill vibes"

**System Response:**
```
⚠️ Warning: High energy + chill mood may conflict — results may vary
```

---

## Design Decisions

### 1. Rule-Based NL Parser (vs. LLM)

| Decision | Rationale | Trade-off |
|---|---|---|
| Keyword matching | Simple, predictable, debuggable | Can't handle complex semantics |
| Longer phrases prioritized | "dance pop" > "pop" | Context-dependent phrases need manual mapping |
| Manual slider override | Expert user control | Adds UI complexity |

**Why not use an LLM?** This is a teaching tool — rule-based is transparent and shows exactly how extraction works. An LLM would add cost and complexity without improving the core demonstration.

### 2. Confidence Scoring

| Threshold | Behavior |
|---|---|
| ≥ 60% | Proceed to recommend |
| < 60% | Ask clarifying question |

**Rationale:** Users shouldn't be pestered with questions if we already have enough information. The 60% threshold provides a balance between gathering requirements and respecting user time.

### 3. Session Persistence

**Decision:** Save to `.vibefinder_state.json`

**Rationale:** Users expect their conversation to persist across page refreshes. This adds continuity without requiring a database.

### 4. Genre Similarity

**Decision:** Partial credit (not binary matching)

| Genre Pair | Similarity |
|---|---|
| pop ↔ dance pop | 0.85 |
| rock ↔ metal | 0.70 |
| lofi ↔ jazz | 0.55 |

**Original problem:** "dance pop" scored 0 against "pop" preference — even though they're similar. Genre similarity fixes this.

---

## Testing Summary

### Tests Passed: 22 Total

| Test File | Coverage |
|---|---|
| `tests/test_nl_parser.py` | 20 tests — energy, mood, genre, valence, acoustic extraction |
| `tests/test_recommender.py` | 2 tests — backward compatibility with original CLI |

### What Worked

- Keyword extraction for common phrases ("upbeat", "chill", "energetic")
- Genre synonym mapping ("EDM" → "electronic", "indie" → "indie pop")
- Confidence scoring algorithm
- Session persistence across refreshes
- Edge case warnings for unknown genres

### What Didn't Work (Initially Fixed)

| Issue | Fix |
|---|---|
| "dance pop" matched "pop" first | Sort keywords by length (longest first) |
| Quick buttons crashed in columns | Refactor to use session state |
| `use_container_style` deprecated | Remove argument (Streamlit 1.x) |
| Import errors when running from src/ | Fix relative imports |

### What I Learned

1. **Silent failures are dangerous** — Unknown genres returned low scores without warning in v1.0; explicit warnings are better
2. **Simple heuristics work** — Rule-based parsing is predictable and debuggable vs. LLM black box
3. **UX matters** — Session persistence creates continuity that users expect
4. **Edge cases define quality** — The test profiles (A-F) caught problems the happy path missed

---

## Reflection

### What This Project Taught Me About AI

1. **Transparency is a feature** — Confidence scores and explanations aren't just nice-to-have; they're how users trust the system

2. **Edge cases reveal assumptions** — Testing Profile E (unknown genre "classical") taught me that "working" and "useful" are different things

3. **Simple + transparent > complex + opaque** — A rule-based parser I can trace through code is more valuable for a portfolio than an LLM I can't explain

### Problem-Solving Approach

- **Start with working code** — The original CLI was functional; I wrapped it, not replaced it
- **Test the edges** — The adversarial profiles caught more issues than happy paths
- **Iterate on feedback** — Streamlit button bugs were caught by running the app, not tests

---

## Files Reference

| New in VibeFinder 2.0 | Description |
|---|---|
| `src/app.py` | Streamlit conversational interface |
| `src/nl_parser.py` | Natural language preference parser |
| `src/state.py` | Conversation state manager |
| `src/genre_similarity.py` | Genre similarity lookup |
| `tests/test_nl_parser.py` | 20 parser unit tests |
| `assets/system_diagram.md` | Visual architecture diagram |
| `.vibefinder_state.json` | Session persistence (runtime) |

| Original Files (unchanged) | Description |
|---|---|
| `src/recommender.py` | Core scoring engine |
| `src/main.py` | CLI runner |
| `data/songs.csv` | 20-song catalog |
| `tests/test_recommender.py` | Original tests |

---

## Running Tests

```bash
# All tests
pytest tests/ -v

# Parser only
pytest tests/test_nl_parser.py -v

# Recommender only
pytest tests/test_recommender.py -v
```

---

## Future Improvements (Not Implemented)

Ideas for extending this project:

1. **LLM-based parser** — Use GPT for more nuanced extraction
2. **Feedback loop** — Allow users to skip/replay songs to update profile
3. **Diversity rule** — Prevent 5 songs from same genre
4. **Audio features** — Use actual audio analysis for recommendations
5. **User accounts** — Save favorites across sessions

---

*Built for applied AI coursework — demonstrating how to wrap an algorithm in an accessible interface.*