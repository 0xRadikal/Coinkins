#!/usr/bin/env python3
"""
check_wallet.py - SAFETY AUDIT of the test wallet before any transaction.

Checks whether this address holds real value on Arc mainnet and on major
L1/L2s. If it holds real money, we MUST NOT use it for testnet experiments.

Read-only. No private key is loaded here - address only.
"""
import sys
sys.path.insert(0, '/webapp/arc-nft')
from arclib import rpc, to_int, MAINNET, TESTNET  # noqa: E402

ADDR = "0xa842e3aB069562Db379c35Dd52C77ef214324004"

NETS = {
    "Arc MAINNET":  MAINNET,
    "Arc TESTNET":  TESTNET,
    "Ethereum":     "https://ethereum-rpc.publicnode.com",
    "Base":         "https://base-rpc.publicnode.com",
    "Arbitrum":     "https://arbitrum-one-rpc.publicnode.com",
    "Optimism":     "https://optimism-rpc.publicnode.com",
    "Polygon":      "https://polygon-bor-rpc.publicnode.com",
    "BSC":          "https://bsc-rpc.publicnode.com",
}


def main():
    print(f"AUDITING ADDRESS: {ADDR}")
    print("=" * 70)
    risk = []
    for name, url in NETS.items():
        bal = rpc(url, "eth_getBalance", [ADDR, "latest"], tries=2)
        nonce = rpc(url, "eth_getTransactionCount", [ADDR, "latest"], tries=2)
        if "result" not in bal:
            print(f"  {name:14s} UNREACHABLE ({bal.get('_err', bal.get('error'))})")
            continue
        wei = to_int(bal["result"])
        n = to_int(nonce.get("result", "0x0")) if "result" in nonce else None
        eth = wei / 1e18
        flag = ""
        if wei > 0:
            flag = "  <-- HAS BALANCE"
            if name not in ("Arc TESTNET",):
                risk.append((name, eth))
        print(f"  {name:14s} balance={eth:.18f}  nonce={n}{flag}")

    print()
    print("=" * 70)
    if risk:
        print("!! WARNING: real-value balances found on:")
        for n, e in risk:
            print(f"     {n}: {e} native")
        print("   DO NOT use this wallet for experiments.")
    else:
        print("OK: no balance on any mainnet checked.")
        print("    This wallet is safe to use as a throwaway test wallet.")


if __name__ == "__main__":
    main()
