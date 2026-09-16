# ARCHIVE — Rare Friends Genesis mint bot (closed 2026-09-16)

Status: **abandoned by decision** — the team kept postponing the public stage.
Service stopped and disabled: `systemctl is-active rf-mint` -> inactive/disabled.
Code kept at `/webapp/rf-mint/` (86/86 tests passing) in case it is ever useful.

## What was built
A production mint bot for OpenSea SeaDrop collections on Robinhood Chain (4663).

- `mint_bot.py` — pre-signs the tx, waits on **chain time**, fires at T+0
- `preflight.py` — 17 read-only on-chain checks
- `run_mint.sh` — launcher, reads the window **from chain**, auto-restarts
- `rf-mint.service` — systemd unit with exit-code-aware restart policy
- `status.sh` — read-only health/countdown report
- `test_suite.py` — 86 tests

## Verified technical findings (reusable knowledge)

### Robinhood Chain
- chainId **4663**, Arbitrum Orbit rollup, ETH gas
- block time measured at **exactly 0.100 s**
- sequencer is **FIFO** — higher gas buys nothing, only latency matters
- fastest RPC measured: `robinhood.drpc.org` **42 ms** vs official **117 ms**
- `drpc` free plan refuses `eth_getLogs` over 10k blocks; official RPC allows it

### OpenSea SeaDrop architecture
Canonical SeaDrop: `0x00005EA00Ac477B1030CE78506496e8C2dE24bf5`
Four independent mint stages, each a different function:

| Stage | Selector | Requirement |
|---|---|---|
| Public | `mintPublic` `0x161ac21f` | nothing |
| Allowlist | `mintAllowList` `0x7d19bebe` | merkle proof |
| Signed | `mintSigned` `0x4b61cd6f` | server signature |
| Token-gated | `mintAllowedTokenHolder` `0xedf7c6a2` | holding another NFT |

NFT contracts have **no** public `mint()`. The only entry is via SeaDrop.

### Hard-won lessons (each cost a real bug)
1. **Never hardcode the mint window.** Rare Friends moved its public stage
   +12 h mid-flight (`04:00` -> `16:00` UTC). Read `getPublicDrop()` live and
   re-poll while waiting.
2. **Never fire early.** A tx submitted before `startTime` IS accepted into the
   pool but is mined as a **FAILED** tx, burning the nonce. Proven on a fork.
3. **Arbitrum reserves `maxFee * gasLimit` upfront**, even though unused gas is
   refunded. A 5 gwei / 500k config reserved 0.0025 ETH and returned
   `Insufficient funds` on a wallet holding 0.00039 ETH.
4. **SeaDrop versions differ.** One collection had `totalMinted()` but not
   `totalSupply()`; another the exact opposite. Fall back across both plus
   `getMintStats()`.
5. **Mint to a plain EOA.** A contract/AA wallet reverts in `onERC721Received`.
6. **`StartLimitIntervalSec` belongs in `[Unit]`**, not `[Service]` — systemd
   silently ignores it there, so the restart limit stays active and systemd can
   give up mid-window.
7. **Scam CAs circulate on X.** `0x56ab53b7...` was pushed as the Rare Friends
   contract; it has no code on that chain at all. Always resolve the contract
   from the OpenSea API **and** verify on-chain.

### Proven results
- **3 Seconds** (user's test collection): minted **token #1** on live mainnet,
  submit->confirmed in **728 ms**. Collection later sold out 1000/1000.
- Watchdog test on a fork: window moved mid-wait -> detected -> re-scheduled ->
  minted, detect-to-fire **1 ms**.
- Real gas cost per mint: **~0.0000151 ETH** (~5 cents).

## Why it was abandoned
Rare Friends' 1024 supply was being consumed almost entirely through
`mintSigned` (whitelist). At abandonment: **907/1024 minted, 117 left**, and the
public window had already been pushed twice. Not worth waiting on.
