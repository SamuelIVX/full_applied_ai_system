# 🎧 Model Card: Music Recommender Simulation

---

## 1. Model Name

**VibeFinder 1.0**

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
  favors Western electronic and indie music and would systematically underserve
  listeners from other musical traditions.

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
