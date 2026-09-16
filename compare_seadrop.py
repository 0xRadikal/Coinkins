#!/usr/bin/env python3
"""
compare_seadrop.py - Compare OUR locally compiled SeaDrop against the
SeaDrop already deployed on Arc mainnet.

Goal: determine whether we compiled the SAME contract. 33 bytes of
difference was observed; this explains exactly why.

Key insight: foundry.toml sets bytecode_hash = "none", which STRIPS the
CBOR metadata trailer. The Arc-deployed copy KEEPS its metadata
(we proved it contains "solc" 0.8.17 + ipfs hash). So a size delta equal
to the metadata length is expected and harmless.
"""
import json
import sys

sys.path.insert(0, '/webapp/arc-nft')
from arclib import rpc, MAINNET  # noqa: E402

ARTIFACT = '/webapp/arc-nft/seadrop/out/SeaDrop.sol/SeaDrop.json'
SEADROP_ADDR = '0x00005EA00Ac477B1030CE78506496e8C2dE24bf5'


def strip_metadata(hexstr):
    """
    Remove the CBOR metadata trailer.
    Layout: <code> <cbor> <2-byte big-endian cbor length>
    Returns (code_without_metadata, metadata_len).
    """
    b = bytes.fromhex(hexstr)
    if len(b) < 2:
        return hexstr, 0
    mlen = int.from_bytes(b[-2:], 'big')
    # sanity: metadata must fit and be plausible
    if 0 < mlen < 200 and mlen + 2 <= len(b):
        return b[:-(mlen + 2)].hex(), mlen + 2
    return hexstr, 0


def main():
    local = json.load(open(ARTIFACT))['deployedBytecode']['object']
    if local.startswith('0x'):
        local = local[2:]

    onchain = rpc(MAINNET, 'eth_getCode', [SEADROP_ADDR, 'latest'])['result'][2:]

    print("=== RAW SIZES ===")
    print(f"  local  (our compile) : {len(local)//2:,} bytes")
    print(f"  onchain (Arc)        : {len(onchain)//2:,} bytes")
    print(f"  delta                : {len(onchain)//2 - len(local)//2} bytes")
    print()

    l_strip, l_meta = strip_metadata(local)
    o_strip, o_meta = strip_metadata(onchain)
    print("=== METADATA TRAILERS ===")
    print(f"  local metadata   : {l_meta} bytes "
          f"({'stripped by bytecode_hash=none' if l_meta == 0 else 'present'})")
    print(f"  onchain metadata : {o_meta} bytes")
    print()

    print("=== AFTER STRIPPING METADATA ===")
    print(f"  local   : {len(l_strip)//2:,} bytes")
    print(f"  onchain : {len(o_strip)//2:,} bytes")
    print(f"  delta   : {len(o_strip)//2 - len(l_strip)//2} bytes")
    print()

    if l_strip == o_strip:
        print("  *** IDENTICAL *** our compile matches Arc exactly.")
        return

    # Not identical - locate and classify the differences
    a = bytes.fromhex(l_strip)
    b = bytes.fromhex(o_strip)
    n = min(len(a), len(b))
    diffs = [i for i in range(n) if a[i] != b[i]]
    print(f"  differing bytes: {len(diffs)} of {n} "
          f"({100*len(diffs)/n:.4f}%)")

    if not diffs:
        print("  (common prefix identical; only lengths differ)")
        return

    runs = []
    s = p = diffs[0]
    for i in diffs[1:]:
        if i == p + 1:
            p = i
        else:
            runs.append((s, p))
            s = p = i
    runs.append((s, p))
    print(f"  diff runs: {len(runs)}")
    for (s, e) in runs[:10]:
        print(f"    off {s}-{e} ({e-s+1}B)")
        print(f"      local  : {a[s:e+1].hex()[:64]}")
        print(f"      onchain: {b[s:e+1].hex()[:64]}")


if __name__ == '__main__':
    main()
