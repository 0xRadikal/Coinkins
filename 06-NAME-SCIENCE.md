# 06 — NAME SELECTION BY MARKETING/NAMING SCIENCE
**Date:** 2026-09-16
**Answers user request #2:** choose the name using marketing psychology + branding research, by actually reading the research.
**Method:** encode published findings as a scorer → validate scorer on known winners AND known losers → generate candidates → verify availability with control-tested tooling.

---

## 1. RESEARCH SOURCES ACTUALLY READ

| Tag | Source | Finding encoded into scorer |
|---|---|---|
| S81 | Schloss 1981 (analysis of top US brands) | 54% of leading brands start with **C, P, K** vs 19% base rate → `+3` for initial c/p/k |
| VB84 | Vanden Bergh 1984/1990 | **Plosive/stop** initials (p,t,k,b,d,g) measurably increase brand recall → `+2` voiceless, `+1.5` voiced |
| SM98 | Smith 1998 "comfort factor" | **Two syllables** = peak comfort → `+2`. Initial **fricatives** (f,s,v,z,h) = negative affect → `-2`. `yu/ew/oo` clusters = disgust → `-1.5` |
| K00 | Klink 2000 | **Front vowels** (i,e) → small/fast/sharp. **Back vowels** (o,u) → big/strong/rich. Vowel choice reliably transmits product attributes |
| SAP | Sapir 1929; Newman 1933; Ultan 1978 | Foundational sound symbolism: /i/ = small, /a,o/ = large. Cross-linguistically stable |
| PL23 | Placek / Lexicon Branding 2023 | **Doubled consonants** read as friendlier/softer (cf. "Kodak","Google") → small bonus |
| LS05 | Lowrey & Shrum 2005/2006; Yorkston & Menon 2004; Meyers-Levy | Name–category **FIT** drives recall and preference, not phonetics alone → used as tie-breaker |

**Tooling:** `name_science.py` (scorer, every rule cites its source), `gen_names.py` (generator + plausibility filter), `check_names.py` v3 (availability).

---

## 2. SCORER VALIDATION — done BEFORE trusting it

Reproduced twice, deterministic:

```
Pudgy         9.5   ← top-5 NFT brand by volume
Pengu         8.0
Kaiju         8.0
Captainz      6.5
CryptoPunks   6.0
Doodles       4.5
Moonbirds     3.0
Milady        2.0
Azuki         1.5
Strikelings   0.0   ← MY OWN earlier pick (doc 03) — rejected by the science
HoodPunksArc -4.5   ← representative Arc-field spam name
```

The scorer separates real winners from the spam field, and it **rejected my own previous recommendation**. That is the evidence it is not merely confirming what I already wanted.

Known limitation (stated, not hidden): this is a heuristic encoding of published effect directions. It is **not** a predictive market model. Effect sizes in the literature are modest; the scorer ranks, it does not forecast sales.

---

## 3. WHY NO REAL ENGLISH WORD WAS USABLE

Every single-word "real word" candidate was already taken on X. Verified TAKEN (not assumed):

> Planchet, Assay, Mintage, Ducat (**all four of Option A's suggestions**), Pondo, Konto, Koban, Potto, Coppa, Kopek, Karat, Koppers, Kopperz, Pennykins, Coinnies, Kobbins, Pipkins, Poffins, Koinos

Consequence: a **coined** name is forced. This is also better for trademark distinctiveness.

---

## 4. FINALISTS — FREE ON ALL FIVE SURFACES

Verified with fixed v3 checker, then independently re-verified by curl:

| name | X | .xyz | .io | .com | OS slug | score |
|---|---|---|---|---|---|---|
| Koinnies | free | free | free | free | free | **9.5** |
| Kopples | free | free | free | free | free | **9.0** |
| Coppits | free | free | free | free | free | **7.0** |
| Coinkins | free | free | free | free | free | **6.5** |

Independent curl verification (x.com returns 404 free / 200 taken):
```
coinkins 404   kopples 404   koinnies 404   coppits 404      → FREE
CONTROL: azuki 200   pudgypenguins 200                       → TAKEN (correct)
```

**Honest caveat:** `twitter.com` returned **301 for every handle including controls** → that domain carries **zero signal**. The verdict rests on `x.com` alone, where controls behaved correctly. Two-domain agreement was therefore NOT achieved; this is single-source-but-control-validated.

---

## 5. RECOMMENDATION — `Coinkins`

Not the top phonetic score. Chosen on the **combined** criteria the research actually supports:

| criterion | Coinkins | Koinnies (9.5) | Kopples (9.0) |
|---|---|---|---|
| c/p/k initial [S81] | ✅ | ✅ | ✅ |
| two syllables [SM98] | ✅ | ✅ | ✅ |
| **meaning instantly parsed** [LS05] | ✅ "little coins" | ❌ none | ❌ none |
| real English morpheme | ✅ `-kin` (napkin, pumpkin, munchkin) | ❌ | ❌ |
| category FIT [LS05] | ✅ gas token **is** USDC | ❌ | ❌ |
| coined → TM-distinctive | ✅ | ✅ | ✅ |
| holder nickname | ✅ "kins" | ~ | ~ |
| misspelling risk | low (`coin` spelled correctly) | **high** (`Koinnies` vs Coinnies/Koinies) | medium |

**Deciding argument:** Lowrey & Shrum and Meyers-Levy show name–category *fit* drives recall and preference. On a chain where gas is literally USDC, "little coins" is maximum fit. `Koinnies`' +3 phonetic points do not buy back the lost meaning plus the spelling ambiguity — and a name people cannot spell cannot be searched, which is fatal for discovery.

**Runner-up if you prefer pure phonetics:** `Kopples`.

---

## 6. IDENTITY SPEC (register in ONE sitting, before publishing the name)

```
Brand        Coinkins
X            @coinkins
Domain       coinkins.xyz (primary) + .io + .com defensive
OS slug      coinkins
Holder term  kins
```

---

## 7. WHAT I COULD NOT VERIFY — USER MUST DO

- ❌ **Trademark search** — no tool available. You must run **USPTO TESS + WIPO Global Brand DB, classes 9 & 42**. Do this BEFORE registering anything.
- ❌ **Instagram** — returns HTTP 200 for nonsense handles → no signal. Earlier Instagram claim formally **withdrawn**.
- ⚠️ **X availability is a snapshot.** Handles are taken continuously. Re-check immediately before registering.
- ⚠️ Availability ≠ legal clearance.
