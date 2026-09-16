# 12 — B1 MAINNET TEST PLAN (REAL MONEY)
**Date:** 2026-09-16
**Status:** ⏸ AWAITING YOUR APPROVAL — no mainnet tx sent yet.
**Network:** Arc **MAINNET**, chainId 5042
**Wallet:** `0xa842e3aB069562Db379c35Dd52C77ef214324004`

---

## 1. ✅ NATIVE TOKEN VALUE — NOW PROVEN, NOT ASSUMED

From Circle's official docs (`docs.arc.io/arc/references/gas-and-fees`), verbatim:

| Parameter | Value |
|---|---|
| **Gas unit** | **USDC (18 decimals)** |
| Pricing model | EIP-1559 + EWMA smoothing |
| Base fee target | ~$0.001 per ERC-20 transfer |
| **Minimum base fee** | **20 Gwei** (protocol floor) |
| **Maximum base fee** | **20,000 Gwei** (hard ceiling) |
| Gas throughput | 30M gas/block |

Also verbatim: *"USDC is the native gas token… There is no volatile native token."*

**Therefore: 1 native unit = 1 USDC ≈ $1. Cost in native == cost in USD.**
This closes the open item from doc 08 (native = 18 dec) with the *reason*:
it is USDC accounted at 18-decimal precision.

⚠️ **Doc correction:** Circle states execution env is **"EVM (Osaka hard fork)"**,
not Cancun. My Cancun tests all passed because Osaka is *newer* and
superset-compatible — so `evmVersion: cancun` remains safe, but Osaka is the
accurate label.

### I independently verified a doc claim
Docs say: *"Arc publishes the next block's base fee in the parent header's
`extra_data` field as an 8-byte big-endian value."* Tested:
```
block 21,177,822
extra_data      0x00000016a1a9a971   (exactly 8 bytes)
parsed          97.2015 gwei
same block baseFee 97.5824 gwei
within protocol bounds [20, 20000]: True
```
**Claim confirmed.** Adjacent values, correct size, plausible range.

---

## 2. 💰 EXACT COST — WORST CASE $0.95 OF $2.00

Balance re-audited after your funding:
```
Arc MAINNET   2.000000000000000000   nonce=0   <-- $2.00, never used
Arc TESTNET  39.996372698750001007   nonce=1   (our smoke deploy)
Ethereum/Base/Arbitrum/Optimism/Polygon/BSC   0.0   nonce=0
```
**Still zero real-world value outside Arc. Wallet hygiene intact.**

Live gas at planning time: baseFee median **101.60 gwei** (97.58–105.71),
priority p50 **19.53 gwei** → chosen `maxFeePerGas` **230.94 gwei**
(= max×2.0 + tip, and ≥ the documented 20 gwei floor).

| step | gas | cost |
|---|---|---|
| deploy ERC721SeaDrop | 3,500,000 | $0.8083 |
| setMaxSupply | 60,000 | $0.0139 |
| setBaseURI | 80,000 | $0.0185 |
| updateCreatorPayoutAddress | 70,000 | $0.0162 |
| updateAllowedFeeRecipient | 70,000 | $0.0162 |
| updatePublicDrop | 120,000 | $0.0277 |
| mintPublic ×1 | 200,000 | $0.0462 |
| **TOTAL** | **4,100,000** | **$0.9469** |

```
balance          $2.0000
worst-case spend $0.9469
left over        $1.0531
headroom         2.11x   -> OK
```
Actual will be lower: the smoke deploy landed at **98.5%** of estimate, and
this model uses `max×2.0` not median.

⚠️ **MAXIMUM POSSIBLE LOSS: ~$0.95.** That is the entire downside.

---

## 3. ✅ ARC'S SEADROP HAS THE FUNCTIONS WE NEED

Selectors verified with `cast sig` (not memory), then searched inside the
**bytecode actually deployed on Arc**:

| function | selector | in Arc bytecode |
|---|---|---|
| `mintPublic(address,address,address,uint256)` | `0x161ac21f` | ✅ FOUND |
| `updatePublicDrop((uint80,uint48,uint48,uint16,uint16,bool))` | `0x01308e65` | ✅ FOUND |
| `updateCreatorPayoutAddress(address)` | `0x12738db8` | ✅ FOUND |
| `updateAllowedFeeRecipient(address,bool)` | `0x8e7d1e43` | ✅ FOUND |
| `getPublicDrop(address)` | `0xbc6a629c` | ✅ FOUND |
| `mintSigned` | `0x4b61cd6f` | ✅ FOUND |
| `mintAllowList` | `0x7d19bebe` | ⬜ not located |
| `mintAllowedTokenHolder` | `0xedf7c6a2` | ⬜ not located |

**Every function our plan uses is present.** The two not located are unused
by B1; a raw byte search can miss selectors depending on jump-table encoding,
so I am **not** claiming they are absent — only that I did not locate them.

---

## 4. EXACT PARAMETERS — READ FROM SOURCE, NOT GUESSED

`PublicDrop` struct (field order and widths matter for ABI encoding):
```solidity
struct PublicDrop {
    uint80 mintPrice;                 //  80/256
    uint48 startTime;                 // 128/256
    uint48 endTime;                   // 176/256
    uint16 maxTotalMintableByWallet;  // 224/256
    uint16 feeBps;                    // 240/256
    bool   restrictFeeRecipients;     // 248/256
}
```
Constraint found in `SeaDrop.sol:722`: `if (feeBps > 10_000) revert InvalidFeeBps`.

`ERC721SeaDrop` constructor — **SeaDrop address is injected, not hardcoded**:
```solidity
constructor(string name, string symbol, address[] allowedSeaDrop)
```

### Planned values for the test collection
```
name        "Arc Mint Path Test"      <- THROWAWAY, deliberately not Coinkins
symbol      "AMPT"
allowedSeaDrop [0x00005EA00Ac477B1030CE78506496e8C2dE24bf5]  (canonical)
maxSupply   5
mintPrice   0                  <- FREE, so we test the mint path, not payments
startTime   now - 60
endTime     now + 30 days
maxTotalMintableByWallet 5
feeBps      0                  <- avoids fee-split complications
restrictFeeRecipients false     <- avoids the feeRecipient allowlist path
```
**Why `mintPrice = 0`:** B1's purpose is to prove the *canonical wiring works*.
A zero price removes payment-split variables, so any failure is unambiguous.
The paid path is a separate, later test.

⚠️ **Why a throwaway name:** this contract is **permanent and public**. Using
`Coinkins` would burn the real brand on a 5-item test artifact. Doc 11 flagged
this; enforcing it here.

---

## 5. SAFETY GATES (all enforced in code, mainnet variant)

```
GATE 1  chainId == 5042 (MAINNET)      - explicit, deliberate
GATE 2  derived address == audited wallet
GATE 3  per-tx cost cap + TOTAL run cap ($1.20)
GATE 4  maxFeePerGas >= 20 gwei documented floor
GATE 5  balance >= projected total before each step
GATE 6  every step re-reads live gas (no stale values)
GATE 7  abort immediately on any non-0x1 status
```
Note GATE 1 is **inverted** from the smoke test, which hard-refused mainnet.
That inversion is the single deliberate change, and it is why I am asking
for approval before running.

---

## 6. EXECUTION SEQUENCE (7 txs, each verified before the next)

| # | action | verify by |
|---|---|---|
| 1 | deploy `ERC721SeaDrop` | `eth_getCode` > 0; `name()`/`symbol()` readback |
| 2 | `setMaxSupply(5)` | `maxSupply()` == 5 |
| 3 | `setBaseURI(...)` | `tokenURI(0)` after mint |
| 4 | `updateCreatorPayoutAddress(self)` | `getCreatorPayoutAddress` via SeaDrop |
| 5 | `updateAllowedFeeRecipient(self,true)` | read back |
| 6 | `updatePublicDrop(...)` | `getPublicDrop(token)` matches exactly |
| 7 | `mintPublic(token,self,0,1)` | `balanceOf(self)`==1, `totalSupply()`==1, Transfer event |

**Stop-on-failure.** Any step that fails halts the run; remaining budget unspent.

---

## 7. WHAT B1 WILL AND WILL NOT PROVE

### Will prove
- ✅ Our `ERC721SeaDrop` deploys and is accepted by canonical SeaDrop
- ✅ `mintPublic` works end-to-end against Arc's real SeaDrop
- ✅ Configuration txs behave as documented
- ✅ Real mainnet gas costs for every operation
- ✅ Whether OpenSea indexes an Arc collection at all

### Will NOT prove
- ⬜ Paid-mint payment splitting (price = 0 here)
- ⬜ Allowlist / signed / token-gated stages
- ⬜ ERC-20 USDC **6-decimal** token path (native is 18-dec USDC)
- ⬜ Whether OpenSea's drop UI renders a mint button
- ⬜ Anything about demand

---

## 8. ⚠️ RISKS — STATED BEFORE YOU DECIDE

| risk | severity | mitigation |
|---|---|---|
| Spend up to $0.95 | **low** | hard total cap $1.20; stop-on-failure |
| Permanent public junk contract on Arc | **low** | throwaway name; real brand protected |
| Gas spike mid-run (base fee can hit 20,000 gwei) | medium | re-read gas each step; abort if projection exceeds cap |
| A config tx reverts, deploy cost already sunk | medium | ~$0.81 sunk worst case; still under $1 |
| Deploy succeeds but OpenSea never indexes it | **informational** | that *is* a finding, and a valuable one |

**I am not claiming this will make OpenSea list us. That is the open question
B1 answers.**

---

## 9. APPROVAL REQUEST

Everything is verified and staged. To proceed I need your explicit OK on:

1. **Spend up to ~$0.95** (hard cap $1.20) of the $2.00 on Arc mainnet
2. **Throwaway name** `Arc Mint Path Test` / `AMPT` — NOT `Coinkins`
3. **maxSupply 5, mintPrice 0** for this test

Say the word and I run it step by step, verifying each tx before the next.
