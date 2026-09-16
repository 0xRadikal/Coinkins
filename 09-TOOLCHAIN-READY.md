# 09 — TOOLCHAIN FIXED & VALIDATED (2026-09-16)
**Scope:** fix the broken Bash tool, then verify every prerequisite for Phase 1 (Option A).
**Every number below was measured. Nothing is assumed.**

---

## 1. ROOT CAUSE OF THE BASH TOOL FAILURES — FOUND AND FIXED

I did not guess. I bisected it:

| test | result |
|---|---|
| `echo OK1` | ✅ works |
| `printf > file && cat` | ✅ works |
| heredoc, 2 lines | ✅ works |
| heredoc, 40+ lines with quotes/f-strings | ❌ **FAILS** |

**Root cause: large multi-line heredocs**, not bash itself.

**Fix applied:** all non-trivial logic now lives in **real `.py` files** written
with the `Write` tool and invoked with a one-line command
(`python3 script.py`). Since applying this, **every** Bash call has succeeded.

Reusable library created: **`arclib.py`** — with self-tests that assert
`to_int('0x13b2')==5042` and that each RPC reports its expected chainId.
Self-test result: **all assertions pass.**

---

## 2. ⚠️ THE WALLET FILE IS A PLACEHOLDER — NO FUNDS EXIST

You asked me to use the wallet in `wallet-test.env` / `test-wallet.env`.
I searched the **entire filesystem** (`find / -maxdepth 5`). Exactly one match:

```
/tmp/test_wallet.env   (36 bytes, dated Sep 12)
contents: private-key=0xYOUR_PRIVATE_KEY_HERE
```

**That is literal placeholder text, not a key.** Additional checks:
- `grep -rlE "0x[0-9a-fA-F]{64}"` across `rf-mint/` → **no key anywhere**
- `rf-mint/config.json` → `"dry_run": true` (it never ran with real funds)

**I will not invent, guess, or generate a key and call it yours.**
Nothing can be deployed until you provide a funded key. See §7.

---

## 3. ✅ TESTNET FAUCET FOUND — VIA DOCS, NOT GUESSWORK

My guessed URLs (`faucet.testnet.arc.io`, `faucet.arc.io`, …) **all failed DNS**.
So I parsed the real `href`s out of `docs.arc.io` and found:

```
https://faucet.circle.com     <- official Circle faucet
```
Verified it actually supports Arc:
```
{"name":"ARC","currencies":["USDC","EURC","CIRBTC"],
 "limits":{"ms":3600000},"priority":2,"maintenanceMode":false}
UI label: "Arc Testnet"
feature flag present: arcFaucetEnabled
```
**Arc Testnet faucet is live, rate limit 3,600,000 ms = 1 hour, not in maintenance.**
Currencies: USDC, EURC, CIRBTC.

⚠️ Unverified: the exact **amount** per drip (not exposed in the page payload) and whether it needs a Circle login/captcha (`recaptchaEnabled` flag exists).

---

## 4. ✅ EXPLORER + CONTRACT VERIFICATION AVAILABLE

| endpoint | status |
|---|---|
| `explorer.testnet.arc.io` | **LIVE**, Blockscout **v11.3.0** |
| `explorer.arc.io` (mainnet) | LIVE for humans; **HTTP 403** to bots (Cloudflare) |
| `/api/v2/stats` | **HTTP 200** |
| `/api/v2/smart-contracts/verification/config` | **HTTP 200** |

Testnet explorer stats (live):
```
average_block_time  510.0 ms      (matches the 0.5 s figure)
gas_prices          slow 21.37 / average 24.1 / fast 32.18 gwei
network_utilization 4.97 %
```

Verification capability:
```
solidity_compiler_versions : 1657 available (newest v0.8.36)
verification_options       : multi-part, standard-input, flattened-code,
                             sourcify, vyper-*
rust_verifier_microservice : enabled
evm_versions               : ... shanghai, cancun, prague, osaka, default
```
**Contract verification on testnet is fully supported.**

---

## 5. ✅ EVM COMPATIBILITY — PROVEN BY EXECUTION, NOT DOCS

I executed real opcodes on-chain via `eth_call` with `to:null`. Each test
returns a **distinct** value so the result cannot be misread:

| opcode | fork | MAINNET | TESTNET |
|---|---|---|---|
| `PUSH1` baseline | — | ✅ → **42** | ✅ → **42** |
| `PUSH0` (0x5f) | Shanghai | ✅ → 0 | ✅ → 0 |
| `MCOPY` (0x5e) | Cancun | ✅ → **42** | ✅ → **42** |
| `TLOAD` (0x5c) | Cancun | ✅ → 0 | ✅ → 0 |
| `BASEFEE` (0x48) | London | ✅ | ✅ |
| `CHAINID` (0x46) | Istanbul | ✅ → **5042** | ✅ → **5042002** |

The harness is self-validating: `PUSH1 → 42` proves the method works,
`MCOPY → 42` proves real memory movement, and `CHAINID` independently
confirms **which chain each RPC is**.

**Conclusion: full Cancun support on both networks. `evmVersion: cancun` is safe.**

---

## 6. ✅ COMPILER INSTALLED, INTEGRITY VERIFIED

Chose the official standalone binary over Hardhat/Foundry because
**Node is v12.22.9** (Hardhat needs ≥18) and only **1.8 GB disk** is free.

```
expected sha256 (binaries.soliditylang.org): 0xfb03a29a...37c30d5f
actual   sha256 (downloaded):                  fb03a29a...37c30d5f
                                               ^^ EXACT MATCH
solc 0.8.24+commit.e11b9ed9.Linux.g++   (15 MB)
disk after install: still 1.8 GB free
```

### Compile + execute proof
```
solc --evm-version cancun --optimize --optimize-runs 200
  -> Compiler run successful
  -> SmokeTest.bin = 512 bytes, begins 60a0604052348015 61000f 575f80fd5b
                                                              ^^^^ 5f = PUSH0
```
PUSH0 in the output proves the Cancun/Shanghai codegen is genuinely active —
matching the on-chain PUSH0 support measured in §5.

### Deploy simulated on BOTH networks (no key, no funds, no spend)
`eth_call` with `to:null` **actually executed the constructor**:
```
             constructor   runtime returned   estimateGas
TESTNET      EXECUTED ok   403 bytes          165,763 gas
MAINNET      EXECUTED ok   403 bytes          165,763 gas
```
Identical results on both → the pipeline `solc → bytecode → Arc EVM` works.

### Live cost (never hardcoded)
```
TESTNET  baseFee 20.00 gwei (spread 1.00x)  tip p50 2.800  -> 0.005437 native @1.5x
MAINNET  baseFee 162.05     (spread 1.33x)  tip p50 30.597 -> 0.045364 native @1.5x
                            min 141.55 / max 188.86
```
⚠️ Mainnet baseFee observed **84.74 → 162.05 → 274.54 gwei** within one hour
(**3.2x swing**). Any hardcoded gas value is guaranteed wrong. `arclib`
always samples live.

---

## 7. 🚧 THE ONE REMAINING BLOCKER

Everything technical is ready. **The only missing input is a funded key.**

| requirement | status |
|---|---|
| RPC endpoints | ✅ 3 live |
| SeaDrop authenticity | ✅ proven byte-identical (doc 08) |
| Permissionless deploy | ✅ proven |
| EVM/Cancun support | ✅ proven by execution |
| Compiler | ✅ installed, hash-verified |
| Compile → execute pipeline | ✅ proven on both nets |
| Testnet explorer + verification | ✅ live |
| Testnet faucet | ✅ live (`faucet.circle.com`) |
| **Funded private key** | ❌ **placeholder only** |

### What you need to do (I cannot do these)
1. **Create a brand-new throwaway wallet** for testnet. Never reuse a wallet
   holding real assets.
2. Claim Arc Testnet funds at **https://faucet.circle.com** (choose "Arc Testnet").
3. Put the key in `/webapp/arc-nft/.env` as `PRIVATE_KEY=0x...`
   — I will add `.env` to `.gitignore` before anything is committed.

⚠️ **Loss warning:** a testnet key must be a **fresh** wallet. If you paste a
key that also controls mainnet funds, a mistake could move real money.
Testnet funds are worthless, so the key protecting them should be worthless too.

---

## 8. CORRECTIONS TO MY OWN EARLIER WORK

| # | earlier | corrected |
|---|---|---|
| 1 | "Bash tool is broken/degraded" | **Large heredocs** were the cause. Fixed by using files. |
| 2 | Phase 1 needs testnet SeaDrop (doc 08) | Still true — SeaDrop absent on testnet, so **we deploy our own** (Option A) |
| 3 | gas 274.54 gwei median (doc 08) | now **162.05**; observed 84.74–274.54 in one hour → **live sampling mandatory** |
| 4 | "solc install may not fit in 1.8 GB" | ✅ fits — 15 MB, disk unchanged at 1.8 GB free |
| 5 | assumed a funded test wallet existed | ❌ **it is a 36-byte placeholder** |

---

## 9. FILES ADDED THIS PHASE

```
arclib.py                  RPC toolkit + self-tests (all pass)
probe_faucet.py            faucet/explorer discovery
probe_evm.py               on-chain opcode proof
verify_deploy_sim.py       keyless deploy simulation + live costing
contracts/SmokeTest.sol    toolchain validation contract (never on mainnet)
contracts/out/             compiled artifacts (512 B bin, abi)
```

## 10. STILL UNVERIFIED — stated, not guessed
- ⬜ Faucet drip **amount** per request, and whether login/captcha is required
- ⬜ Whether OpenSea's Arc drop UI accepts a **self-deployed** SeaDrop token
- ⬜ Mainnet contract verification (explorer blocks bots; may need manual UI)
- ⬜ Trademark clearance for `Coinkins` (**your action** — USPTO/WIPO cl. 9 & 42)
