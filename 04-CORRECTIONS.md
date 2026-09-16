# 04 — CORRECTIONS TO MY OWN EARLIER WORK
Written 2026-09-16 after re-verification on the CORRECT RPC endpoints.
Anything in docs 01–03 that contradicts this file is WRONG. This file wins.

---

## C-1. I was querying RPC endpoints that do not exist

Docs 01–03 cite "live Arc reads". The endpoints I had used are dead:

```
https://rpc.arc.network      -> HTTP 000 (no response)
https://rpc.arc.build        -> HTTP 000
https://rpc.circle.com/arc   -> HTTP 000
arc-mainnet.rpc.caldera.xyz  -> HTTP 404
```

The REAL endpoints, found via the official `circlefin/arc-node` repo:

```
MAINNET  https://rpc.mainnet.arc.io   chainId 0x13b2   = 5042
TESTNET  https://rpc.testnet.arc.io   chainId 0x4cef52 = 5042002
```

**Consequence:** every number in docs 01–03 had to be re-measured.
Some survived, one did not (see C-3).

---

## C-2. Block height: my number was right, my explanation was absent

I reported head ≈ 21,162,317. That looked impossible for a chain
"launched today", so I tested it:

```
genesis block timestamp = 0x6a026d80 = 2026-05-12 00:00:00 UTC
measured block time     = 0.500 s  (40 blocks in 20 s, measured live)
21,168,921 blocks x 0.5 s = 122.5 days
2026-05-12 -> 2026-09-16  = 127 days
```

Consistent. **Arc has been producing blocks since 12 May 2026** in a
permissioned phase; 16 September 2026 is when the mainnet opened to the
**public**. The chain is ~4 months old, not 0 days old.

This matters strategically: Arc is not a blank slate. See C-4.

---

## C-3. ❌ THE GAS NUMBER IN DOC 03 IS WRONG

Doc 03 states baseFee is **103.13 gwei** and that ~155 gwei is the floor.
Re-measured on the real mainnet RPC:

```
eth_gasPrice = 0xeeaf31b23 = 64.07 gwei
```

Earlier observations ranged 103.13–213.96 gwei. So the true picture is
**a volatile fee market roughly 64–214 gwei**, not a fixed 103.

**The rule stands and is now better justified: NEVER hardcode gas.**
Read `baseFeePerGas` at send time and multiply by 1.5–2. Both Option A's
20 gwei and my own 155 gwei would be wrong at different times of day.

---

## C-4. ❌ "THE COMPETITIVE FIELD IS EMPTY" IS FALSE

Doc 01 claims all Arc collections are LP NFTs or supply=0. That is wrong.
Live query of OpenSea's API:

```
GET /api/v2/collections?chain=arc&limit=100  -> HTTP 200, 100 collections
```

Real names: Core Heat, Hash Friends, ArcCitizens, RichGirlsClub, Arcatrium,
HoodPunksArc, NormiesARC, BeMisfits, ARC MACHINES, ARCTRUM, Mr.Stonk,
Arc Punk, Pixel Realms, Arc Fuzzies, Nullheads, zooklandia, Arc Horizon,
Arc bears, Hero Arc, ARCAT, Broke Bookies, sharclings, Rare Arc Family…

Field composition (measured):
| Metric | Value |
|---|---|
| Collections on page 1 | 100 |
| With "arc" in the name | 36 (36%) |
| Duplicate names (same creator spamming) | 12 |

**The field is crowded but WORTHLESS.** See C-5.

---

## C-5. The field is crowded yet has zero economic activity

Queried `/collections/{slug}/stats` for 30 Arc collections:

```
collections with total volume > 0      : 0 / 30
collections with total volume > $5,000 : 0 / 30
collections with zero sales entirely   : 23 / 30
SUM of all volume across top 30        : 0.00
```

**Control test** (proves the API field works and 0 is real, not a bug):
```
boredapeyachtclub  total_vol = 1,581,643   sales = 57,503
azuki              total_vol =   831,547   sales = 92,500
pudgypenguins      total_vol =   521,157   sales = 92,223
```
The field returns real numbers for real collections. **Arc's zero is real.**

Some Arc collections show sales>0 with volume=0 (Nullheads 1,269 sales,
arc-fuzzies 833, mr-stonk 697) — that is the signature of **free mints**:
many claims, no money changing hands.

**Strategic read:** 100 competitors, none monetising. Being "first" is
already lost. Being **the first to actually sell** is wide open.

---

## C-6. ⚠️ THE BLUE CHECK RULE — my most important correction

Doc 03 treats the $50k gate as needing secondary sales. I extracted the
full criteria list from OpenSea's own page (it renders via JS; I pulled it
out of the raw HTML payload):

> * A username
> * A profile picture and banner image
> * A verified email address
> * A connected, active, and affiliated social media presence
>   — a connected Twitter account, **or** a collection with an active Discord
> * Ownership of at least one collection with:
>   * **At least $50,000 USD (or equivalent) in total volume, INCLUDING
>     MINT VOLUME on OpenSea AND secondary sales volume**
>   * A title / A banner / A logo image
>   * **All collection items minted/revealed**

And the post-application review:
> * Unique purchases by buyers in the last 30 days
> * **No significant inorganic sales volume**
> * **Organic owner to item ratio**
> * "We may deny badging if we believe the creator has artificially
>   inflated collection buying and selling volume."

### Why this reverses my recommendation

**MINT VOLUME COUNTS TOWARD THE $50,000.**

My earlier "free mint" advice makes the gate nearly unreachable:

| Structure | Mint volume | Secondary needed | Verdict |
|---|---|---|---|
| 1,500 free | **$0** | **$50,000** | 30% resold @ $25 = $11,250 → **SHORT** |
| 1,500 free | $0 | $50,000 | 50% resold @ $25 = $18,750 → **SHORT** |
| 2,000 @ $25 | **$50,000** | $0 | **GATE CLEARED AT MINT** |
| 1,500 @ $35 | **$52,500** | $0 | **GATE CLEARED AT MINT** |
| 1,000 @ $50 | **$50,000** | $0 | **GATE CLEARED AT MINT** |

A free mint forces you to depend on strangers reselling to each other.
A paid sell-out clears the gate **on mint day**.

Also note: **"All collection items minted/revealed"** is a hard requirement.
An unsold, partially-minted collection is ineligible regardless of volume.
That is a strong argument for a **small supply you can actually sell out**.

---

## C-7. ❌ The 25 ETH figure circulating online is outdated

OpenSea tweeted (31 Oct 2024) that they "lowered our secondary volume
requirement to 25E". Do not trust it. Their support page — **updated
12 Aug 2026** — says $50,000 USD. The live document beats the old tweet.

---

## C-8. A bug in my own availability checker (fixed)

`check_names.py` v2 probed each surface once. On transport failure it
returned `None`, and under load some probes silently mis-reported.

Caught by cross-checking with curl:
```
check_names.py said : Kopperz  X = free
curl proved         : x.com/kopperz -> HTTP 200  = TAKEN
```

**Had I not cross-checked, I would have recommended a taken handle.**

v3 fixes this: 3 retries with backoff, requires two AGREEING reads across
`x.com` and `twitter.com`, and prints `???` loudly rather than guessing.
Regression-tested: `Kopperz` now correctly reports TAKEN.

---

## C-9. Withdrawn: the Instagram availability claim

Instagram returns HTTP 200 for handles that cannot exist:
```
strikelings       -> 200  (626,451 bytes)
zzqqxxnope918273  -> 200  (626,462 bytes)   <- nonsense handle
```
Status carries no signal. **Any Instagram claim I made is withdrawn.**
Check it manually in a browser.

---

## C-10. What I could NOT verify (stated plainly)

| Item | Status | Why |
|---|---|---|
| Robinhood Chain volume benchmark | **UNVERIFIED** | API returned HTTP 401 on 3 retries (rate limit). My earlier "StonkBrokers beat BAYC floor" claim is **unconfirmed** — treat as rumour, not data. |
| USPTO / WIPO trademark | **UNVERIFIED** | No reliable tool here. You must do this. |
| Instagram handles | **UNVERIFIED** | See C-9. |
| Discord vanity | Weak evidence | Payload-size heuristic only; needs Boost L3 anyway, non-blocking. |
| Whether OpenSea lists Arc collections on the front end | Partially | API confirms `chain: "arc"` is supported and returns collections. |

### Verified beyond doubt
```
OpenSea supported chains include:  {"chain":"arc","name":"Arc Chain",
  "symbol":"USDC","supports_swaps":true,
  "block_explorer_url":"https://explorer.arc.io"}

Arc mainnet infrastructure (eth_getCode on rpc.mainnet.arc.io):
  Seaport 1.6       0x0000000000000068F116a894984e2DB1123eB395   23,981 B  LIVE
  SeaDrop           0x00005EA00Ac477B1030CE78506496e8C2dE24bf5   21,081 B  LIVE
  CreateX           0xba5Ed099633D3B313e4D5F7bdc1305d3c28ba5Ed   11,838 B  LIVE
  Permit2           0x000000000022D473030F116dDEE9F6B43aC78BA3    9,152 B  LIVE
  Multicall3        0xcA11bde05977b3631167028862bE2a173976CA11    3,808 B  LIVE
  ERC-6551 Registry 0x000000006551c19487814612e58FE06813775758        0 B  ABSENT
```
ERC-6551 being absent is re-confirmed on the correct RPC. If the roadmap
needs token-bound accounts, **we must deploy the registry ourselves**.
