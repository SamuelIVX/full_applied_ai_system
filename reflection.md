# Reflection: Profile Comparisons

This file compares pairs of user profiles to explain what changed between their outputs
and why — in plain language, without assuming any programming knowledge.

---

## Profile A (High-Energy Pop) vs Profile B (Chill Lofi)

These two profiles are almost complete opposites, and the results show it clearly.

Profile A (pop/happy/energy 0.85) surfaces fast, produced, upbeat tracks — Sunrise City
at #1, Gym Hero at #2. Profile B (lofi/chill/energy 0.38) surfaces slow, acoustic,
background-friendly tracks — Library Rain and Midnight Coding at #1 and #2.

What changed: every dimension flipped. The energy targets (0.85 vs 0.38) pulled the
results toward opposite ends of the catalog. The genre and mood labels sent the system
into completely different sections: pop and happy vs lofi and chill.

Why it makes sense: energy is the most tangible "vibe" dimension. A song at 0.93 energy
(Gym Hero) sounds like something you'd hear at a gym. A song at 0.35 energy (Library Rain)
sounds like rain on a window. The system correctly separated these worlds because the
numbers reflect a real difference in how the songs feel.

What to watch out for: Heartstring Theory (country/melancholic) appeared at #5 for the
chill lofi profile because its acousticness value (0.80) is close to the lofi target.
The system treats "high acousticness" as a proxy for "chill," but a country song is not
what a lofi listener is looking for. The number matched; the vibe did not.

---

## Profile A (High-Energy Pop) vs Profile C (Deep Intense Rock/Metal)

Both profiles want high-energy music, but the genre and mood targets are completely
different — and that difference dominates the results.

Profile A gets pop songs (Sunrise City, Gym Hero) while Profile C gets metal and rock
(Iron Cathedral, Storm Runner). The overlap in energy (both targets above 0.85) does
not pull them toward the same songs because genre and mood together carry 50 points out
of 100. A high-energy lofi song would not appear for either profile — the genre label
blocks it before energy even gets considered.

Why Gym Hero shows up for the metal profile: Gym Hero (pop/intense) scores on mood
("intense" matches) even though its genre is wrong. With 30 points available for mood
and only 20 for genre, a mood match can outweigh a genre match for songs ranked #2 and
below. Gym Hero is loud, fast, and aggressive — musically it has something in common
with metal — but a metal listener would still consider it an odd recommendation. The
system is picking up a real signal (intensity) but cannot distinguish the cultural
difference between pop-intense and metal-intense.

---

## Profile B (Chill Lofi) vs Profile D (Adversarial: High Energy + Chill Mood)

This comparison is the most interesting because Profile D was designed to confuse the system.
Profile D asks for lofi/chill music (same as Profile B) but sets energy to 0.92 —
much higher than any lofi song in the catalog.

Both profiles return Library Rain and Midnight Coding at the top. The difference is in
the scores: Profile B gives Library Rain a 0.99 (near perfect), while Profile D gives it
only 0.81 (good, but not great). The gap comes from the energy penalty — Library Rain has
energy 0.35, which is a 0.57 point gap from the 0.92 target. That gap costs points.

What this tells us: when genre and mood match, the system sticks with those songs even if
the numeric values are very far off. The "chill" label wins over the "high energy" number.
This is both a strength and a weakness. It means the system won't recommend a death metal
song to someone who said "chill" — but it also means a user who genuinely wants energetic
background music (think fast-paced lofi study beats) will still get the slowest songs in
the catalog because "lofi" and "chill" override the energy preference.

---

## Profile C (Deep Intense Rock/Metal) vs Profile E (Unknown Genre: Classical)

These two profiles both want low-valence, acoustic-adjacent music at opposite energy levels,
but the genre situation is completely different — and it shows dramatically in the scores.

Profile C returns Iron Cathedral at 0.99 because "metal" exists in the catalog with a
perfect match. Profile E returns River Hymn at only 0.59 because "classical" does not
exist in the catalog at all. The system gave up 20 points on every single song in Profile E
before even getting to mood, energy, or valence.

In plain terms: Profile C is like walking into a restaurant that serves exactly what you
ordered. Profile E is like walking into a restaurant that doesn't have your dish — so they
bring you the closest thing on the menu, but they charge you full price and don't mention
that it isn't what you asked for.

The practical implication: a classical music listener using VibeFinder would receive folk
and ambient suggestions (River Hymn, Spacewalk Thoughts) that are in the right energy zone
but belong to completely different musical traditions. The system fails silently — there is
no message saying "your genre isn't in the catalog."

---

## Profile E (Unknown Genre) vs Profile F (Dead-Center Numeric)

Both of these profiles tested what happens at the edges of the scoring system — but in
opposite directions.

Profile E has a strong genre preference that the catalog cannot satisfy. Profile F has no
strong preference at all — every numeric value is set to the exact middle (0.50), meaning
no song is particularly close or far on energy, valence, or acousticness.

Despite its "neutral" numerics, Profile F produced a clear winner: Quantum Drift at 0.89.
Why? Because Profile F did specify a genre (ambient) and a mood (focused), and Quantum Drift
matches both. The categorical labels did all the work even when the numbers were uninformative.

Profile E, by contrast, had clear numeric preferences (low energy, high acousticness) but
its genre ("classical") matched nothing. The best it could do was 0.59.

The lesson: in VibeFinder, genre and mood labels are far more powerful than numeric values.
A user who picks the right label words gets great results even with neutral numbers. A user
who picks the wrong label words gets mediocre results even with precise numbers. This is a
real usability problem — the system is only as good as the user's ability to categorize
their own taste in the exact vocabulary the catalog uses.
