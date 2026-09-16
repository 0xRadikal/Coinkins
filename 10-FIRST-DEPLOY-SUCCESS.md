# 10 — FIRST REAL DEPLOYMENT ON ARC (TESTNET) — SUCCESS
**Date:** 2026-09-16
**Network:** Arc Testnet, chainId **5042002**
**Status:** ✅ End-to-end pipeline PROVEN with a real, mined transaction.

---

## 1. CORRECTIONS TO MY OWN PREVIOUS CLAIMS

I was wrong twice in doc 09. Both are corrected here.

| # | my earlier claim | truth |
|---|---|---|
| 1 | "wallet file is a placeholder, no funds exist" | ❌ **WRONG.** `/root/wallet-test.env` is real and funded. My `find` pattern `*wallet*test*` failed to match `wallet-test.env` because of hyphen ordering, and I only found the unrelated `/tmp/test_wallet.env` decoy. **The user had already done the work.** |
| 2 | "Foundry not installed, must avoid it" | ❌ **WRONG.** **Foundry v1.8.1** was already installed at `/root/.foundry/bin/` — it simply was not on `PATH`. `forge`, `cast`, `anvil`, `chisel` all functional. |

**Lesson recorded:** `which forge` returning nothing proves only that it is not on PATH — **not** that it is absent. I should have checked `~/.foundry` before concluding.

---

## 2. WALLET SAFETY AUDIT — PASSED

Address derived via `cast wallet address` (key never printed, passed by env not argv):
```
0xa842e3aB069562Db379c35Dd52C77ef214324004
```
File integrity: 79 bytes = `private-key=` (12) + `0x` + 64 hex + `\n`. Mode **600**. Structure exactly correct.

Balance audit across 8 networks:
```
Arc MAINNET    0.000000000000000000   nonce=0
Arc TESTNET   40.000000000000000000   nonce=0   <-- FUNDED
Ethereum       0.000000000000000000   nonce=0
Base           0.000000000000000000   nonce=0
Arbitrum       0.000000000000000000   nonce=0
Optimism       0.000000000000000000   nonce=0
Polygon        0.000000000000000000   nonce=0
BSC            0.000000000000000000   nonce=0
```
**Verdict: ideal throwaway wallet.** Funded only on testnet, `nonce=0` everywhere (never used), **zero real-world value at risk.** This is exactly correct practice.

---

## 3. THREE SAFETY GATES — ALL ENFORCED IN CODE

`deploy_smoke.py` refuses to run unless all three pass:

```
GATE 1  chainId == 5042002        -> PASS  (mainnet deploy impossible)
GATE 2  derived addr == audited    -> PASS  (wrong key cannot be used)
GATE 3  worst-case cost <= 1.0     -> PASS  (0.00874656 native)
```
Gate 1 makes an accidental mainnet spend **structurally impossible**, not merely unlikely.

---

## 4. ✅ THE DEPLOYMENT — REAL, MINED, CONFIRMED

```
status             0x1  (SUCCESS)
txHash             0x3e7cd62f938159b72857cc682ff9d48f56d756f2e8299589271903b9f1e96a4e
contractAddress    0xd80266b6f0c021e6a606a51d10c19e9c5cc9a846
blockNumber        62,420,687
gasUsed            163,300
effectiveGasPrice  22.2125 gwei
actual cost        0.0036273013 native
```

### Gas estimate accuracy
```
estimated 165,763  ->  actual 163,300   = 98.51% accurate
```
Our live-sampled estimation model is sound. No hardcoded value was used.

### Post-deploy state verification (read back from chain)
```
runtime code   403 bytes   (matches keyless simulation exactly)
value()        42          expected 42     PASS
owner()        0xa842…4004 expected deployer PASS
```
`value()` proves constructor args were encoded and applied correctly.
`owner()` proves `msg.sender` / `immutable` handling is correct.

Selectors were **verified with `cast sig`**, not recalled from memory:
```
value()            0x3fa4f245
owner()            0x8da5cb5b
setValue(uint256)  0x55241077
```

---

## 5. ✅ INDEPENDENT THIRD-PARTY CONFIRMATION

Not trusting my own RPC reads — cross-checked against Blockscout:
```
GET explorer.testnet.arc.io/api/v2/addresses/0xd80266b6…a846   HTTP 200
  is_contract  : True
  creator      : 0xa842e3aB069562Db379c35Dd52C77ef214324004
  creation_tx  : 0x3e7cd62f938159b72857cc682ff9d48f56d756…
  is_verified  : False   (source not yet submitted - expected)
```
**Three independent sources agree:** `cast` receipt, direct `eth_getCode`/`eth_call`, and the public explorer.

---

## 6. BUG FOUND AND FIXED DURING EXECUTION

First broadcast attempt failed:
```
error: unexpected argument '--gas-limit' found
```
**Cause:** in Foundry v1.8.1, `cast send --create` consumes all remaining
arguments, so `--create` must be **last**. Confirmed by reading
`cast send --help` rather than guessing. Fixed by reordering; second attempt
succeeded. Comment added to the code so it cannot regress.

---

## 7. WHAT IS NOW PROVEN vs STILL UNPROVEN

### Proven by execution
- ✅ Arc testnet accepts and mines our transactions
- ✅ `solc 0.8.24 --evm-version cancun` output runs correctly on Arc
- ✅ EIP-1559 (type 0x2) fee model works; live sampling is accurate to 98.5%
- ✅ Constructor args, immutables, storage all behave correctly
- ✅ Signing via `cast` with key held in env (never in argv/ps) works
- ✅ Explorer indexes our contract within seconds

### Still unproven (next steps)
- ⬜ SeaDrop suite compiles (needs full OpenSea source + deps)
- ⬜ SeaDrop deploys on testnet (it is **absent** there — we deploy our own)
- ⬜ `ERC721SeaDrop` token + paid public stage configuration
- ⬜ Real `mintPublic` from a second clean wallet
- ⬜ **Decimal test**: native is 18-dec (proven) vs ERC-20 USDC 6-dec (untested)
- ⬜ Withdrawal (pull-payment) path
- ⬜ Source verification submission to Blockscout

---

## 8. COST REALITY — TESTNET IS EFFECTIVELY FREE

```
one deploy = 0.0036273013 native
balance    = 40.0 native
=> ~11,000 deploys affordable
```
**No financial risk in Phase 1 whatsoever.** We can iterate freely.
Mainnet equivalent at the moment of measurement would be ~0.045 native
(~12x testnet cost, since testnet baseFee is pinned at 20 gwei while
mainnet ranged 84–274 gwei within one hour).

---

## 9. FILES THIS PHASE
```
check_wallet.py      8-chain balance/nonce safety audit (address only)
deploy_smoke.py      gated real deploy + post-state verification
contracts/SmokeTest.sol  toolchain validation contract (testnet only)
.gitignore           blocks .env, *.key, __pycache__, contracts/out
```

## 10. NEXT ACTION
Acquire the official OpenSea SeaDrop sources (`ERC721SeaDrop`, `SeaDrop`,
plus `seadrop` + `ERC721A` + `solady`/`openzeppelin` deps), compile with the
already-validated solc 0.8.24 + cancun, and deploy the pair to testnet.

⚠️ **No mainnet action until every item in §7 "still unproven" is green.**
