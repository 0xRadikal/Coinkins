# 05 — MERGED CONCEPT A+B, WITH AN INCREMENTAL ROADMAP
Answering your question: *"can we combine concept A and B and add
capabilities one by one on a roadmap? isn't that better?"*

## Short answer: YES — and it is strictly better. Here is the proof.

---

## 1. Why incremental is not just "nicer" — it is the only structure
##    that survives OpenSea's own rules

OpenSea's verification criteria include, verbatim:

> **All collection items minted/revealed**

A collection that ships a huge feature set but never sells out is
**permanently ineligible** for the badge. Features do not clear the gate —
**a completed, sold-out mint does.**

Second verbatim criterion:
> Unique purchases by buyers in the last 30 days
> No significant inorganic sales volume
> Organic owner to item ratio

These reward **a real, growing holder base over time** — which is exactly
what a roadmap produces and what a big-bang launch does not.

**So: ship the smallest thing that can sell out. Add capability after.**

---

## 2. The merge

| | Concept A (Agents) | Concept B (Receipts) | MERGED |
|---|---|---|---|
| Core idea | NFT owns an ERC-6551 wallet with an on-chain spend policy | NFT as a collectible artifact of Arc's money-native design | NFT ships as a clean collectible, **with a reserved upgrade slot** |
| Needs ERC-6551 | **Yes** — and it is **NOT deployed on Arc** (0 bytes, re-verified) | No | Phase 3 only, after revenue |
| Launch risk | High: unproven primitive, unaudited registry deploy, 4x contract complexity | Low | **Low at launch, high ceiling later** |
| Sell-out probability | Lower (complex story, needs education) | Higher (simple, collectible) | Higher |
| Ceiling | High | Low | **High** |

### The merged product in one sentence
> A small, paid, sold-out collectible whose contract reserves the hooks for
> token-bound accounts, so the "agent wallet" capability can be switched on
> later **without migrating holders.**

### How that is done technically (no guessing — this is standard ERC-721)
1. Deploy a normal `ERC721SeaDrop` collection (SeaDrop is **LIVE on Arc**,
   21,081 bytes verified). No custom mint contract needed.
2. ERC-6551 requires **no changes to the NFT contract at all** — the EIP is
   explicitly designed to work with *existing* NFT contracts. Confirmed from
   the spec: *"without requiring changes to existing smart contracts."*
3. Therefore the upgrade is **purely additive and off-critical-path**:
   deploy the registry later, and every existing token instantly gains an
   account. **Zero migration. Zero holder action. Zero risk at launch.**

This is the decisive technical fact that makes the incremental plan safe:
**we are not deferring a feature we'd have to retrofit — 6551 was designed
to be bolted on afterwards.**

---

## 3. Roadmap — each phase gated on a MEASURABLE trigger

No phase starts on vibes. Each has an entry condition.

### Phase 0 — Foundation  (before anything is public)
| Task | Done when |
|---|---|
| Lock the name | All 5 surfaces registered in ONE sitting |
| USPTO TESS + WIPO search, classes 9 & 42 | **You** confirm clear (I have no tool) |
| Register X, .xyz/.io/.com, OpenSea username, Discord | All owned |
| **Do not publish the name before this is complete** | — |

**Cost: ~$40–60. This is the entire hard capital risk of the project.**

### Phase 1 — Testnet dress rehearsal  (`rpc.testnet.arc.io`, chainId 5042002)
| Task | Done when |
|---|---|
| Deploy ERC721SeaDrop on testnet | Contract verified on testnet explorer |
| Configure a paid public stage | `mintPublic` succeeds from a clean wallet |
| **Gas: read `baseFeePerGas` live × 1.5–2** | Never hardcoded. Measured range 64–214 gwei |
| **Decimal test: native = 18 dec, ERC-20 USDC = 6 dec** | Off-by-10¹² test passes |
| Pull-payment withdrawal (not push) | Withdraw test passes |
| Full end-to-end mint | Token lands in a plain EOA |

**Entry condition for Phase 2: every box above green. No exceptions.**

### Phase 2 — Mainnet launch (the revenue phase)
| Parameter | Value | Justification |
|---|---|---|
| Supply | **1,000** | Must be able to SELL OUT — "all items minted" is mandatory |
| Price | **$50 USDC** | 1,000 × $50 = **$50,000 = gate cleared at mint** |
| Alt (softer) | 2,000 × $25 | Same $50,000, easier per-unit, harder sell-out |
| Per wallet | 2–3 | Maximise unique holders (OpenSea reviews owner:item ratio) |
| Phases | allowlist → public | SeaDrop `mintAllowList` then `mintPublic` |
| Reveal | block after mint, provenance hash pre-published | Anti-sniping |
| Royalty | 5% | Ongoing revenue |
| Rail | **SeaDrop** (live, verified) | No custom mint contract |

⚠️ **This is the honest risk.** See §4.

**Entry condition for Phase 3: collection sold out AND badge applied for.**

### Phase 3 — Token-bound accounts (Concept A switched on)
| Task | Note |
|---|---|
| Deploy canonical ERC-6551 registry to Arc | **0 bytes today — we would be first** |
| Registry address `0x000000006551c19487814612e58FE06813775758` | Use CreateX (live, 11,838 B) for the deterministic address |
| Every existing token gains an account | **No migration — by EIP design** |
| Each NFT can then hold USDC natively | Arc's gas token IS USDC |

**Entry condition: Phase 2 revenue in hand. Fund this from proceeds, not savings.**

### Phase 4 — Spend policy / "agent" layer
Only if Phase 3 lands and holders actually use the accounts.
Measured trigger: **>20% of tokens have a funded TBA.**
If nobody funds them, **stop here** — do not build features nobody uses.

### Phase 5 — Verification + scale
- Apply at `opensea.io/settings/verification` (decision typically ~7 days)
- Pursue `opensea.io/partners` in parallel — partners can be badged
  **without** meeting the minimum threshold (their words)

---

## 4. ⚠️ THE LOSS-MAKING RISK — stated before you decide

You asked me to flag anything loss-making. Here it is.

### Hard cost is trivial
```
deploy ERC721SeaDrop   3,500,000 gas x 64.07 gwei x1.5 = $0.34
configure drop           200,000 gas x 64.07 gwei x1.5 = $0.02
per-mint gas (buyer pays)                                $0.01
domains (.xyz + .io + .com)                              ~$40/yr
-------------------------------------------------------------------
TOTAL HARD CAPITAL RISK                                  ~$40-60
```
**You cannot lose meaningful money on this. Maximum downside ≈ $50.**

### But the sell-out risk is REAL and it is the whole plan
Measured on Arc today: **0 of 30 collections have any volume. 23 of 30 have
zero sales.** A paid mint into that market may simply not sell.

Sell-through sensitivity (1,000 @ $50):
| Sold | Revenue | Gate? |
|---|---|---|
| 10% | $5,000 | no |
| 25% | $12,500 | no |
| 50% | $25,000 | no |
| 75% | $37,500 | no |
| **100%** | **$50,000** | **YES** |

**The gate is binary. 99% sold = no badge** (because "all items
minted/revealed" also fails). This is why supply must be **small**.

### My honest assessment
- **Financial downside: negligible (~$50).**
- **Probability of clearing $50k on Arc in the next 60 days: LOW.**
  There is no demonstrated buyer demand on this chain — zero volume across
  the entire field is the measurement, not a guess.
- **Therefore: the realistic goal is not "blue check in 30 days."** It is
  *be the first collection on Arc that actually sells anything at all.*
  That is achievable and it is what creates the demand you'd later monetise.

### Two things I will not do
1. **Wash trading.** OpenSea explicitly screens for "artificially inflated
   volume" and "organic owner to item ratio", and denies badging for it.
   Faking volume is the one action that permanently forfeits the badge.
2. **Promise you a blue check.** Nobody can. Approval is discretionary:
   *"approval is not guaranteed"* — their words.

### The cheapest way to de-risk
Run Phase 1 + a **free 100-item pilot** first to measure whether ANY demand
exists on Arc, before pricing a 1,000-supply paid mint. Cost: ~$0.36.
If the pilot gets <50 unique claimers, the paid mint would have failed —
and you'd have learned it for 36 cents instead of a launch window.

**I recommend this pilot. It is the single highest-value next step.**

---

## 5. Answering "isn't incremental better?" — verdict

**Yes, for four measurable reasons:**
1. OpenSea requires **all items minted** — small-and-complete beats
   big-and-unfinished. Incremental forces small.
2. ERC-6551 needs **no contract change**, so deferring it costs nothing
   and removes an unaudited deploy from the critical path.
3. Their review rewards **unique buyers over 30 days** and organic
   owner:item ratio — a phased holder base scores better than a one-shot dump.
4. Capital risk stays at ~$50 until revenue proves the next phase.

**The only thing I'd change about your instinct:** make **Phase 0 (name +
trademark)** and the **$0.36 demand pilot** hard gates. Everything else can
flex; those two protect you from the only two real losses available here —
building on a name you don't own, and pricing a mint nobody wants.
