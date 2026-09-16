#!/usr/bin/env python3
"""
verify_deploy_sim.py - Simulate deploying our compiled contract on Arc,
WITHOUT spending anything and WITHOUT a private key.

Uses eth_call (to:null) to actually EXECUTE the constructor on the node,
and eth_estimateGas to get the real gas cost. This is the strongest
pre-deployment validation possible with no funds.
"""
import sys
sys.path.insert(0, '/webapp/arc-nft')
from arclib import (rpc, MAINNET, TESTNET, sample_base_fee,  # noqa: E402
                    priority_fee, to_int)

BIN_PATH = '/webapp/arc-nft/contracts/out/SmokeTest.bin'
# constructor takes uint256 initial -> encode 42
CTOR_ARG = hex(42)[2:].rjust(64, '0')
# a random unfunded address; proves no funds are needed to validate
PROBE_FROM = "0x1111111111111111111111111111111111111111"


def load_initcode():
    b = open(BIN_PATH).read().strip()
    if b.startswith('0x'):
        b = b[2:]
    return "0x" + b + CTOR_ARG


def main():
    init = load_initcode()
    print(f"init code bytes: {(len(init) - 2) // 2}")
    print(f"constructor arg: 42 (0x{CTOR_ARG[-4:]})")
    print()

    for label, url in (("TESTNET", TESTNET), ("MAINNET", MAINNET)):
        print("=" * 68)
        print(f"{label}")

        # 1. Execute the constructor for real (read-only)
        c = rpc(url, "eth_call",
                [{"to": None, "data": init, "from": PROBE_FROM}, "latest"])
        if "result" in c and c["result"] and c["result"] != "0x":
            runtime = c["result"]
            print(f"  constructor EXECUTED ok")
            print(f"  runtime code returned: {(len(runtime) - 2) // 2} bytes")
        elif "error" in c:
            print(f"  constructor REVERTED: {c['error']}")
            continue
        else:
            print(f"  constructor returned empty: {c}")

        # 2. Real gas estimate for the deploy
        g = rpc(url, "eth_estimateGas",
                [{"from": PROBE_FROM, "data": init}])
        if "result" not in g:
            print(f"  estimateGas failed: {g.get('error', g)}")
            continue
        gas = to_int(g["result"])
        print(f"  estimateGas: {gas:,} gas")

        # 3. Live fee data - never hardcoded
        st = sample_base_fee(url, n=6, stride=5)
        pf = priority_fee(url)
        if not st:
            print("  no basefee data")
            continue
        print(f"  baseFee  median={st['median']:.2f} gwei "
              f"(min {st['min']:.2f} / max {st['max']:.2f}, "
              f"spread {st['spread']:.2f}x)")
        if pf:
            print(f"  priority p50={pf['p50']:.3f} p90={pf['p90']:.3f} gwei")

        # 4. Cost in native units at a safe multiplier
        tip = pf['p50'] if pf else 0.0
        for mult in (1.5, 2.0):
            max_fee = st['median'] * mult + tip
            cost = gas * max_fee / 1e9
            print(f"  cost @ base*{mult} + tip = {max_fee:8.2f} gwei "
                  f"-> {cost:.6f} native")
        print()


if __name__ == "__main__":
    main()
