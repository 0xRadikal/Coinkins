# Option A vs Option B — verdict from measured data

Not opinion. Every claim below was tested against the live chain or live
registries on 2026-09-16.

---

## 1. The decisive test: are Option A's names even available?

Option A proposed `Planchet` as primary, with `Assay`, `Mintage`, `Ducat` as
fallbacks — and admitted it could not verify availability.

I verified. Twice, through two independent domains (`x.com` and `twitter.com`),
plus DNS and the OpenSea API.

| Name | X handle | .xyz | .io | .com | OpenSea slug |
|---|---|---|---|---|---|
| **Planchet** | **TAKEN** (200) | free | TAKEN | TAKEN | free |
| **Assay** | **TAKEN** (200) | TAKEN | TAKEN | free | free |
| **Mintage** | **TAKEN** (200) | TAKEN | TAKEN | TAKEN | free |
| **Ducat** | **TAKEN** (200) | TAKEN | TAKEN | TAKEN | free |

Cross-check output:
```
@planchet  ['x.com/:200', 'twitter.com/:200']  => TAKEN
@assay     ['x.com/:200', 'twitter.com/:200']  => TAKEN
@mintage   ['x.com/:200', 'twitter.com/:200']  => TAKEN
@ducat     ['x.com/:200', 'twitter.com/:200']  => TAKEN
```

**All four of Option A's names are unavailable on X.** Its own suggested
fallbacks (`@planchetxyz`, `@0xplanchet`) are the weak pattern — a handle that
does not match the brand costs recognition and looks like a copycat.

Option A's reasoning was sound. Its facts were unverified, and wrong.

---

## 2. A dangerous technical error in Option A

Option A advised:
> "set maxFeePerGas explicitly above 20 gwei"

Measured on Arc mainnet at the same moment:
```
live gasPrice : 103.13 gwei
live baseFee  : 103.13 gwei
```

**20 gwei is 5x BELOW Arc's baseFee. A transaction with that cap would never
be mined.** On mint night that is a total loss of the launch window — the exact
class of bug that cost us on Rare Friends (see `00-ARCHIVE`).

Correct floor is ~155 gwei (1.5x baseFee), i.e. **8x higher** than advised.
And it must not be hardcoded at all: read `baseFeePerGas` live and multiply.

### Option A's other claims, checked
| Claim | Verdict |
|---|---|
| "Verify ERC-6551 on Arc, don't assume" | ✅ **Correct and important.** I verified: registry at `0x000000006551...5758` has **0 bytes** = not deployed |
| "USDC native 18 dec vs ERC-20 6 dec" | ✅ **Correct and critical.** Gas math confirms 18-dec native accounting (200k gas x 103 gwei = 0.0206 native; at 6 dec that would be 20.6 billion USDC = absurd) |
| "Arc may differ on SELFDESTRUCT / singleton factories" | ⚠️ Partly moot — **CreateX is deployed** (11,838 B), so deterministic deploys work |
| "maxFeePerGas above 20 gwei" | ❌ **Wrong and dangerous** |
| "Launch in the second wave, not day one" | ✅ **Correct.** StonkBrokers launched 16 days after Robinhood mainnet, not day 1 |
| "Supply 1,000–2,000, small supply helps reach $50k" | ✅ **Correct arithmetic.** 1,000 items at $50 floor reaches $50k far easier than 10,000 at $2 |
| "Batched raffle over FCFS" | ✅ **Correct** — avoids gas wars and bot dominance |
| "Commit-reveal with pre-published provenance hash" | ✅ **Correct** — standard anti-sniping practice |
| "Budget to survive 30% sell-through" | ✅ **Correct.** Only 1 of Robinhood's first 7 collections truly ran |

---

## 3. What Option B (mine) got right and wrong

| Point | Verdict |
|---|---|
| Arc brand guidelines forbid "Arc" in product names | ✅ Verified from two primary sources; competitors are in direct violation |
| Naming data: median 2 words / 11 chars | ✅ Measured from 11 top collections via OpenSea API |
| `Ledgerlings` / `Wagelings` fully free | ✅ Verified on all five surfaces |
| Warned `-lings` is becoming a generic meta | ✅ Honest — and Option A implicitly agrees by avoiding it |
| Did **not** supply supply/price/anti-bot specifics | ❌ Option A was more complete here |
| Did **not** mention trademark search (USPTO/WIPO) | ❌ Real gap; Option A was right to raise it |
| Did **not** warn that OpenSea ToS lets them reassign usernames | ❌ Real gap |

---

## 4. Verdict

**Neither is fully right. The correct answer is Option A's *discipline* applied
to Option B's *verified facts*.**

- Option A's **process** is better: trademark search, testnet dress rehearsal,
  batched raffle, commit-reveal, second-wave timing, 30% downside budgeting.
- Option A's **facts** are unverified and one is actively dangerous (20 gwei).
- Option B's **facts** are measured, but the plan was thinner on mechanics.

### Which is "easier and more profitable"?
Profit does not come from the name. It comes from: small supply + free mint +
real secondary demand + royalties. Option A's **1,000–2,000 supply** is the
more profitable structure than my original 5,000, for one verified reason:

> OpenSea's verification gate is **$50,000 of volume sold**.
> 1,000 items needing a ~$50 average sale price is achievable.
> 5,000 items needing a ~$10 average across 35–45% of supply is harder to hold.

So I am **revising my own recommendation down to 1,500 supply.**

---

## 5. Final name recommendation

Available on **all five surfaces** (X + .xyz + .io + .com + OpenSea slug):

| Name | Chars | Meaning | Notes |
|---|---|---|---|
| **Strikelings** | 11 | "strike" = the exact minting term for stamping a coin | coin-metaphor like Option A wanted, but actually available |
| **Ledgerlings** | 11 | ledger = Arc's core financial primitive | exactly the median length of top collections |
| **Dollarlings** | 11 | Arc is a stablecoin chain; gas is USDC | most literal to the chain's thesis |
| **Denomlings** | 10 | denomination — coin face value | most abstract/brandable |
| **Coinlings** | 9 | plain and global | .com is taken, rest free |

Also free but weaker: Wagelings, Quorumlings, Coinwrights, Escrowlings,
Numismat (X taken), Seigniorage (X taken).

### My pick: **Strikelings**
It satisfies Option A's actual insight — *coin-minting vocabulary carries
credibility with real collectors* — while being the one such name that is
genuinely free everywhere. "Strike" doubles as the minting verb and as a
holder term ("strikes"), which Option A itself proposed for Planchet.

Identity if approved:
```
Project / brand : Strikelings
OpenSea profile : strikelings
Collection name : Strikelings          (brand == collection, better for OpenSea search)
Collection sub  : Genesis Strike
X handle        : @strikelings         (verified 404 = free)
Domain          : strikelings.xyz  (+ .io and .com also free - take all three)
Holder term     : "strikes"
Positioning     : "Strikelings is built on Arc."   <- brand leads, Arc is infrastructure
Future ticker   : STRK is taken by Starknet -> use STRIKE or avoid a token entirely
```

⚠️ **Caveat I will not hide:** availability was verified at 13:30 UTC on
2026-09-16. Handles get taken continuously. Re-verify immediately before
registering, and register **all surfaces in one sitting** before saying the
name publicly anywhere.

⚠️ **Not verified by me:** USPTO/WIPO trademark search (classes 9 and 42).
I have no reliable tool for that here. Do it before committing.

⚠️ **OpenSea ToS:** they reserve the right to disable an account and reassign
its username and URL. Username ownership is not absolute. Option A was right
to flag this.

---

## 6. Merged execution plan (Option A's rigor + verified numbers)

### Step 1 — Lock the name (today, before anything else)
- [ ] Re-run `check_names.py Strikelings` to confirm still free
- [ ] USPTO TESS + WIPO Global Brand DB search, classes 9 & 42
- [ ] Register in ONE sitting: X handle, .xyz/.io/.com, OpenSea username, Discord
- [ ] Do not publish the name anywhere until all of the above are secured
- [ ] No art, no contract, no site before this step is green

### Step 2 — Technical dress rehearsal on Arc testnet
- [ ] Deploy the canonical **ERC-6551 registry** (0 bytes on mainnet = we'd be first)
- [ ] Confirm `CreateX` deterministic deploy path works (it is deployed: 11,838 B)
- [ ] **Gas: never hardcode.** Read `baseFeePerGas` live, use 1.5–2x.
      Current baseFee is **103 gwei**, not 20.
- [ ] Decimal test: native accounting is **18 dec**; ERC-20 USDC is **6 dec**.
      Get this wrong and the error is a factor of 10^12.
- [ ] Pull-payment withdrawal pattern, not push
- [ ] Full end-to-end mint on testnet before touching mainnet

### Step 3 — Collection parameters (revised down, per Option A's logic)
| Parameter | Value | Why |
|---|---|---|
| Supply | **1,500** | $50k gate needs ~$33 avg per item, not $10 |
| Price | **free** (gas only, ~$0.02) | every winner on the last new chain was free |
| Per wallet | **1** | maximises unique holders = secondary depth |
| Distribution | **batched raffle, 24–48 h window** | no gas war, no bot dominance |
| Reveal | block after mint, provenance hash pre-published | anti-sniping |
| Royalty | **5%** | this is the revenue model, since mint is free |
| Mint rail | **SeaDrop** (already live on Arc, 21,081 B) | no custom mint contract needed |

### Step 4 — Community (Option A's approach, kept)
- [ ] X + Discord, Guild.xyz for role gating
- [ ] Batch-based allowlist, earned not farmed
- [ ] Partner with the 1–2 Arc collections that still have life after a week

### Step 5 — Timing: second wave, not day one
StonkBrokers launched **16 days** after Robinhood mainnet and beat BAYC's floor.
Arc mainnet went live 2026-09-16. **Target launch: 2026-10-01 to 2026-10-07.**
This also gives the field time to flood with follow-farm jpegs so we stand out.

### Step 6 — Verification path
- [ ] Apply at `opensea.io/settings/verification` once $50k volume sold
- [ ] Pursue `opensea.io/partners` in parallel — partners can be badged without
      meeting the threshold
- [ ] **Never wash-trade.** OpenSea states explicitly they deny badging for
      artificially inflated volume. Unrecoverable.

---

## 7. Budget reality

Option A's warning is correct and I am repeating it: **build the budget so 30%
sell-through does not ruin you.** Of Robinhood Chain's first seven NFT
collections, exactly one became StonkBrokers. The other six are footnotes.

Costs on Arc are trivial (deploy ~$0.53, mint ~$0.02). The real spend is time
and art. Keep cash outlay near zero until secondary volume proves demand.

---

## 7. Final verification log + methodology corrections (2026-09-16)

### 7.1 Fresh re-check of the two finalists

```
name             X      .xyz   .io    .com   OS slug
Strikelings      free   free   free   free   free
Ledgerlings      free   free   free   free   free
```

### 7.2 Control test — proof the checker is not just printing "free"

A checker that returns "free" for everything is worthless. Control run:

```
azuki            TAKEN  TAKEN  TAKEN  TAKEN  TAKEN
pudgypenguins    TAKEN  TAKEN  TAKEN  TAKEN  TAKEN
Planchet         TAKEN  free   TAKEN  TAKEN  free
Ducat            TAKEN  TAKEN  TAKEN  TAKEN  free
```

The checker correctly separates taken from free. Option A's names re-confirmed
TAKEN on X on a second independent run.

### 7.3 Redirect resolution (the 301s were not failures)

```
twitter.com/strikelings  -> 301 -> x.com/strikelings      -> 404  = FREE
discord.gg/strikelings   -> 301 -> discord.com/invite/... -> 200  = see 7.4
```
The 301 is just twitter.com -> x.com. Following it lands on a real 404.
X handle `@strikelings` is confirmed free through two independent entry points.

### 7.4 CORRECTION — two checks I initially misread

**Instagram check is INVALID. Discarded.**
```
strikelings       -> HTTP 200  bytes=626451
azuki             -> HTTP 200  bytes=727886
zzqqxxnope918273  -> HTTP 200  bytes=626462   <- nonsense handle ALSO 200
ledgerlings       -> HTTP 200  bytes=626450
```
A handle that cannot possibly exist returns 200 with a byte count within 11
bytes of our candidates. Instagram serves a login/JS shell to unauthenticated
clients, so HTTP status carries no signal. **Any earlier "Instagram free"
claim is withdrawn — it was never measured.**

**Discord check is WEAK, not proof.**
```
discord.gg/azuki             bytes=24303   <- real invite, embeds server metadata
discord.gg/strikelings       bytes=18357
discord.gg/ledgerlings       bytes=18381
discord.gg/zzqqxxnope918273  bytes=18381   <- nonsense baseline
```
Real invites are clearly distinguishable by payload size. Our candidates sit at
the nonsense baseline, so no server holds that vanity URL. But `discord.gg`
vanity URLs require Server Boost Level 3 and are not reserved by name, so this
is not a namespace we can "lose". Treated as non-blocking.

### 7.5 What is actually verified vs not

| Surface | Strikelings | Confidence |
|---|---|---|
| X / Twitter handle | FREE | **High** — 404 via two independent domains, control-tested |
| .xyz / .io / .com / .art | FREE | **High** — DNS, control-tested against known-registered |
| OpenSea slug | FREE | **Medium** — API 401/404 for unknown slugs; only settles at registration |
| Discord vanity | FREE | Low-Medium — payload heuristic; non-blocking either way |
| Instagram | **UNKNOWN** | **None** — check invalid, must be done manually in a browser |
| USPTO / WIPO trademark | **UNKNOWN** | **None** — no tool available here; you must do this |

**Bottom line: nothing blocking found. Two items remain genuinely unverified
(Instagram, trademark) and I am not going to pretend otherwise.**
