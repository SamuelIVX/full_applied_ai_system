# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder 1.0 generates ranked song recommendations from a 20-song catalog based on a user's stated genre, mood, and energy preferences. It is designed for classroom exploration of content-based filtering concepts, not for production use. The system assumes the user can articulate their preferences in advance as explicit values (e.g. "I want pop, happy, energy 0.85") rather than learning from listening history. It makes no assumptions about demographics, listening context, or time of day.

---

## 3. How the Model Works

The recommender works like a judge scoring each song in a competition. Every song in the catalog is evaluated against the user's stated preferences and receives a score between 0.0 and 1.0. Songs that match the user's favorite genre earn up to 20 points out of 100; songs that match the mood earn up to 30 points. The remaining 50 points come from how close the song's energy, emotional tone (valence), and acoustic texture are to the user's targets — the closer the song's values, the higher the score. Once every song has been scored, they are sorted from highest to lowest and the top five are returned with a plain-language explanation of what contributed to each song's score.

---

## 4. Data

The catalog contains 20 songs across 16 distinct genres and 10 distinct moods. The original 10-song starter set was expanded with 10 additional songs to increase genre diversity. Despite this, the distribution is highly uneven: lofi appears 3 times, pop and ambient each appear twice, and 13 other genres appear only once. Moods are more balanced (happy, chill, intense, and moody each appear 3 times), but rare moods like romantic, peaceful, and melancholic each have only a single representative song. The catalog reflects a Western, digitally-produced music perspective — there are no classical, Latin, African, or K-pop entries, which would affect users with those tastes.

---

## 5. Strengths

The system works best when the user's preferred genre has multiple catalog entries and aligns cleanly with their mood target. Profile B (lofi/chill) produced the most intuitive results: Library Rain and Midnight Coding scored 0.99 and 0.98 respectively, and the gap between matched and unmatched songs was large and meaningful. The explanation strings are a genuine strength — every recommendation tells the user exactly which features matched and by how much, which makes the system transparent in a way that real black-box recommenders are not. For simple, well-represented taste profiles, VibeFinder reliably surfaces the right songs.

---

## 6. Limitations and Bias

**The primary weakness discovered through testing is the winner-take-all genre problem.** Because genre matching contributes 20 out of 100 possible points and most genres appear only once in the catalog, any user whose preferred genre has a single representative song will almost always receive that song as #1 — regardless of how poorly it matches their mood or energy. Iron Cathedral (metal/intense) scored 0.99 for the metal profile purely because it is the only metal song; even if its energy had been 0.40 instead of 0.97, it would still rank first.

A second bias is that exact string matching for genre and mood creates invisible penalization. "Dance pop" and "indie pop" receive zero genre credit against a "pop" profile despite being sonically very close. Users who would genuinely enjoy these songs are shown a worse result than they deserve, and the system has no way to express that "rock" is closer to "metal" than "reggae" is. This means the recommender systematically underserves users whose taste sits near genre boundaries.

A third limitation is the absence of a diversity floor. All five recommendations can come from the same genre or share the same mood if those are the closest matches, creating a filter bubble. A user exploring new music will always be pushed back toward what they already said they liked, with no mechanism for serendipitous discovery.

---

## 7. Evaluation

Six user profiles were tested against all 20 songs. Results were evaluated by asking: does the #1 result match what a real listener would expect, and does the gap between matched and unmatched songs feel proportionate?

**Profile A — High-Energy Pop (genre=pop, mood=happy, energy=0.85)**
Result: Sunrise City scored 0.98 at #1. This felt correct — it is the only song that matches both genre and mood simultaneously. What was surprising was Gym Hero ranking #2 at 0.68 despite having the wrong mood ("intense" instead of "happy"). It kept its position purely because of the pop genre match. A real listener asking for happy pop would likely find Gym Hero jarring.

**Profile B — Chill Lofi (genre=lofi, mood=chill, energy=0.38)**
Result: Library Rain and Midnight Coding scored 0.99 and 0.98 at #1 and #2. This was the cleanest result across all tests — both songs are genuinely correct recommendations. What was surprising was Heartstring Theory (country/melancholic) appearing at #5 with zero genre or mood match, kept there solely by its high acousticness score. A chill lofi listener would not expect a country song in their list.

**Profile C — Deep Intense Rock (genre=metal, mood=intense, energy=0.95)**
Result: Iron Cathedral scored 0.99 at #1. This result is correct, but it reveals a fragility — if Iron Cathedral were removed from the catalog, the #1 result would be Storm Runner (rock, not metal) at 0.58, which feels like a significant drop in relevance. The system is one song away from failing this profile entirely.

**Profile D — Adversarial: Conflicting Energy + Mood (genre=lofi, mood=chill, energy=0.92)**
Result: Midnight Coding scored 0.85 at #1. The system resolved the contradiction by siding with genre and mood (0.50 combined weight) over energy (0.30 weight). The lofi songs won even though they have energy around 0.40 — far from the target of 0.92. This shows the system's priority order clearly, but it also means a user who genuinely wants high-energy chill music would receive very low-energy results with no explanation of the tradeoff.

**Profile E — Adversarial: Unknown Genre ("classical")**
Result: River Hymn scored 0.59 at #1, with songs 2–5 clustered at 0.45–0.49. The system degraded gracefully — it found the closest match (peaceful folk) — but the scores compressed. There was no signal to the user that their genre preference was completely unrepresented. A real system would surface a "no catalog match" warning.

**Profile F — Adversarial: Dead-Center Numeric (genre=ambient, mood=focused, energy=0.50)**
Result: Quantum Drift scored 0.89 at #1, demonstrating that the categorical features (genre + mood) remain decisive even when numeric features are perfectly neutral. This confirmed that the weight design is internally consistent — the system never relies solely on numeric proximity to break ties in unexpected ways.

**Weight-shift experiment:** Halving genre weight (0.40→0.20) and doubling energy weight (0.15→0.30) caused Neon Carnival and Rooftop Lights to rise above Gym Hero in Profile A, which was more musically intuitive. However, it allowed Storm Runner to climb into the chill lofi profile at #5 — a musically incorrect result. The experiment confirmed that genre weight is load-bearing and cannot be cut in half without introducing genre-category noise.

---

## 8. Future Work

The most impactful improvement would be replacing exact string genre matching with a genre similarity graph — so that "rock" receives partial credit (e.g. 0.5) against a "metal" profile instead of zero. This alone would fix the winner-take-all problem and make the system useful for genre-adjacent users. A diversity constraint that prevents more than two songs from the same genre appearing in the top five would address the filter bubble issue. Adding listening context (time of day, activity type) as an optional profile field would make the numeric features more meaningful — a user who wants "chill" at 11pm means something different than one who wants it at 9am. Finally, replacing explicit user input with implicit signals (track skips, replays, playlist adds) would move the system toward the collaborative filtering approach that real platforms use.

---

## 9. Personal Reflection

Building VibeFinder made it clear how much of a recommendation is really just a set of design choices disguised as math. Choosing to weight genre at 0.40 versus 0.20 is not a neutral technical decision — it encodes a belief about how people relate to music, and that belief turns out to be partially wrong once you test it against real edge cases. The most surprising discovery was how badly the system degrades when a genre simply doesn't exist in the catalog, producing near-random results with no warning to the user. Real platforms like Spotify handle this gracefully because they have millions of songs — the cold-start problem is hidden by scale. At 20 songs, every gap in the dataset is immediately visible, which made the biases much easier to see and reason about than they would be in a production system.
