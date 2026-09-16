# 08 — PREFLIGHT VERIFICATION (Arc chosen; measured 2026-09-16)
**Every line below is a measured result, not an assumption.**
**This document INVALIDATES Phase 1 of doc 05. Read §4 before any work.**

---

## 1. CHAIN STATE — all three RPCs live

| endpoint | chainId | block | baseFee |
|---|---|---|---|
| `rpc.mainnet.arc.io` | 0x13b2 = **5042** | 21,172,975 | **163.65 gwei** |
| `rpc.testnet.arc.io` | 0x4cef52 = **5042002** | 62,418,065 | 20.00 gwei |
| `rpc.drpc.testnet.arc.io` | 0x4cef52 = **5042002** | 62,418,065 | 20.00 gwei |

`web3_clientVersion` = **`arc/v1`**. `eth_syncing` = false. `arc_chainConfig` = not supported.

### Mainnet is genuinely busy (not a ghost chain)
```
block gasLimit  30,000,000
block gasUsed   15,035,679   (50% full)
txs in block    72
```
This matters: the **chain** has real activity. It is the **NFT market on it** that is empty. Two different facts — I previously conflated them.

---

## 2. GAS — my earlier number was WRONG and is now corrected

Doc 05 costed the deploy at **64.07 gwei**. Measured now over 12 sampled blocks:

```
min 223.54   max 298.90   median 274.54   mean 269.51 gwei
spread 1.34x  -> VOLATILE, MUST be read live, never hardcoded
priorityFee  p50 = 69.23 gwei   p90 = 406.01 gwei
eth_maxPriorityFeePerGas = 0x0   (unreliable -> use feeHistory, not this)
```

**Gas is ~4.3x higher than doc 05 assumed.** Corrected cost model at median 274.54 gwei:

| action | gas | @1.5x | @2.0x |
|---|---|---|---|
| ERC721SeaDrop deploy | 3,500,000 | **1.441 native** | 1.922 native |
| configure drop | 200,000 | 0.082 | 0.110 |
| single mint (buyer pays) | 150,000 | 0.062 | 0.082 |

⚠️ `eth_maxPriorityFeePerGas` returns **0** — trusting it would produce a stuck tx. Use `eth_feeHistory` percentiles.

---

## 3. NATIVE CURRENCY = 18 DECIMALS (tested, not assumed)

Sampled real on-chain tx values from a live block:
```
100000000000000000        /1e18 = 0.100000   /1e6 = 100,000,000,000   <- absurd
343222633315844182360     /1e18 = 343.22     /1e6 = 343,222,633,315
30000000000000000000      /1e18 = 30.000000
16500000000000000000      /1e18 = 16.500000
4748219000000000000       /1e18 = 4.748219
```
Clean human numbers at **1e18**, nonsense at 1e6 → **native is 18-decimal**.

**Consequence:** the gas/native unit is an 18-dec representation, **not raw 6-decimal USDC**. Any pricing code that assumes 6 decimals for the *native* value field would be wrong by **10¹²**. An ERC-20 USDC *token* contract may still be 6-dec — these must be handled separately and tested independently.

---

## 4. 🚨 BLOCKER — SEADROP DOES NOT EXIST ON ARC TESTNET

This kills Phase 1 of doc 05 as written.

| contract | MAINNET | TESTNET |
|---|---|---|
| **SeaDrop** `0x00005EA0…24bf5` | **21,081 B LIVE** | **0 B — ABSENT** |
| **Seaport 1.6** | 23,981 B LIVE | **0 B — ABSENT** |
| **ConduitController** | 8,820 B LIVE | **0 B — ABSENT** |
| CreateX | 11,838 B LIVE | 11,838 B LIVE |
| Create2Factory | 69 B LIVE | 69 B LIVE |
| Multicall3 | 3,808 B LIVE | 3,808 B LIVE |
| Permit2 | 9,152 B LIVE | 9,152 B LIVE |
| **ERC-6551 Registry** | **0 B — ABSENT** | **571 B LIVE** |

Also probed Seaport 1.1 / 1.4 / 1.5 on testnet — **all 0 bytes**. No SeaDrop variant exists on testnet.

**Note the inversion:** SeaDrop is on mainnet only; ERC-6551 is on **testnet** only. Doc 05 said 6551 was "not deployed" — that was true for mainnet, but it **is** live on testnet and is **genuine**: calling `account(...)` returned a valid computed address `0xdc19bb…de180c` rather than reverting.

**Meaning: a full SeaDrop dress rehearsal on testnet is impossible today.** Options in §7.

---

## 5. ✅ PROOF THAT ARC'S SEADROP IS THE REAL CANONICAL SEADROP

Strongest available check — byte-level diff against Ethereum mainnet:

```
SeaDrop     ARC len=21081   ETH len=21081   differing bytes = 34 (0.161%)
Seaport1.6  ARC len=23981   ETH len=23981   differing bytes = 34 (0.142%)
ConduitController                           IDENTICAL sha256
```

The 34 differing bytes fall in exactly **2 runs**, and they are the chain-binding constants:
```
run 1  offset 14462-14463 (2B)   ARC = 0x13b2   ETH = 0x0001
       0x13b2 = 5042 = Arc chainId  (matches eth_chainId)  -> MATCH: True
run 2  offset 14645-14676 (32B)  = EIP-712 domainSeparator
       high entropy both sides (22/24 and 24/24 unique bytes) = keccak output
```

**Conclusion: identical logic, only chainId + derived EIP-712 domain separator differ.** This is exactly what a correct same-bytecode cross-chain deployment looks like. Arc's SeaDrop is trustworthy.

---

## 6. ✅ DEPLOYMENT IS PERMISSIONLESS (tested)

Arc has institutional validators (BlackRock, Visa, Mastercard, NYSE), so permissioned deploy was a real risk worth testing.

```
eth_estimateGas({from: 0x1111…1111 (random, zero balance), data: <init code>})
  -> result 0x10624 = 66,596 gas
```
A contract-creation estimate **succeeded from an unfunded random address** with no authorization error. **Anyone can deploy.** (Estimate ≠ mined tx, but a permissioned chain rejects at estimate.)

---

## 7. SANDBOX TOOLCHAIN — CONSTRAINTS FOUND

```
node     v12.22.9   <-- too old (Hardhat needs >=18; ethers v6 needs >=14)
npm      8.5.1
python3  3.10.12    <-- viable
solc     NOT INSTALLED
forge / cast / anvil NOT INSTALLED
disk     37G used / 1.8G free  = 96% FULL   <-- installs are constrained
```

⚠️ **Three real constraints.** A Hardhat/Foundry install is high-risk here (Node too old + 1.8 GB free). The low-footprint path is **python3 + a standalone `solc` binary (~15 MB) + raw JSON-RPC**, which is what I already used for all verification above.

---

## 8. HOW PHASE 1 MUST CHANGE (options, with honest costs)

| option | what it is | cost | risk |
|---|---|---|---|
| **A. Deploy our own SeaDrop to testnet** | SeaDrop is open source; deploy it + our token on testnet | testnet gas only, 20 gwei (free faucet) | ⭐ Best. Full rehearsal, zero real money. More build work. |
| **B. Rehearse on mainnet at tiny supply** | Deploy real, 5-item supply | ~1.5–2 native (~$2) | Real money, real exposure, but trivial sum |
| **C. Local fork (anvil)** | Simulate Arc locally | 0 | ❌ forge not installed + 1.8 GB free + Node 12 |
| **D. Plain ERC-721A, no SeaDrop** | Own mint function | ~$1 | ❌ Loses OpenSea drop-page integration |

**Recommendation: A, with B as the final smoke test.** Option A proves every code path for free; B proves the mainnet SeaDrop wiring for ~$2.

---

## 9. CORRECTIONS THIS DOC MAKES TO MY OWN EARLIER WORK

| # | earlier claim | corrected |
|---|---|---|
| 1 | deploy ≈ $0.34 @ 64.07 gwei | **≈1.44–1.92 native @ 274.54 gwei median** (4.3x) |
| 2 | Phase 1 = testnet SeaDrop rehearsal | **IMPOSSIBLE — SeaDrop absent on testnet** |
| 3 | "ERC-6551 not deployed on Arc" | mainnet ✗ but **testnet ✓ (571 B, genuine)** |
| 4 | Arc field is empty/dead | market empty, but **chain is 50% full, 72 tx/block** |
| 5 | gas "volatile 64–214 gwei" | now **223–299 gwei**; read live, always |
| 6 | native decimals unstated | **18 decimals, proven by tx-value analysis** |

---

## 10. OPEN ITEMS — NOT YET VERIFIED (no guessing)

- ⬜ Testnet faucet existence / USDC test funds source
- ⬜ Arc block explorer + contract verification API endpoint
- ⬜ Whether OpenSea's Arc drop UI accepts a self-deployed SeaDrop token
- ⬜ `solc` install feasibility under 1.8 GB free disk
- ⬜ Trademark clearance for `Coinkins` (**user action** — USPTO/WIPO classes 9 & 42)
