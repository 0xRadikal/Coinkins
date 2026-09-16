# 11 — SEADROP BUILD + A FALSIFIED HYPOTHESIS
**Date:** 2026-09-16
**Outcome:** SeaDrop suite compiles. A hypothesis I formed was **tested and proven WRONG**, which changed the deployment strategy. Documented honestly.

---

## 1. FORENSIC PROOF OF OPENSEA'S EXACT COMPILER

I did not trust `foundry.toml`. I extracted the compiler version from the
**CBOR metadata trailer of the bytecode actually deployed on Arc**:

```
tail bytes: … 64 736f6c63 43 000811 0033
                 "solc"      ^^^^^^
                             00 08 11  =  0.8.17
metadata length = 0x0033 = 51 bytes
contains "ipfs" marker: True
```
**Deployed SeaDrop on Arc = solc 0.8.17.** This matches `foundry.toml`
(`solc_version = '0.8.17'`) — two independent sources agree.

My installed 0.8.24 would have been the **wrong compiler**. Caught before use.

### solc 0.8.17 installed, integrity verified
```
expected sha256: 0x99f2070b776e9714f1f76c43c229cf99b8978a92938ee8d2364c6de11c1a03d4
actual   sha256:   99f2070b776e9714f1f76c43c229cf99b8978a92938ee8d2364c6de11c1a03d4
                   ^^ EXACT MATCH
```

---

## 2. DISK SAFETY — MEASURED BEFORE CLONING, NOT AFTER

Only 1.8 GB free, so I sized every dependency via the GitHub API **before**
downloading anything:

```
openzeppelin-contracts              52.1 MB
openzeppelin-contracts-upgradeable  39.8 MB
forge-std                            1.2 MB
ERC721A / solmate                    0.8 MB each
murky                                0.3 MB
ERC721A-Upgradeable                  0.6 MB
ds-test / create2-helpers            0.1 MB each
utility-contracts                    0.0 MB
-----------------------------------------------
total                              ~96 MB
```
Used `--depth 1` shallow clones throughout. Result: **101 MB**, disk went
1.8 GB → 1.7 GB. No risk of filling the disk.

---

## 3. ✅ BUILD SUCCEEDED

```
forge build --use /usr/local/bin/solc-0.8.17
  -> compiled, only lint NOTES on test files (missing-inheritance), no errors

SeaDrop        runtime 21,048 bytes
ERC721SeaDrop  runtime 19,805 bytes
```

---

## 4. ❌ MY HYPOTHESIS WAS FALSIFIED — AND THAT MATTERED

Our SeaDrop compiled to **21,048 B**; Arc's deployed copy is **21,081 B**.
Delta 33 bytes. First diff samples looked like `f0→e8`, `2a→22`, `63→5b`
— all exactly **−8**.

**My hypothesis:** "all differing bytes differ by exactly 8, so this is
just shifted PUSH2 jump destinations — same logic, benign."

I wrote `analyze_diff.py` to **test** that rather than assert it:

```
after stripping metadata:  local 21,036 B   onchain 21,028 B
differing bytes: 8,142 of 21,028  (38.72%)
distribution of (local - onchain):
   +255 -> 164 (2.01%)      +6 -> 137 (1.68%)     -33 -> 131 (1.61%)
     -1 -> 130 (1.60%)    -255 -> 120 (1.47%)      +1 -> 110 (1.35%)
distinct deltas observed: 469
```

**VERDICT: HYPOTHESIS FALSE.** Not a uniform shift. 469 distinct deltas and
38.7% of bytes differ. **Our compile is NOT bytecode-equivalent to Arc's SeaDrop.**

Had I trusted the first few samples and skipped the test, I would have made
a false equivalence claim. The early `−8` pattern was a coincidence of the
first ten diffs.

### Likely cause (stated as unproven)
`foundry.toml` has `optimizer_runs = 1_000_000` and a commented-out
`via_ir = true`. OpenSea's release build almost certainly used different
optimizer/IR settings than my local run. ⬜ **Not verified — I am not
claiming it as fact.**

---

## 5. ✅ THE DECISIVE ANCHOR — ARC'S COPY IS THE AUTHENTIC ONE

Independent cross-check against Ethereum mainnet:
```
Arc vs Ethereum canonical SeaDrop: 34 differing bytes of 21,028
  (doc 08 proved: chainId 0x13b2 vs 0x0001 + the derived EIP-712
   domain separator — nothing else)
```
So: **Arc's deployed SeaDrop is byte-authentic canonical OpenSea SeaDrop.
My local compile is the outlier, not Arc.**

---

## 6. 🔄 STRATEGY CHANGE (this supersedes doc 08 §8 Option A)

| before | after |
|---|---|
| "SeaDrop is absent on testnet → deploy our own SeaDrop" | **Never deploy our own SeaDrop. Use Arc mainnet's authentic canonical one.** |

**Reasons, in order of importance:**
1. Our compile is **not** byte-equivalent (measured above). Deploying it
   would create a **non-canonical** SeaDrop.
2. OpenSea's drop UI/indexer recognises the **canonical** SeaDrop address.
   A self-deployed clone would likely not be indexed as a drop.
3. Deploying an unaudited self-compiled variant adds risk for **zero** benefit.

### ✅ AND IT IS FULLY SUPPORTED — verified in source
`ERC721SeaDrop` does **not** hardcode a SeaDrop address:
```solidity
constructor(
    string memory name,
    string memory symbol,
    address[] memory allowedSeaDrop      // <-- injected, not hardcoded
) ERC721ContractMetadata(name, symbol)
```
plus `updateAllowedSeaDrop(address[])` to change it later. The only
hardcoded `0x00005EA0…` in the whole `src/` tree is in
`clones/ERC721SeaDropCloneFactory.sol` — a factory we are not obliged to use.

**Therefore: we deploy ONLY our token (`ERC721SeaDrop`) and point its
`allowedSeaDrop` at the canonical address. ~19.8 KB instead of ~41 KB, and
we inherit audited, indexed infrastructure.**

---

## 7. ⚠️ CONSEQUENCE FOR TESTNET — HONEST ASSESSMENT

Canonical SeaDrop exists on **Arc mainnet** but is **absent on Arc testnet**
(doc 08, re-verified). So:

| what we can test on TESTNET | possible? |
|---|---|
| `ERC721SeaDrop` deploy, name/symbol/supply, owner, royalties | ✅ yes |
| `ERC721A` mint mechanics, transfers, enumeration | ✅ yes |
| Revert paths, access control, maxSupply enforcement | ✅ yes |
| **Full `mintPublic` through canonical SeaDrop** | ❌ **no — SeaDrop absent** |

**Options for the mint-path test — I will not guess which is right:**
- **A1** Deploy our self-compiled SeaDrop on **testnet only**, purely as a
  mint-path harness (never on mainnet). Non-canonical is acceptable for a
  rehearsal; we just must not claim it is canonical.
- **B1** Test the mint path on **mainnet** with a tiny 5-item supply
  (~0.045 native ≈ cents) against the real canonical SeaDrop.

**Recommendation: A1 then B1.** A1 costs nothing and exercises our token's
integration; B1 is the only way to prove the canonical wiring, and it is
trivially cheap.

⚠️ **Loss note:** B1 spends real mainnet gas (~0.05 native) and creates a
public 5-item collection. That contract would be permanent and visible.
We should use a throwaway name for it, **not** `Coinkins`, so the real brand
is not burned on a test artifact.

---

## 8. FILES THIS PHASE
```
seadrop/                    ProjectOpenSea/seadrop @ main (shallow) + 10 submodules
seadrop/out/                forge build artifacts
compare_seadrop.py          local-vs-Arc bytecode comparison + metadata stripping
analyze_diff.py             falsification test for the jumpdest-shift hypothesis
/usr/local/bin/solc-0.8.17  hash-verified official binary
```

## 9. STILL UNVERIFIED
- ⬜ Exact optimizer/via_ir settings OpenSea used (cause of the 38.7% delta)
- ⬜ Whether OpenSea's Arc UI lists a token pointed at canonical SeaDrop
- ⬜ ERC-20 USDC 6-decimal path (native 18-dec is proven)
- ⬜ `mintPublic` end-to-end (blocked on the A1/B1 decision above)
