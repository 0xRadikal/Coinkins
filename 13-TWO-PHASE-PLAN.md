# 13 — TWO-PHASE MAINNET PLAN (APPROVED SCOPE)
**Date:** 2026-09-16
**Your instructions:** cost is fine; any throwaway name; **two phases close in
time**; Phase 1 = free allowlist mint to OUR wallet; Phase 2 = public paid
**0.1 USDC**; **supply 1000**.
**Status:** fully verified, ready to execute.

---

## 1. ⚠️ TWO SELECTOR ERRORS I MADE — FOUND AND CORRECTED

I had quoted selectors from **memory**. Both were wrong. Caught before spending.

| function | my memory (WRONG) | real (`cast sig` from source) |
|---|---|---|
| `mintAllowList` | `0x7d19bebe` | **`0x4300a4e6`** |
| `mintAllowedTokenHolder` | `0xedf7c6a2` | **`0xd734375a`** |
| `updateAllowList` | `0x20351c01` (assumed `bytes32`) | **`0xebb4a55f`** (takes `AllowListData`) |

Root cause of the third: I assumed the parameter was a bare `bytes32`.
Source shows it is a **struct**:
```solidity
struct AllowListData { bytes32 merkleRoot; string[] publicKeyURIs; string allowListURI; }
```
**This is exactly why doc 12 flagged those two as "not located" rather than
claiming they were absent.** They were present — my selectors were wrong.

---

## 2. ✅ ARCHITECTURE FACT — CONFIG GOES THROUGH THE TOKEN

Found in source: SeaDrop's setters carry `onlyINonFungibleSeaDropToken`,
so **we cannot call SeaDrop directly**. We call the **token**, which forwards.

```
US (owner) --> ERC721SeaDrop.updateAllowList(seaDropImpl, AllowListData)
                    |  _onlyOwnerOrSelf() + _onlyAllowedSeaDrop()
                    v
               SeaDrop.updateAllowList(AllowListData)
                    |  onlyINonFungibleSeaDropToken  (msg.sender == token)
                    v
               _allowListMerkleRoots[token] = merkleRoot
```

### All selectors verified on BOTH sides

**SeaDrop-side** (deployed on Arc, 21,081 bytes):
```
mintPublic              0x161ac21f  FOUND
mintAllowList           0x4300a4e6  FOUND
updateAllowList(ALD)    0xebb4a55f  FOUND
getAllowListMerkleRoot  0x32bf11f5  FOUND
updatePublicDrop(PD)    0x01308e65  FOUND
getPublicDrop           0xbc6a629c  FOUND
```
**Token-side** (our compiled 19,805 bytes):
```
updateAllowList(addr,ALD)         0x3680620d  FOUND
updatePublicDrop(addr,PD)         0x1b73593c  FOUND
updateCreatorPayoutAddress(a,a)   0x66251b69  FOUND
updateAllowedFeeRecipient(a,a,b)  0x48a4c101  FOUND
setMaxSupply                      0x6f8b44b0  FOUND
setBaseURI                        0x55f804b3  FOUND
```
Live call confirmation: `getAllowListMerkleRoot(dummy)` returns 32 zero
bytes — callable, unconfigured token = zero root, exactly as expected.

---

## 3. ✅ MERKLE ROOT — COMPUTED AND DOUBLE-VERIFIED

Leaf formula proven from source (`SeaDrop.sol:301`):
```solidity
keccak256(abi.encode(minter, mintParams))
```
Note `abi.encode`, **not** `encodePacked` → every field padded to 32 bytes.

Empty-proof behaviour proven from OpenZeppelin `MerkleProof.processProof`:
```solidity
bytes32 computedHash = leaf;
for (uint256 i = 0; i < proof.length; i++) { ... }   // skipped when empty
return computedHash;                                  // == leaf
```
**So for a 1-entry allowlist: `root == leaf`, `proof == []`.** Not a guess —
read from the library source.

### Computed result
```
abi.encode size = 288 bytes  (= 32 addr + 8 x 32 fields)  MATCH
merkleRoot (cast keccak) = 0x6adbda1469cfd800d396df8fa2c39ba6644ca34fdcb56f2793a62c1cc586c95b
merkleRoot (python)      = 0x6adbda1469cfd800d396df8fa2c39ba6644ca34fdcb56f2793a62c1cc586c95b
INDEPENDENT MATCH: True
```
Two independent keccak implementations agree.

---

## 4. ✅ PAYMENT MODEL — VERIFIED

```solidity
function _checkCorrectPayment(uint256 quantity, uint256 mintPrice) internal view {
    if (msg.value != quantity * mintPrice) revert IncorrectPayment(...);
}
```
Payment is **`msg.value` in native USDC** — which is exactly Arc's model
(native gas token IS USDC, 18 decimals). No ERC-20 approve flow needed.

`mintPrice` is `uint80`:
```
uint80 max        = 1,208,925,819,614,629,174,706,175  (~1,208,925 USDC)
0.1 USDC (18 dec) =           100,000,000,000,000,000
fits: True, headroom 12,089,258x
```
**Requires EXACT payment.** Overpay reverts too. Our mint tx must send
precisely `quantity * mintPrice`.

---

## 5. FINAL PARAMETERS

```
name           "Arc Pathfinder Test"
symbol         "APFT"
allowedSeaDrop [0x00005EA00Ac477B1030CE78506496e8C2dE24bf5]  (canonical)
maxSupply      1000
```

### Phase 1 — ALLOWLIST, FREE, our wallet only
```
mintPrice                0
maxTotalMintableByWallet 5
startTime                now - 300      (already open)
endTime                  now + 7 days
dropStageIndex           1              (MUST be non-zero, per source)
maxTokenSupplyForStage   1000
feeBps                   0
restrictFeeRecipients    false
merkleRoot               0x6adbda14...c95b
proof                    []
```

### Phase 2 — PUBLIC, PAID 0.1 USDC
```
mintPrice                100000000000000000   (0.1 x 1e18)
startTime                now + 120            (2 min after phase 1)
endTime                  now + 7 days
maxTotalMintableByWallet 5
feeBps                   0
restrictFeeRecipients    false
```
**Phases overlap deliberately**, per your instruction to mint both within a
short window. Allowlist stays open while public opens 2 minutes later.

⚠️ Phase 2 mint costs **0.1 USDC of real value** on top of gas — but it
returns to our own `creatorPayoutAddress` (ourselves), so net loss is only
the gas plus fee split (feeBps = 0, so no fee taken).

---

## 6. EXECUTION SEQUENCE — 9 transactions

| # | tx | verify |
|---|---|---|
| 1 | deploy `ERC721SeaDrop(name,symbol,[seadrop])` | `name()`, `symbol()`, code size |
| 2 | `setMaxSupply(1000)` | `maxSupply()` == 1000 |
| 3 | `setBaseURI(...)` | readback |
| 4 | `updateCreatorPayoutAddress(sd, self)` | via SeaDrop getter |
| 5 | `updateAllowedFeeRecipient(sd, self, true)` | readback |
| 6 | `updateAllowList(sd, AllowListData)` | `getAllowListMerkleRoot(token)` == our root |
| 7 | **`mintAllowList`** free, qty 1 | `balanceOf`==1, `totalSupply`==1 |
| 8 | `updatePublicDrop(sd, PublicDrop)` | `getPublicDrop(token)` field-by-field |
| 9 | **`mintPublic`** paid 0.1 USDC, qty 1 | `balanceOf`==2, `totalSupply`==2 |

**Stop-on-failure at every step.** Budget unspent if a step fails.

---

## 7. COST ESTIMATE (live gas at planning time)

baseFee median ~101 gwei, tip ~19.5 gwei → maxFee ~231 gwei worst case.

| group | gas | cost |
|---|---|---|
| deploy | 3,500,000 | ~$0.81 |
| 5 config txs (2–6, 8) | ~600,000 | ~$0.14 |
| 2 mints (7, 9) | ~400,000 | ~$0.09 |
| **gas total** | **~4,500,000** | **~$1.04** |
| mint payment (phase 2) | — | 0.10 USDC (returns to us) |
| **TOTAL OUTLAY** | | **~$1.14 of $2.00** |

Headroom ~1.75x. You approved unlimited cost, but I keep a hard cap at
**$1.60** so a gas spike cannot drain the wallet and strand us mid-run.

⚠️ **Honest risks:**
- Gas can legally reach **20,000 gwei** (protocol ceiling). If it spikes
  mid-run, later steps abort and the deploy cost is sunk (~$0.81).
- `maxSupply 1000` with only 2 minted means **"all items minted" is FALSE** →
  this collection can never get a blue check. **That is intentional** — it is
  a throwaway test, not the real launch.

---

## 8. WHAT THIS PROVES

- ✅ allowlist (merkle) mint path against Arc's canonical SeaDrop
- ✅ paid public mint path with real value transfer
- ✅ two overlapping stages coexisting
- ✅ exact real gas costs for a 1000-supply configuration
- ✅ whether OpenSea indexes an Arc SeaDrop collection

Still NOT proven: OpenSea drop-UI rendering, ERC-20 6-dec USDC path
(not used — native is 18-dec), demand.
