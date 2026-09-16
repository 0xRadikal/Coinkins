# Arc NFT Launch — Strategy & Concept

Built on the verified findings in `01-ARC-RESEARCH.md`. Every recommendation
traces back to something measured, not assumed.

---

## The one insight that decides everything

**Arc is not a degen chain. It is Circle's institutional settlement layer.**
Validators are BlackRock, Visa, Mastercard, NYSE. Stated use cases are
tokenization, FX, credit, treasury, prediction markets, and **AI-agent
economic activity**. Gas is paid in **USDC**.

Copying a Robinhood-Chain-style animal PFP onto Arc is fighting on the wrong
terrain. The winner on Robinhood Chain was **StonkBrokers** — and it won for
exactly one reason: **it was the chain's own thesis turned into an NFT.**
A stock-trading chain got an NFT that *was a brokerage account* (ERC-6551
token-bound accounts pre-loaded with tokenized TSLA/NVDA/AAPL). Floor beat
BAYC. $4.7M volume.

So the question is not "what jpeg should we draw."
It is **"what is Arc's thesis, and what NFT *is* that thesis?"**

Arc's thesis, in Circle's own words: *programmable dollars + autonomous AI
agents settling value in real time.*

---

## Verified infrastructure position (this shapes what is buildable)

Checked on-chain at chainId 5042:

| Contract | Status | Consequence |
|---|---|---|
| Seaport 1.6 | **LIVE** (23,981 B) | secondary trading on OpenSea works |
| **SeaDrop 1.0** | **LIVE** (21,081 B) | we get 4 mint phases for free: public / allowlist(merkle) / signed / token-gated |
| ERC721SeaDrop impl | **LIVE** (21,257 B) | same implementation Robinhood collections cloned |
| CreateX | LIVE | deterministic deploys |
| Multicall3 | LIVE | cheap batch reads for a mint site |
| Permit2 | LIVE | gasless approvals |
| **ERC-6551 Registry** | **NOT DEPLOYED** | the StonkBrokers primitive is unavailable — **but the registry is permissionless, so whoever deploys it is first** |
| SeaDrop clone factory | not deployed | we deploy our own ERC721SeaDrop, not a clone |

Two strategic gifts hidden in that table:
1. **SeaDrop is already live** → we can run a professional phased mint natively
   on OpenSea, with no custom mint contract and no custom mint site required.
2. **ERC-6551 is missing** → deploying the canonical registry ourselves makes us
   the first token-bound-account collection on Arc. That is a genuine
   "first" that is technically true, not marketing fluff.

Cost reality: mint ≈ **$0.04**, full collection deploy ≈ **$0.53**.
Money is not the constraint. Attention is.

---

## Concept recommendation

### ⭐ Primary: **"Agents"** — an NFT that is a real on-chain AI-agent wallet

**One-sentence pitch:** Each Agent is an NFT that owns its own USDC wallet on
Arc, with an on-chain spending policy — the first collection where the NFT
*is* the autonomous economic actor Circle built Arc for.

Why this is the right answer:

| Arc's actual thesis | What the NFT does |
|---|---|
| "Agentic economic activity" — Circle's #1 differentiator | Each NFT owns an ERC-6551 token-bound account = an agent wallet |
| Gas and value are **USDC** | Each Agent is seeded with a small USDC balance at mint |
| "Predictable dollar-based fees, payments like API calls" | Agents can pay each other; wallet-to-wallet USDC flows are the collection's activity |
| "Spend limits, delegate onchain tasks" (Arc Portal's own feature) | On-chain policy per Agent: daily cap, allowlisted counterparties |
| Prediction markets, FX, lending are live use cases | Agents can be delegated into those protocols later |

**Mechanics (deliberately simple, all shippable):**
- Supply **5,000**. Enough for a real holder base and a $50k volume path;
  small enough to stay scarce. (StonkBrokers 4,444 / Chain Mancers 5,000.)
- **Free mint**, 1 per wallet. Every reference winner on the last new chain was
  free or sub-$10 and repriced 10–100x. Free maximises holder count, which is
  what drives secondary volume — which is what OpenSea's $50k gate measures.
- **Each Agent is minted with its ERC-6551 account already created**, holding a
  seed of USDC (e.g. $0.25–$1). Small, but it makes the claim literally true:
  *your NFT has money in it.* This is the StonkBrokers trick, minus the
  reflexive token-peg that destroyed StonkBrokers' floor.
- **Traits are functional, not cosmetic**: each Agent has a `role`
  (Settler / Router / Oracle / Treasurer / Arbiter), a `daily limit`, and a
  `trust tier`. Rarity = higher limits and more capable roles.
- **No project token.** This is the deliberate anti-StonkBrokers decision:
  their floor was a formula pegged to their token and fell 26% in a week when
  the token fell. We keep the floor a real market price.
- Phase 2 (only after phase 1 ships): Agents can be **delegated** — an owner
  authorises their Agent to execute a policy inside a live Arc protocol
  (Aave/Morpho are already on Arc). Yield or fees accrue *into the NFT's own
  wallet*, transferring with the NFT on sale.

**Art direction:** institutional-terminal aesthetic — monospace, grid,
ledger-green/amber on near-black, each Agent rendered as a machine-readable ID
card with its policy printed on it. Generated fully on-chain as SVG where
possible (so "fully on-chain" is also true). This deliberately looks like
Arc/Circle's own design language, not like a Robinhood Chain cartoon.

### Alternative if you want something lighter to execute

**"Receipts"** — 5,000 fully on-chain SVG NFTs, each one a stylised payment
receipt for a real transaction that happened in Arc's genesis blocks. Trait =
the actual block/tx it commemorates. Cheap to build, genuinely native to the
chain, strong "day-one artifact" collectibility. Weaker long-term utility than
Agents, but far less engineering.

### What NOT to build (evidence-based)
- ❌ Another animal/pixel PFP with a roadmap of "staking + token + game."
  The field will have hundreds within two weeks; a builder with reach already
  said publicly he will scroll past exactly this.
- ❌ A token-pegged AMM floor (the StonkBrokers model). It manufactures a
  headline floor and unwinds at the same speed. Verified: −26% in one week.
- ❌ Anything requiring an airdrop narrative. Circle has announced no ARC
  airdrop; building on that is building on a rumour.

---

## Launch plan

Timeline assumes a **14–21 day** runway. Arc mainnet went live 2026-09-16, and
the competitive window closes in roughly two weeks.

### Phase 0 — Foundation (days 1–3)
- [ ] Lock the concept and write the two-sentence positioning. If it does not
      survive being said out loud, it is not ready.
- [ ] Secure handles: X, Discord (or deliberately no Discord), domain.
- [ ] Deploy the **ERC-6551 registry** to Arc (permissionless, canonical
      bytecode, deterministic address). This is a real, verifiable "first."
- [ ] Deploy `ERC721SeaDrop` on Arc + create the OpenSea collection page.
      SeaDrop is already live, so no custom mint contract is needed.
- [ ] Testnet dress rehearsal of the full mint, end to end.

### Phase 1 — Credibility before audience (days 3–10)
The research is unambiguous: **50 real people beat 5,000 followers**, and
**paid promotion before organic traction never returns its cost.**
- [ ] Publish a technical thread that *proves* something, not one that promises.
      e.g. "We deployed ERC-6551 to Arc. Here is the address. Here is the first
      NFT on Arc that owns a USDC wallet. Verify it yourself."
      Builders reshare verifiable firsts; they ignore mint dates.
- [ ] Ship a working demo page: connect wallet → see a live Agent → watch its
      wallet receive USDC. A working thing is the marketing.
- [ ] Manual outreach to the Arc builder community: `community.arc.io`, the
      Arc Discord (`discord.com/invite/buildonarc`), Arc House events.
      Participate for real, do not broadcast.
- [ ] Get listed on `nftcalendar.io` (it already runs a Robinhood/Arc drop feed)
      and the Arc ecosystem pages.

### Phase 2 — Allowlist as a filter (days 10–17)
Allowlists measure who will actually transact. Keep criteria **honest**.
- [ ] **Tier A — Earned (guaranteed).** Deploy-verified builders on Arc, people
      who shipped something, active Arc Discord contributors, and holders of a
      small set of respected collections. Manual review.
- [ ] **Tier B — Contributed (guaranteed).** People who produced something real:
      art, a thread that taught something, a tool, a translation. Not "like and
      retweet." This is the single biggest differentiator from the hundreds of
      follow-farm collections.
- [ ] **Tier C — FCFS.** Open list, first-come-first-served, capped.
- [ ] Publish the exact cutoff time and honour it. Ambiguity in the final days
      converts directly into negative sentiment.
- [ ] Target ratio: allowlist demand ≈ **1.5–2x** supply. Higher and the public
      phase is pointless; lower and the mint looks failed.

### Phase 3 — Mint (day ~18)
Use SeaDrop's native phases — already deployed, battle-tested, and it means the
mint happens **on OpenSea itself**, which is where the audience already is.
| Phase | Mechanism | Window | Supply |
|---|---|---|---|
| Allowlist A+B | `mintAllowList` (merkle) | 6 h | 60% |
| Allowlist C | `mintAllowList` (merkle) | 6 h | 20% |
| Public | `mintPublic`, 1/wallet | until out | 20% |
- Free mint, 1 per wallet, all phases. Gas ≈ 4 cents so nobody is priced out.
- Set royalty to **5%** (OpenSea's default max for creator earnings). Royalties
  are the revenue model, since the mint is free.
- Pre-announce exact UTC times. Publish them on-chain (`getPublicDrop`) so
  third-party tools and bots read the truth — and **never move the window**.
  (Rare Friends moved theirs twice and lost community trust.)

### Phase 4 — The $50k path to verification (days 18–45)
OpenSea's gate: **$50,000 of volume sold**, organic, plus activity and social
presence. Do the arithmetic honestly:
- 5,000 free mints → target **35–45% of supply trading at least once** in the
  first month at an average of ~$25–30 → $45k–65k. That is the realistic path.
- Levers that are legitimate: a real secondary reason to buy (Agent wallets
  accrue value), holder-only phase-2 access, consistent shipping.
- **Do not wash-trade.** OpenSea states explicitly they screen for artificially
  inflated volume and will deny badging. It is the one unrecoverable mistake.
- Also pursue the **partner route** (`opensea.io/partners`) in parallel —
  partner collections can be badged *without* the volume threshold.
- Apply the moment eligible; decisions come in ~7 days, re-apply after 7.

### Phase 5 — Post-mint (ongoing)
- Holders are the marketing channel. A roadmap you cannot deliver is worse than
  no roadmap.
- Ship the delegation feature. One shipped feature beats ten promised ones.
- Weekly verifiable updates (addresses, tx hashes, numbers), not vibes.

---

## Honest risk assessment

| Risk | Severity | Mitigation |
|---|---|---|
| Arc has no retail speculation culture; NFT demand may be far smaller than Robinhood Chain | **High** | Target Arc's *builder* audience, not degens. Free mint means no one loses money. Volume target is modest, not moonshot. |
| Hundreds of competing launches in 2 weeks | High | Differentiate on a verifiable technical first (ERC-6551 on Arc), not on art volume |
| $50k organic volume is genuinely hard | High | Free mint maximises holders; pursue partner route in parallel; never fake volume |
| We deploy ERC-6551 and nobody cares | Medium | It still gives a true "first" claim and real utility; cost is ~$1 |
| Scam clones of our collection | Medium | Publish the contract address everywhere; Robinhood Chain saw fakes within 9 days |
| Free mint = no primary revenue | Medium | Accepted by design. Revenue = 5% royalties on secondary. Every winner on the last new chain was free. |
| Team is anonymous with no track record | Medium | Spritehood made $1.28M largely on a known founder's name. We compensate with *shipped proof* instead of reputation. |

### What I will not claim
- I cannot promise a sell-out. Robinhood Chain's NFT wave worked because its
  users were retail traders who already speculated. Arc's users are banks.
  That difference is real and unknowable in advance.
- Anyone guaranteeing a blue check or a specific floor is guessing.
- The $50k threshold is the *minimum to apply*; approval is discretionary.

---

## Immediate decision needed from you

Before I build anything, three choices are yours:

1. **Concept**: Agents (higher ceiling, more engineering) or Receipts
   (faster, simpler, lower ceiling)?
2. **Supply & price**: I recommend 5,000 and free. Confirm or change.
3. **Identity**: anonymous or doxxed? It materially changes the marketing plan.

Once those are locked I can, in order:
- deploy the ERC-6551 registry to Arc and verify it on-chain,
- deploy the ERC721SeaDrop collection and configure phases,
- build the mint/demo site,
- generate the art and metadata,
- and write the allowlist tooling.
