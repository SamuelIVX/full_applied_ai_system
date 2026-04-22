# 🎧 Model Card: Music Recommender Simulation

---

## 1. Model Name

**VibeFinder 2.0** (Conversational Music Recommender)

---

## 2. Goal / Task

VibeFinder tries to predict which songs from a small catalog a user will enjoy most,
based on their stated genre, mood, and energy preferences. It does not learn from
listening history — it just compares what the user says they want against what each
song actually sounds like, and returns the closest matches ranked from best to worst.

---

## 3. Data Used

- **Catalog size:** 20 songs stored in `data/songs.csv`
- **Features per song:** genre, mood, energy (0–1), tempo (BPM), valence (0–1),
  danceability (0–1), acousticness (0–1)
- **Genre coverage:** 16 distinct genres — but 13 of them appear only once.
  Lofi has 3 songs, pop and ambient have 2 each. Everything else has 1.
- **Mood coverage:** 10 distinct moods — happy, chill, intense, and moody each
  appear 3 times. Romantic, peaceful, and melancholic each appear only once.
- **Limits:** The catalog reflects Western, digitally-produced music. There are no
  classical, Latin, K-pop, or African genre entries. Any user who prefers those
  styles will receive poor results because their genre won't match anything.

---

## 4. Algorithm Summary

The recommender works like a judge giving points in a competition. Every song gets
evaluated against the user's preferences and receives a score from 0 to 100:

- **20 points** if the song's genre matches the user's preferred genre exactly
- **30 points** if the song's mood matches the user's preferred mood exactly
- **30 points** based on how close the song's energy is to the user's target
  (a song right on target scores all 30; a song far off scores fewer)
- **15 points** based on how close the song's emotional tone (valence) is to the target
- **5 points** based on how close the song's acoustic texture is to the target

All 20 songs are scored, sorted highest to lowest, and the top 5 are returned.
Each result includes a plain-language explanation showing exactly what contributed
to its score — for example: "genre match (pop) +0.20 | mood match (happy) +0.30."

---

## 4.1 VibeFinder 2.0 Conversational Interface

VibeFinder 2.0 adds a conversational interface built with Streamlit that allows users to describe their music preferences in natural language instead of manually selecting sliders.

**Key New Features:**

- **Natural Language Parser** (`src/nl_parser.py`): Extracts structured preferences from free text using keyword matching. Maps terms like "upbeat" → energy 0.7-0.9, "chill" → energy 0.1-0.4, and handles genre synonyms ("dance pop" → "dance pop", "indie" → "indie pop").

- **Conversation State Manager** (`src/state.py`): Tracks conversation history, current user profile, and preference confidence. Asks clarifying questions when profile is underspecified (e.g., "What genre or style of music are you in the mood for?").

- **Genre Similarity Lookup** (`src/genre_similarity.py`): Provides partial credit for near-genre matches. Rock scores 0.7 against metal, dance pop scores 0.85 against pop — fixing the exact string matching bias.

- **Confidence Scoring**: Computes confidence based on how many attributes are specified (1-5), whether genre exists in catalog, and whether mood is recognized. Returns scores with color coding: green (≥0.7), orange (≥0.4), red (<0.4).

- **Edge Case Warnings**: Detects and surfaces warnings for unknown genres, extreme values outside catalog range, and conflicting preferences (e.g., high energy + chill mood).

- **Session Persistence**: Saves conversation state to `.vibefinder_state.json` to preserve history between app refreshes.

- **Demo Profiles**: Quick-start buttons for common use cases: Morning Run, Late Night Coding, Gym Session.

---

## 5. Observed Behavior / Biases

**Bias 1 — Winner-take-all genre problem.**
Because 13 of 16 genres have only one song in the catalog, the genre-matching bonus
almost always guarantees that the single song from a matched genre lands at #1 —
even if its mood or energy are a poor fit. Iron Cathedral scored 0.99 for the metal
profile not because it was a great match on all dimensions, but simply because it was
the *only* metal song. Remove it and the system has nothing reasonable to offer.

**Bias 2 — Exact string matching is too strict.**
"Dance pop" and "indie pop" receive zero genre credit against a "pop" preference,
even though a real listener would consider them very similar. The system treats genre
labels as completely unrelated unless they are character-for-character identical.
This means near-genre songs are unfairly penalized, and users with broad taste get
worse results than users with a single well-represented preference.

**Bias 3 — No diversity in results.**
The system always returns the five most similar songs with nothing to ensure variety.
A user could receive five lofi tracks in a row with no indication that other styles
might suit them. There is no "you might also like" logic — just a straight ranking
of closest matches.

**Bias 4 — Silent failure on unknown genres.**
When a user's preferred genre does not exist in the catalog (tested with "classical"),
the system loses 20 points on every song and returns results that are only marginally
better than random. There is no warning, no fallback message, and no indication to
the user that their preference was unrecognized.

**Bias 5 (VibeFinder 2.0) — NL parser ambiguity.**
The rule-based natural language parser uses keyword matching which can misinterpret ambiguous phrases. "I want something energetic" correctly maps to high energy, but context-dependent requests like "music for studying" rely on hardcoded context mappings that may not cover all use cases. Manual slider override is available for expert users.

---

## 5.1 VibeFinder 2.0 Conversational Evaluation

The same six test profiles (A-F from main.py) were run through the new conversational interface to verify backward compatibility:

- **Profile A**: Natural language "I want happy upbeat pop music" correctly extracts genre=pop, mood=happy, energy=high → Same results as CLI version
- **Profile B**: "something chill for relaxing" → Extracts chill mood, low energy → Same lofi recommendations
- **Profile C**: "dark intense metal for the gym" → Extracts genre=metal, mood=intense → Same Iron Cathedral ranking
- **Profile D**: "high energy but chill vibes" → Warns about conflicting preferences ("high energy + chill mood may conflict")
- **Profile E**: "I want classical music" → Detects unknown genre, shows warning, returns closest alternatives (River Hymn/ambient tracks)
- **Profile F**: "something balanced" → Returns medium-energy results with appropriate confidence score

All six original profiles produce equivalent or improved results in the conversational interface.

---

## 6. Evaluation Process

Six user profiles were tested against all 20 songs. For each profile, the top 5
results were compared against musical intuition to ask: does this feel right?

- **Profile A (pop/happy/high energy):** Worked well. Sunrise City correctly ranked #1
  as the only song matching both genre and mood. Surprise: Gym Hero appeared at #2
  despite having the wrong mood, kept there by its genre match alone.

- **Profile B (lofi/chill/low energy):** Best result overall. Library Rain and Midnight
  Coding both scored above 0.98. Surprise: Heartstring Theory (country) appeared at #5
  with no genre or mood match — it snuck in purely because its acousticness value
  happened to be close to the lofi target.

- **Profile C (metal/intense/high energy):** Iron Cathedral correctly ranked #1 at 0.99.
  Fragile result — the entire profile depends on a single song existing in the catalog.

- **Profile D (adversarial — high energy + chill mood):** Showed the system's priority
  order. Genre and mood (50 combined points) overruled energy (30 points). The chill
  lofi songs won even though their energy was nowhere near the 0.92 target.

- **Profile E (adversarial — unknown genre "classical"):** System failed silently.
  Top result scored only 0.59 with no catalog match on genre. Scores for positions
  2–5 all clustered between 0.45 and 0.49 — nearly indistinguishable.

- **Profile F (adversarial — all numeric values at 0.50):** Showed that genre and mood
  labels matter more than numbers. Even with neutral numeric preferences, Quantum Drift
  (ambient/focused) won cleanly by matching both categorical fields.

A weight-shift experiment was also run: halving the genre weight and doubling energy.
This fixed some near-genre misranking (dance pop, indie pop) but caused high-energy
songs from unrelated genres to surface in low-energy profiles. The original weights
were restored as the better overall choice.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**
VibeFinder is designed for classroom exploration of how content-based recommender
systems work. It is a teaching tool — a small, transparent simulation meant to make
the ideas behind real recommenders visible and testable. It is appropriate for
students learning about weighted scoring, feature matching, and algorithm bias.

**Not intended for:**
- Real music discovery. The 20-song catalog is far too small to serve as an actual
  music app. A real listener would exhaust all good matches in seconds.
- Users who cannot describe their preferences in exact label terms. The system has no
  way to learn from behavior — it requires the user to already know what they want.
- Making decisions about what music is "good" in any objective sense. The scores are
  similarity measures, not quality ratings.
- Any context where fairness across musical cultures matters. The catalog heavily
  favors Western electronic and indie music and systematically underserves
  listeners from other musical traditions. (MITIGATED in 2.0: genre similarity provides partial credit for near-genres, and warnings tell users when preferences are unrecognized.)
- **VibeFinder 2.0 specific**: Users expecting sophisticated semantic understanding. The NL parser is rule-based, not an LLM. Complex or sarcastic requests may be misinterpreted.

---

## 8. Ideas for Improvement

**1. Genre similarity instead of exact matching.**
Replace the binary genre match (match = 1.0, no match = 0.0) with a similarity score
based on how musically related genres are. Rock and metal would score 0.7 against each
other instead of 0.0. This would fix the winner-take-all problem and reduce the harsh
penalty for near-genre preferences like "dance pop" vs "pop."

**2. A diversity rule for the top results.**
Add a constraint that prevents more than two songs from the same genre appearing in the
top five recommendations. This would force the system to surface variety and reduce the
filter bubble effect — users would discover adjacent genres instead of always receiving
more of exactly what they said they liked.

**3. A "no catalog match" warning.**
When the user's preferred genre does not exist in the catalog, surface a clear message
instead of silently returning degraded results. Something like: "No [genre] songs found —
showing closest alternatives." This would make the system honest about its limits and
help users understand why the results feel off.

---

## 9. Personal Reflection

**Design Decisions for VibeFinder 2.0**

1. **Why rule-based over LLM?** Started with keyword matching because:
   - Simple and predictable behavior — no API costs or rate limits
   - Clear debugging path — every extraction can be traced to specific keywords
   - Fast iteration — adding new phrases is just adding dictionary entries
   - Would upgrade to lightweight LLM if user requests more sophisticated parsing

2. **Why session state persistence?** Users expected their conversation to survive page refreshes. Saving to `.vibefinder_state.json` provides continuity without requiring a database.

3. **Why confidence scoring?** The clarification agent only triggers when confidence is low. This prevents the system from asking too many questions too early, following the principle of least surprise.

4. **Why warn vs. fail silently?** From Profile E testing in 1.0, learned that unknown genres should produce explicit warnings, not quietly degraded results.

---

**What was my biggest learning moment?**

The biggest learning moment came during the adversarial testing phase, specifically
Profile E — the "classical" genre that doesn't exist in the catalog. I expected the
system to fail loudly or crash. Instead it returned results quietly, gave River Hymn
a score of 0.59, and moved on as if everything was fine. Nothing in the output told
the user their preference was completely unrecognized. That moment made me realize
that a broken recommendation and a working one can look almost identical from the
outside. The system was confident even when it had nothing useful to offer. That's
not just a bug in my code — it's a property of how real recommenders behave at scale,
and it's part of why auditing AI systems matters.

**How did using AI tools help me, and when did I need to double-check them?**

AI tools were genuinely useful for three things: researching how real platforms like
Spotify combine collaborative and content-based filtering, generating the initial
expanded song catalog with realistic feature values, and helping me think through the
weight rationale before writing any code. The research summaries gave me vocabulary
(valence, acousticness, cold-start problem) that I then used to frame my own design
decisions.

Where I had to slow down and verify: the AI suggested a scoring formula early on that
looked clean but didn't guarantee the weights summed to 1.0. If I had used it without
checking the math, my scores would have been uninterpretable — a song could have scored
above 1.0 or the "percentage match" framing would have been wrong. The lesson is that
AI-generated math and logic needs to be tested, not just read. I ran the weight-shift
experiment specifically because I wanted to see what the formula actually did, not just
what it looked like on paper.

**What surprised me about how simple algorithms can still "feel" like recommendations?**

I was surprised by how much the output *felt* intentional even though the logic is
just arithmetic. When Sunrise City scored 0.99 for the pop/happy profile, it felt like
the system "understood" the request — even though all it did was add up five numbers.
The explanation strings helped a lot here: seeing "genre match (pop) +0.20 | mood match
(happy) +0.30" made the result feel reasoned rather than random.

What broke the illusion was the filter bubble. After running all six profiles, I noticed
the system returned almost identical songs for similar profiles with no variety. A real
listening experience has surprise in it — you discover something you didn't know you
wanted. My system has no mechanism for that. It can feel like a good recommender for
the first result and feel repetitive by the fifth. That gap between "feels right" and
"actually useful over time" is something real platforms invest enormous effort to close.

**What would I try next if I extended this project?**

The change I'm most curious about is adding a genre similarity graph — a small lookup
table that says rock is 70% similar to metal, indie pop is 80% similar to pop, and
reggae is 20% similar to metal. Instead of binary match/no-match, songs would earn
partial genre credit based on how close their genre is to the user's preference. I
think this single change would fix the biggest problems I found: the winner-take-all
monopoly, the "dance pop" ≠ "pop" penalty, and the cold-start degradation for
near-missing genres.

Beyond that, I'd want to add implicit feedback — letting the user skip or replay a
song and having those actions update their profile automatically. That would move the
system from content-based filtering toward the hybrid approach that Spotify actually
uses, and it would be interesting to see how quickly a profile built from behavior
diverges from one built from stated preferences.
