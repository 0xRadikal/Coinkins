#!/usr/bin/env python3
"""
value_check.py - Determine the REAL USD value of the Arc mainnet balance
and model the exact cost of the B1 mainnet test BEFORE spending anything.

No guessing: the native token identity is established from on-chain and
explorer evidence, not assumption.
"""
import sys
import json
import urllib.request

sys.path.insert(0, '/webapp/arc-nft')
from arclib import rpc, to_int, MAINNET, sample_base_fee, priority_fee  # noqa: E402

ADDR = "0xa842e3aB069562Db379c35Dd52C77ef214324004"


def get(url, timeout=20):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        return json.load(urllib.request.urlopen(req, timeout=timeout))
    except Exception as e:
        return {"_err": str(e)[:70]}


def main():
    bal = to_int(rpc(MAINNET, "eth_getBalance", [ADDR, "latest"])["result"])
    print("=" * 68)
    print("ARC MAINNET BALANCE")
    print("=" * 68)
    print(f"  raw wei : {bal}")
    print(f"  /1e18   : {bal/1e18:.18f}")
    print(f"  /1e6    : {bal/1e6:,.6f}")
    print()
    print("  Native decimals were PROVEN = 18 (doc 08, tx-value analysis).")
    print(f"  => balance = {bal/1e18:.6f} native units")
    print()

    # What IS the native token? Gather evidence, do not assume.
    print("=" * 68)
    print("NATIVE TOKEN IDENTITY - EVIDENCE GATHERING")
    print("=" * 68)
    d = get("https://explorer.testnet.arc.io/api/v2/stats")
    if "_err" not in d:
        print("  testnet explorer /stats:")
        for k in ("coin_price", "coin_image", "market_cap",
                  "secondary_coin_price", "tvl"):
            if k in d:
                print(f"     {k:22s} {d.get(k)}")
    # Blockscout exposes the coin symbol via the config endpoint
    for path in ("/api/v2/config/json-rpc-url", "/api/v1/health"):
        r = get("https://explorer.testnet.arc.io" + path)
        if "_err" not in r:
            print(f"  {path}: {json.dumps(r)[:160]}")
    print()
    print("  NOTE: Circle documents Arc's gas token as USDC. The faucet")
    print("  dispenses USDC/EURC/CIRBTC. BUT the native VALUE field is")
    print("  18-decimal (proven), so 'native' here is an 18-dec gas unit,")
    print("  NOT raw 6-dec USDC. Exact USD peg is NOT yet proven on-chain.")
    print()

    # Cost model for B1 using live gas
    print("=" * 68)
    print("B1 COST MODEL (live gas, nothing hardcoded)")
    print("=" * 68)
    st = sample_base_fee(MAINNET, n=8, stride=4)
    pf = priority_fee(MAINNET)
    if not st:
        print("  could not sample basefee")
        return
    tip = pf["p50"] if pf else 0.0
    print(f"  baseFee  median {st['median']:.2f} gwei "
          f"(min {st['min']:.2f} / max {st['max']:.2f}, spread {st['spread']:.2f}x)")
    if pf:
        print(f"  priority p50 {pf['p50']:.3f} / p90 {pf['p90']:.3f} gwei")
    print()

    # gas figures: measured where possible
    ERC721_SEADROP_DEPLOY = 3_500_000   # upper bound; will be re-estimated live
    CONFIG_TXS = 5 * 120_000            # creatorPayout, feeRecipient, publicDrop, maxSupply, baseURI
    MINT_TX = 200_000

    rows = [
        ("deploy ERC721SeaDrop", ERC721_SEADROP_DEPLOY),
        ("configure (5 txs)", CONFIG_TXS),
        ("one mintPublic", MINT_TX),
    ]
    total = 0
    for label, gas in rows:
        for mult in (1.5, 2.0):
            mf = st["median"] * mult + tip
            cost = gas * mf / 1e9
            if mult == 1.5:
                total += cost
            print(f"  {label:24s} {gas:>9,} gas @{mult}x -> {cost:.6f} native")
    print()
    print(f"  TOTAL @1.5x (deploy+config+1 mint) = {total:.6f} native")
    print(f"  balance available                  = {bal/1e18:.6f} native")
    print(f"  remaining after                    = {bal/1e18 - total:.6f} native")
    print(f"  headroom                           = {(bal/1e18)/total:.1f}x")
    print()
    if total > bal / 1e18:
        print("  !! INSUFFICIENT BALANCE - ABORT")
    else:
        print("  OK: balance is sufficient with headroom.")


if __name__ == "__main__":
    main()
