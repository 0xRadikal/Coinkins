# 14 — B1 EXECUTION RESULTS: ✅ COMPLETE SUCCESS
**Date:** 2026-09-16
**Network:** Arc **MAINNET**, chainId 5042
**Result:** all 9 transactions succeeded. Both mint phases work.
**Total cost: $0.2248** (vs $1.14 projected — 80% under budget)

---

## 1. 🎯 THE HEADLINE — OPENSEA INDEXED IT

This was the open question of the entire project. **Answered: YES.**

```
GET api.opensea.io/api/v2/chain/arc/contract/0xd80266b6…a846   HTTP 200
{
  "address"           : "0xd80266b6f0c021e6a606a51d10c19e9c5cc9a846",
  "chain"             : "arc",
  "collection"        : "arc-pathfinder-test",
  "contract_standard" : "erc721",
  "name"              : "Arc Pathfinder Test"
}
```
Collection endpoint:
```
collection      arc-pathfinder-test
name            Arc Pathfinder Test
owner           0xa842e3ab069562db379c35dd52c77ef214324004   (us)
safelist_status not_requested
is_disabled     False
opensea_url     https://opensea.io/collection/arc-pathfinder-test
created_date    2026-09-16
contracts       [{address: 0xd80266b6…a846, chain: arc}]
stats           num_owners: 1, volume 0, sales 0
```

**Proven: deploying ERC721SeaDrop on Arc pointed at the canonical SeaDrop
produces a live, auto-indexed OpenSea collection with its own slug and URL.**

⚠️ `total_supply` reads 0 in OpenSea's API while the chain says 2 — indexer
lag on a minutes-old collection. Not a contradiction, just staleness.
⚠️ `volume_symbol: "ETH"` is an OpenSea display default, not a claim that
Arc uses ETH. Arc's gas/payment token is USDC (proven, doc 12).

---

## 2. ALL 9 TRANSACTIONS — EVERY ONE status 0x1

| # | tx | gas used | cost |
|---|---|---|---|
| 1 | deploy ERC721SeaDrop | 4,507,488 | $0.198958 |
| 2 | `setMaxSupply(1000)` | 49,076 | $0.002201 |
| 3 | `setBaseURI` | 95,880 | $0.004312 |
| 4 | `updateCreatorPayoutAddress` | 54,598 | $0.002468 |
| 5 | `updateAllowedFeeRecipient` | 99,990 | $0.004205 |
| 6 | `updateAllowList` (merkle) | — | $0.002388 |
| 7 | **`mintAllowList` PHASE 1 FREE** | — | $0.003939 |
| 8 | `updatePublicDrop` (0.1 USDC) | — | $0.002369 |
| 9 | **`mintPublic` PHASE 2 PAID** | — | $0.003923 |
| | **TOTAL** | | **$0.224763** |

Key tx hashes:
```
deploy        0x717a8030e952c2ab08e7ed61a0e6f8d13932e4655ebe6e540c3cdef5386fef11
mintAllowList 0x30e5d30dbeb86c1d…
mintPublic    0x67de2bc47826a45d…
```
**TOKEN CONTRACT: `0xd80266b6f0c021e6a606a51d10c19e9c5cc9a846`**

---

## 3. INDEPENDENT ON-CHAIN VERIFICATION

Read back fresh from chain by `verify_final.py` (trusting no prior output):

```
runtime code    19,805 bytes        (matches compiled artifact exactly)
name()          'Arc Pathfinder Test'
symbol()        'APFT'
maxSupply()     1000
totalSupply()   2
balanceOf(us)   2
owner()         0xa842e3ab069562db379c35dd52c77ef214324004

ownerOf(1) = 0xa842e3ab…4004    <- PHASE 1 allowlist mint
ownerOf(2) = 0xa842e3ab…4004    <- PHASE 2 paid mint
ownerOf(0) = <nonexistent>      <- ERC721A starts at id 1, not 0
```

### SeaDrop config, read from the canonical SeaDrop contract
```
merkleRoot on-chain 0x00662c925101d384f528e24b5fef91e19f68d08696d6577071e2963bae31c259
merkleRoot expected 0x00662c925101d384f528e24b5fef91e19f68d08696d6577071e2963bae31c259
MATCH: True

getPublicDrop(token):
  mintPrice                100000000000000000  = 0.100000 USDC
  startTime                1789573443
  endTime                  1790178213
  maxTotalMintableByWallet 5
  feeBps                   0
  restrictFeeRecipients    0
```
**The merkle root we computed offline matches what the canonical SeaDrop
stored. The allowlist mechanism is fully proven.**

---

## 4. 💰 COST — 80% UNDER BUDGET

```
projected (doc 13)   ~$1.14
actual                $0.224763
```
Reason: gas fell from ~101 gwei at planning time to ~31 gwei at execution.
**This is exactly why every gate re-reads gas live instead of hardcoding.**

```
started with    2.000000 USDC
balance now     1.775237 USDC
net change     -0.224763 USDC
```
**The 0.1 USDC mint payment returned to us in full** (we were the
`creatorPayoutAddress`, and `feeBps = 0` so OpenSea took nothing).
**Net loss = gas only.**

Deploy gas estimate accuracy: estimated 5,453,314 (incl. 1.2x headroom),
actual 4,507,488 → the raw estimate was ~4,544,428, i.e. **99.2% accurate**.

---

## 5. WHAT IS NOW PROVEN

- ✅ `ERC721SeaDrop` deploys on Arc mainnet and is accepted by canonical SeaDrop
- ✅ **Allowlist (merkle) mint works** — root computed offline, verified on-chain
- ✅ **Paid public mint works** with real value transfer in native USDC
- ✅ **Two overlapping stages coexist** (allowlist open while public opened)
- ✅ Token-side → SeaDrop-side config forwarding works as the source implied
- ✅ `msg.value` payment model works (no ERC-20 approve needed)
- ✅ **OpenSea auto-indexes Arc collections** with slug + URL
- ✅ Real gas costs for a full 1000-supply setup: **~$0.22**
- ✅ Payment routes back to `creatorPayoutAddress` correctly

## 6. STILL NOT PROVEN
- ⬜ Whether OpenSea's **drop UI renders a mint button** (API indexing ≠ UI)
- ⬜ ERC-20 USDC **6-decimal** path (unused; native 18-dec is what SeaDrop takes)
- ⬜ Secondary-market trading / royalty enforcement
- ⬜ `tokenURI(0)` returned None — expected, id 0 does not exist. ⬜ Did not
  re-test `tokenURI(1)`; metadata rendering unverified.
- ⬜ Anything about **demand**

---

## 7. ⚠️ IMPORTANT LIMITS OF THIS ARTIFACT

- This collection has `maxSupply 1000` with only **2 minted** → the
  "all items minted/revealed" criterion **fails permanently**.
  **It can never get a blue check. That was intentional.**
- It is **permanent and public** on Arc mainnet under a throwaway name,
  exactly as planned, so the real `Coinkins` brand is untouched.
- `baseURI` points at a placeholder; there is no real art or metadata.

**Do not treat `arc-pathfinder-test` as anything but a proving harness.**

---

## 8. IMPLICATIONS FOR THE REAL LAUNCH

1. **Technical risk is now ~zero.** Every contract-level step is proven on
   mainnet for $0.22. The remaining risk is entirely **demand**, not code.
2. **Cost of the real launch is trivial** — a 1000-supply configured drop
   costs ~$0.22 in gas. Budget is a non-issue.
3. **Supply must be small enough to sell out**, because "all items minted"
   is mandatory. Doc 05's 1,000 @ $50 = $50,000 clears the gate *only on a
   full sellout*.
4. **The blue-check gate is unchanged:** $50,000 volume including mint.
   Measured reality (doc 07): Arc has **0 verified collections and 0 volume**.
   Nothing in B1 changes that. **B1 proved the machine works; it proved
   nothing about buyers.**

## 9. FILES
```
deploy_b1.py             9-tx executor, 7 gates, resumable via b1_state.json
verify_final.py          independent chain read-back
build_allowlist.py       merkle root (dual-implementation verified)
allowlist_phase1.json    exact MintParams + root + proof
b1_state.json            tx log with hashes and per-tx cost
```
