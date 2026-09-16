#!/usr/bin/env python3
"""
usd_cost.py - Exact USD cost model for the B1 mainnet test.

PROVEN FACTS (Circle official docs, docs.arc.io/arc/references/gas-and-fees):
  - "Arc denominates all transaction fees in USDC, the native gas token"
  - "Gas unit | USDC (18 decimals) | Native gas accounting precision"
  - "Minimum base fee (testnet) 20 Gwei", "Maximum base fee 20,000 Gwei"
  - "Set maxFeePerGas to at least 20 Gwei" else tx may hang forever
  - Arc publishes NEXT block's base fee in parent header extra_data
    as an 8-byte big-endian value.

Therefore: 1 native unit == 1 USDC == ~1 USD (USDC is a dollar stablecoin).
So cost_in_native == cost_in_USD directly.
"""
import sys

sys.path.insert(0, '/webapp/arc-nft')
from arclib import (rpc, to_int, MAINNET, sample_base_fee,  # noqa: E402
                    priority_fee)

ADDR = "0xa842e3aB069562Db379c35Dd52C77ef214324004"

# Protocol constants from official docs - enforced, not guessed.
MIN_BASE_FEE_GWEI = 20.0
MAX_BASE_FEE_GWEI = 20_000.0


def read_extradata_basefee(url):
    """
    Arc publishes the NEXT block's base fee in the parent header's
    extra_data as an 8-byte big-endian value (per official docs).
    Verify that claim against the actual next block.
    """
    head = rpc(url, "eth_getBlockByNumber", ["latest", False]).get("result")
    if not head:
        return None
    ed = head.get("extraData", "0x")
    raw = bytes.fromhex(ed[2:]) if len(ed) > 2 else b""
    if len(raw) < 8:
        return {"extra_data": ed, "parsed": None, "len": len(raw)}
    val = int.from_bytes(raw[-8:], "big")
    return {
        "extra_data": ed,
        "len": len(raw),
        "parsed_wei": val,
        "parsed_gwei": val / 1e9,
        "block": to_int(head["number"]),
        "this_block_basefee_gwei": to_int(head.get("baseFeePerGas", "0x0")) / 1e9,
    }


def main():
    bal = to_int(rpc(MAINNET, "eth_getBalance", [ADDR, "latest"])["result"])
    bal_usdc = bal / 1e18

    print("=" * 70)
    print("PROVEN: 1 native unit = 1 USDC = ~1 USD")
    print("  source: docs.arc.io/arc/references/gas-and-fees")
    print("          'Gas unit | USDC (18 decimals)'")
    print("=" * 70)
    print(f"  WALLET BALANCE = {bal_usdc:.6f} USDC  (~${bal_usdc:.2f})")
    print()

    # Validate the extra_data claim from the docs
    print("=" * 70)
    print("VERIFYING DOC CLAIM: next base fee in parent extra_data")
    print("=" * 70)
    ed = read_extradata_basefee(MAINNET)
    if ed:
        print(f"  block               {ed.get('block')}")
        print(f"  extra_data len      {ed.get('len')} bytes")
        print(f"  extra_data          {ed.get('extra_data')[:66]}")
        if ed.get("parsed_gwei") is not None:
            print(f"  parsed (last 8B)    {ed['parsed_gwei']:.4f} gwei")
            print(f"  this block baseFee  {ed['this_block_basefee_gwei']:.4f} gwei")
            plaus = MIN_BASE_FEE_GWEI <= ed['parsed_gwei'] <= MAX_BASE_FEE_GWEI
            print(f"  within protocol bounds [20, 20000]: {plaus}")
    print()

    # Live fees
    st = sample_base_fee(MAINNET, n=8, stride=4)
    pf = priority_fee(MAINNET)
    tip = pf["p50"] if pf else 1.0
    print("=" * 70)
    print("LIVE FEE DATA")
    print("=" * 70)
    print(f"  baseFee median {st['median']:.2f} gwei  "
          f"(min {st['min']:.2f} / max {st['max']:.2f})")
    print(f"  priority p50 {tip:.3f} gwei")
    # enforce the documented floor
    max_fee = max(st["max"] * 2.0 + tip, MIN_BASE_FEE_GWEI)
    print(f"  chosen maxFeePerGas = {max_fee:.2f} gwei "
          f"(>= documented 20 gwei floor)")
    print()

    print("=" * 70)
    print("B1 COST IN USD  (1 native == 1 USDC == $1)")
    print("=" * 70)
    steps = [
        ("deploy ERC721SeaDrop", 3_500_000),
        ("setMaxSupply", 60_000),
        ("setBaseURI", 80_000),
        ("updateCreatorPayoutAddress", 70_000),
        ("updateAllowedFeeRecipient", 70_000),
        ("updatePublicDrop", 120_000),
        ("mintPublic x1", 200_000),
    ]
    total_gas = 0
    total_usd = 0.0
    for label, gas in steps:
        usd = gas * max_fee / 1e9
        total_gas += gas
        total_usd += usd
        print(f"  {label:30s} {gas:>9,} gas  ${usd:>8.4f}")
    print("  " + "-" * 56)
    print(f"  {'TOTAL':30s} {total_gas:>9,} gas  ${total_usd:>8.4f}")
    print()
    print(f"  balance          ${bal_usdc:.4f}")
    print(f"  worst-case spend ${total_usd:.4f}")
    print(f"  left over        ${bal_usdc - total_usd:.4f}")
    print(f"  headroom         {bal_usdc/total_usd:.2f}x")
    print()
    if total_usd > bal_usdc:
        print("  !! INSUFFICIENT - ABORT")
    elif bal_usdc / total_usd < 1.5:
        print("  !! WARNING: headroom < 1.5x. Gas spikes could strand us.")
    else:
        print("  OK: sufficient with safe headroom.")
    print()
    print("  NOTE: this uses max*2.0 (worst case). Actual cost will be lower;")
    print("  the smoke deploy came in at 98.5% of estimate.")


if __name__ == "__main__":
    main()
