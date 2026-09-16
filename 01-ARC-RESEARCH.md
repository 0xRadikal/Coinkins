# Arc NFT Launch — Research Findings (verified 2026-09-16)

Everything here was checked against a primary source: the chain itself, the
OpenSea API, or a dated article. Nothing is assumed.

---

## 1. Arc network — measured on-chain, not from docs

| Fact | Value | How verified |
|---|---|---|
| chainId | **5042** | `eth_chainId` -> `0x13b2` |
| RPC (working) | `https://rpc.mainnet.arc.io` | responded; `rpc.arc.io` did NOT |
| RPC (alt) | `https://arc.drpc.org` | responded, same chainId |
| Head block | 21,161,178+ | `eth_blockNumber` |
| **Block time** | **0.511 s** | measured across 400 blocks |
| Block gas limit | 30,000,000 | `eth_getBlockByNumber` |
| baseFee | ~214 gwei-equivalent | live read |
| Activity | 50 txs in latest block | live read |
| **Gas token** | **USDC** | OpenSea API: `"symbol": "USDC"` |

### Cost per action (measured gasPrice x typical gas)
| Action | Gas | Cost |
|---|---|---|
| ERC-721 transfer | 85,000 | ~0.018 |
| SeaDrop-style mint | 200,000 | **~0.043 USDC (4 cents)** |
| Deploy ERC-721A | 2,500,000 | ~0.53 USDC |

Minting is effectively free for users. Deploying a collection costs under $1.

### What Arc actually is
Circle's own L1, purpose-built for stablecoin finance. Genesis validators:
**BlackRock, Visa, Mastercard, NYSE, Standard Chartered, Galaxy, Figment,
Sumitomo, Worldpay/Global Payments.** Ecosystem partners at launch: Aave,
Uniswap, Morpho, Aerodrome, Across, Binance, Bybit, OKX, Ledger, MetaMask.

This is the single most important strategic fact: **Arc is an institutional
payments chain, not a degen chain.** Its stated use cases are tokenization,
FX, credit, treasury, prediction markets, and **agentic (AI-agent) economic
activity**. There is no ARC airdrop announced.

---

## 2. OpenSea supports Arc — confirmed from OpenSea's own API

`GET https://api.opensea.io/api/v2/chains` returns:
```json
{ "chain": "arc", "name": "Arc Chain", "symbol": "USDC",
  "supports_swaps": true, "block_explorer": "Arc Explorer",
  "block_explorer_url": "https://explorer.arc.io" }
```
Arc is live in production on OpenSea, day one, with swaps enabled.
OpenSea's own ecosystem lead confirmed publicly: "partnering with Arc as a
launch partner and supporting both tokens and NFTs from day one."

---

## 3. The competitive field on Arc is EMPTY — verified

`GET /api/v2/collections?chain=arc&limit=50&order_by=created_date` returns
50 rows, and almost all of them are **DeFi LP position NFTs**
("EARN: CM Position Manager" repeated ~40 times), plus a few unnamed
contract-address placeholders.

The only two named PFP-ish collections found:
| Collection | Chain | Supply |
|---|---|---|
| StonkRaccoons | arc | **0** |
| Monkey Want ARC Chain | arc | **0** |

Both have **zero supply** — deployed but not minted. Note also that
"ARC Stellars" (888 supply) is on **ethereum**, not Arc — a naming
coincidence, not a competitor.

### Announced-but-unlaunched Arc competitors (from X / news)
| Project | Supply | Angle |
|---|---|---|
| Arclings (`@ArclingsNFT`) | 6,283 | 1-bit pixel, "first fully on-chain on Arc", closed-circle grails |
| Kynera (`@KyneraOnArc`) | ~6,000 | "first original PFP on Arc"; mints an OpenSea pass, then delivers the real NFT |
| ARC Terminal | ? | free mint, WL farming |
| Hazels | ? | free mint, WL farming |

**Conclusion: the first-mover window on Arc is genuinely still open, but it
closes within days.** An OpenSea-side warning from a builder with reach:
> "there will be hundreds of nft collections 'launching on arc' in the next two
> weeks and most of them will be a follow, a like, a retweet and a jpeg. if the
> whole roadmap is a mint date, i'm going to scroll past. arc is a chain built
> for programmable dollars. **build like it.**"

That sentence is the strategy brief.

---

## 4. What actually worked on the last new chain (Robinhood Chain, July 2026)

Robinhood Chain is the closest available analogue: brand-backed L2, launched
1 July 2026, OpenSea support, NFT mania within ~2 weeks. Hard numbers:

| Collection | Supply | Mint | Result |
|---|---|---|---|
| **StonkBrokers** | 4,444 | **free**, burn-gated (no public) | floor peaked **13.41 ETH** (>BAYC), **$4.7M** volume |
| **Spritehood Wisps** | 44,444 | paid ~$17 / ~$117 rare, **no whitelist** | **sold out in ~53 min, $1.28M** |
| Cash Cats | 9,995 | — | floor ~0.26 ETH (~$490) |
| Chain Mancers | 5,000 | 75% free via token burn | floor ~0.9 ETH (~$1,700) |

Chain-wide: 50K mints, 80K secondary sales, 25K+ wallets in the first months;
seven collections past 1,500 ETH; NFT volume briefly **2x Ethereum's**.

### The pattern behind every winner
1. **Free or near-free mint.** Every reference run was free or sub-0.01 ETH and
   repriced **10–100x** on secondary. Nobody won by pricing high.
2. **The NFT does something the chain is for.** StonkBrokers used **ERC-6551**
   token-bound accounts so each NFT *is a brokerage account* holding tokenized
   equities (TSLA, NVDA, AAPL). On a stock-trading chain. That is why it beat
   BAYC's floor.
3. **Earned access, not open whitelist.** StonkBrokers required burning a prior
   NFT. Chain Mancers required burning tokens. Scarcity of *access* created the
   premium.
4. **A named human with a track record.** Spritehood = ex-Pudgy Penguins
   co-founder. That alone drove $1.28M with **zero whitelist**.
5. **Art-only also works** if the artist is real: `bolds` by boldleonidas is
   explicitly "no utility, anti-hype, no Discord" and still generated demand.

### The failure mode, also visible in the data
StonkBrokers' floor is **not a price, it is a formula**: its AMM quotes every
NFT at a fixed 666,666 $STONKBROKER, so the floor is leveraged token exposure.
Rewards are recycled trading fees — a closed loop with no external revenue.
Owner concentration was 14.2% (630 owners / 4,444) vs BAYC's 56.7%.
It fell 26% from peak within a week.

**Lesson: reflexive tokenomics manufacture a headline floor and then unwind.
Do not copy the token-peg. Copy the ERC-6551 *usefulness*.**

---

## 5. OpenSea verification — the real, current criteria

From OpenSea's own help centre (updated 12 Aug 2026):

> Accounts that own one or more collections with **at least $50,000 USD of
> volume sold** (or equivalent) and meet other criteria like **minimum activity
> levels and social media presence** are eligible to apply.

Process, verified:
- Apply at `opensea.io/settings/verification`
- Profile must be complete; collections must have no missing fields
- Decision typically **within 7 days**; re-apply after 7 days if denied
- Approval covers the **account**; eligible collections are then auto-badged
- **They review whether volume is organic.** Explicit: *"We may deny badging if
  we believe the creator has artificially inflated collection buying and selling
  volume."*
- Verification can be **revoked** at any time
- Partner collections can be badged **without** meeting the threshold —
  there is a `opensea.io/partners` route

### What this means for planning
$50,000 of **sold volume** is the gate. Two honest routes:
- 5,000 supply x $10 mint = $50,000 primary — but primary mint volume is not
  the same as secondary "volume sold"; secondary trading is what counts safely.
- Free mint + strong secondary: 5,000 items, 15% of supply trading once at
  ~$65 average = ~$50,000. This is how the Robinhood winners got there.

**Do not wash-trade.** It is the one thing OpenSea explicitly screens for, and
the penalty is permanent denial.

---

## 6. Launch-sequence best practice (cross-checked, 2026 sources)

The order matters more than the channel:

1. **Reason to exist first.** If it cannot be explained in two sentences, no
   marketing fixes it. Vague "empowering holders" language is instantly skipped.
2. **50 real people before 5,000 followers.** Manual participation in existing
   communities for weeks. Bought followers and follow-for-follow inflate numbers
   while real engagement stays flat.
3. **Allowlist as a filter, not a gift.** It measures how many people will
   actually transact, and gives supporters a reason to recruit. Keep criteria
   honest — handing spots to silent wallets destroys the signal.
   Typical window: **2–4 weeks**, closed with a clearly communicated cutoff.
4. **Do not punish the community at mint.** Gas wars, crashing mint pages,
   broken reveals, and overpricing relative to community size are the standard
   failure modes. Price off *recent comparable collections on the same chain*.
5. **Post-mint is the real marketing.** Holders are the channel. A roadmap you
   cannot deliver is worse than no roadmap.

Also verified: **paid promotion before organic traction almost never returns
its cost.** It works only as a multiplier on something already moving.

---

## 7. Risks, stated plainly

| Risk | Evidence |
|---|---|
| Arc is an institutional chain; degen NFT demand may never materialise | Circle's own positioning is payments/RWA/agents; no airdrop announced |
| "Hundreds of collections in two weeks" | direct quote from an OpenSea-adjacent builder |
| Arc has **no** native retail speculation culture yet | NFT slots on OpenSea are 90% LP position NFTs |
| Free mint = zero primary revenue | every reference winner was free; revenue came from royalties + secondary |
| $50k verification gate is real money of organic volume | OpenSea screens for wash trading |
| New-chain scam wave | Robinhood Chain saw fake contracts, honeypots, $56k individual losses, a hijacked founder account draining ~650 ETH within 9 days of launch |

### The honest bear case
Robinhood Chain worked for NFTs because it was a **retail trading brand** whose
users already speculated. Arc is a **B2B settlement chain** whose users are
BlackRock and Visa. The NFT wave may be much smaller. Anyone claiming a
guaranteed sell-out is guessing.

### The honest bull case
Circle is the #2 stablecoin issuer; Arc launched with the deepest institutional
validator set in crypto history and OpenSea on day one. Gas is ~4 cents.
The field is empty *today*. If even a fraction of the Robinhood Chain pattern
repeats, being first with something that actually uses the chain wins.
