# Coinkins — Arc NFT Launch Project

**Persistent memory for this project.** Everything verified is recorded here so
nothing is lost between sessions. Read this file first.

---

## STATUS AT A GLANCE (2026-09-16)

| item | status |
|---|---|
| Chain decision | **Arc mainnet**, chainId **5042** |
| Brand name | **Coinkins** (chosen by naming science, doc 06) |
| Technical feasibility | ✅ **PROVEN ON MAINNET** — 9/9 txs, $0.2248 |
| OpenSea indexing on Arc | ✅ **CONFIRMED** (auto-indexed with slug) |
| Allowlist merkle mint | ✅ **WORKS** |
| Paid public mint (0.1 USDC) | ✅ **WORKS** |
| Blue check | ❌ not achieved — blocked on **demand**, not code |
| Real launch | ⏸ not started |

---

## THE ONE THING THAT MATTERS

> **Technical risk is ~zero. The entire remaining risk is DEMAND.**

Measured (doc 07): Arc has **0 verified collections** and **0 volume** across
100 collections scanned. The OpenSea blue check requires **$50,000 volume
(including mint) AND all items minted/revealed**.

A full 1000-supply drop costs **~$0.22 in gas**. Money is not the constraint.
**Buyers are.**

---

## PROVEN FACTS (do not re-derive these)

### Arc chain
```
mainnet RPC   https://rpc.mainnet.arc.io     chainId 5042    (0x13b2)
testnet RPC   https://rpc.testnet.arc.io     chainId 5042002 (0x4cef52)
testnet alt   https://rpc.drpc.testnet.arc.io
client        arc/v1
block time    ~0.5 s      block gas limit 30,000,000
EVM           Osaka hard fork (Cancun opcodes all verified working)
```

### Gas / native token — CRITICAL
```
native gas token  = USDC at 18 DECIMALS   (docs.arc.io/arc/references/gas-and-fees)
=> 1 native unit == 1 USDC == ~$1
min base fee      = 20 gwei   (protocol floor; below this, tx hangs forever)
max base fee      = 20,000 gwei (hard ceiling)
observed range    = 31 - 299 gwei within a few hours -> ALWAYS read live
eth_maxPriorityFeePerGas returns 0 -> DO NOT TRUST IT, use eth_feeHistory
next block's base fee is in parent header extra_data (8 bytes, big-endian) - verified
```

### Deployed infrastructure
```
                        MAINNET      TESTNET
SeaDrop (canonical)     21,081 B     ABSENT     0x00005EA00Ac477B1030CE78506496e8C2dE24bf5
Seaport 1.6             23,981 B     ABSENT
ConduitController        8,820 B     ABSENT
CreateX                 11,838 B     11,838 B
Create2Factory              69 B         69 B
Multicall3               3,808 B      3,808 B
Permit2                  9,152 B      9,152 B
ERC-6551 Registry        ABSENT          571 B
```
**Arc's SeaDrop is byte-authentic**: differs from Ethereum's canonical copy by
exactly 34 bytes = chainId (`0x13b2` vs `0x0001`) + derived EIP-712 domain
separator. Compiled by **solc 0.8.17** (extracted from CBOR metadata).

⚠️ **NEVER deploy our own SeaDrop.** Our local compile is NOT byte-equivalent
(469 distinct byte deltas, 38.7% differ — doc 11). Use the canonical address.

### Correct selectors (derived with `cast sig`, verified in bytecode)
```
SeaDrop side:
  mintPublic                        0x161ac21f
  mintAllowList                     0x4300a4e6   (NOT 0x7d19bebe)
  mintSigned                        0x4b61cd6f
  mintAllowedTokenHolder            0xd734375a   (NOT 0xedf7c6a2)
  updateAllowList(AllowListData)    0xebb4a55f
  getAllowListMerkleRoot            0x32bf11f5
  updatePublicDrop(PublicDrop)      0x01308e65
  getPublicDrop                     0xbc6a629c

Token side (WE call these; SeaDrop setters are onlyINonFungibleSeaDropToken):
  updateAllowList(addr,ALD)         0x3680620d
  updatePublicDrop(addr,PD)         0x1b73593c
  updateCreatorPayoutAddress(a,a)   0x66251b69
  updateAllowedFeeRecipient(a,a,b)  0x48a4c101
  setMaxSupply(uint256)             0x6f8b44b0
  setBaseURI(string)                0x55f804b3
```

### Structs (field order matters for encoding)
```solidity
struct PublicDrop {            // uint80 price! max ~1,208,925 USDC
    uint80 mintPrice; uint48 startTime; uint48 endTime;
    uint16 maxTotalMintableByWallet; uint16 feeBps; bool restrictFeeRecipients;
}
struct MintParams {            // all uint256 + bool
    uint256 mintPrice, maxTotalMintableByWallet, startTime, endTime,
            dropStageIndex /* MUST be non-zero */, maxTokenSupplyForStage, feeBps;
    bool restrictFeeRecipients;
}
struct AllowListData { bytes32 merkleRoot; string[] publicKeyURIs; string allowListURI; }
```

### Merkle allowlist
```
leaf = keccak256(abi.encode(minter, mintParams))      // abi.encode, NOT packed
                                                       // = 288 bytes for 1 entry
1-entry tree: root == leaf, proof == []               // proven from OZ processProof
```

### Payment
```solidity
if (msg.value != quantity * mintPrice) revert IncorrectPayment(...);
```
Payment is **native USDC via msg.value**. No ERC-20 approve. Must be EXACT.
`feeBps <= 10_000` enforced. Payout goes to `creatorPayoutAddress`.

### ERC721A quirk
Token IDs start at **1**, not 0. `ownerOf(0)` reverts / is nonexistent.

---

## B1 MAINNET PROOF — what we actually deployed

```
TOKEN      0xd80266b6f0c021e6a606a51d10c19e9c5cc9a846
name       "Arc Pathfinder Test"   symbol "APFT"
maxSupply  1000    totalSupply 2   owner = our wallet
OpenSea    https://opensea.io/collection/arc-pathfinder-test
deploy tx  0x717a8030e952c2ab08e7ed61a0e6f8d13932e4655ebe6e540c3cdef5386fef11
cost       $0.224763 total for 9 transactions
```
⚠️ **Throwaway harness.** 2 of 1000 minted → "all items minted" fails
permanently → can never be verified. Intentional. The `Coinkins` brand is
deliberately NOT used here.

### Real gas costs measured
```
deploy ERC721SeaDrop   4,507,488 gas   $0.198958
setMaxSupply              49,076 gas   $0.002201
setBaseURI                95,880 gas   $0.004312
updateCreatorPayout       54,598 gas   $0.002468
updateAllowedFeeRecip     99,990 gas   $0.004205
updateAllowList                         $0.002388
mintAllowList (free)                    $0.003939
updatePublicDrop                        $0.002369
mintPublic (0.1 USDC)                   $0.003923
```

---

## WALLET
```
0xa842e3aB069562Db379c35Dd52C77ef214324004
key at /root/wallet-test.env  (NEVER committed; .gitignore blocks it)
```
Audited across 8 chains: zero balance and **nonce 0 on Ethereum, Base,
Arbitrum, Optimism, Polygon, BSC**. Only Arc has funds. Safe throwaway.

---

## TOOLCHAIN
```
Foundry v1.8.1     /root/.foundry/bin/  (forge, cast, anvil) - NOT on PATH
solc 0.8.17        /usr/local/bin/solc-0.8.17   (for SeaDrop - hash verified)
solc 0.8.24        /usr/local/bin/solc          (general - hash verified)
Node v12.22.9      too old for Hardhat; unused
python3 3.10.12    primary tooling
disk               ~1.7 GB free - keep clones shallow
```
⚠️ **Bash tool fails on large heredocs.** Write `.py` files with the Write
tool and run them with a short command. This was diagnosed by bisection.

### Rebuild the SeaDrop dependency (excluded from this repo)
```bash
cd /webapp/arc-nft
git clone --depth 1 https://github.com/ProjectOpenSea/seadrop.git
cd seadrop && git submodule update --init --recursive --depth 1
forge build --use /usr/local/bin/solc-0.8.17
```

---

## SCRIPTS
| file | purpose |
|---|---|
| `arclib.py` | RPC toolkit + live gas sampling + self-tests |
| `check_wallet.py` | 8-chain balance/nonce safety audit |
| `deploy_b1.py` | 9-tx mainnet executor, 7 safety gates, resumable |
| `verify_final.py` | independent chain read-back |
| `build_allowlist.py` | merkle root, dual-implementation verified |
| `probe_evm.py` | on-chain opcode support proof |
| `verify_allowlist2.py` | selector verification both sides |
| `usd_cost.py` | USD cost model from live gas |
| `name_science.py` | research-cited brand name scorer |
| `check_names.py` | X / domain / OpenSea availability checker |

**Safety gates in `deploy_b1.py`:** chainId, address match, total spend cap,
20-gwei floor, balance check, live gas per tx, abort on status != 0x1.

---

## DOCUMENT INDEX
| doc | contents |
|---|---|
| 00 | archived Rare Friends mint-bot knowledge |
| 01–03 | early research — **contains errors, superseded** |
| 04 | 10 corrections to docs 01–03 |
| 05 | merged concept A+B roadmap, phases 0–5 |
| 06 | **name science → Coinkins** |
| 07 | **benchmark evidence: Arc has zero demand** |
| 08 | preflight verification, SeaDrop authenticity |
| 09 | toolchain fixed, faucet found |
| 10 | first testnet deploy success |
| 11 | SeaDrop build + falsified hypothesis |
| 12 | B1 plan |
| 13 | two-phase plan |
| 14 | **B1 results — full success** |

---

## NEXT DECISIONS (open)
1. Register the 5 `Coinkins` surfaces (X, .xyz, .io, .com, OpenSea) in one sitting
2. **USER ACTION:** USPTO TESS + WIPO trademark search, classes 9 & 42
3. Decide real supply/price — must be able to **sell out**
4. Solve **demand** — the only unsolved problem

## STILL UNVERIFIED
- ⬜ Whether OpenSea's drop UI renders a mint button (API indexing confirmed, UI not)
- ⬜ `tokenURI(1)` metadata rendering
- ⬜ Secondary trading / royalty enforcement on Arc
- ⬜ ERC-20 6-decimal USDC path (unused; SeaDrop takes native 18-dec)
- ⬜ Trademark clearance for "Coinkins"
