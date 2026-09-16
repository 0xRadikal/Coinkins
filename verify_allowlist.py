#!/usr/bin/env python3
"""
verify_allowlist.py - Prove the allowlist path exists on Arc's SeaDrop.

My earlier claim used selector 0x7d19bebe recalled from MEMORY, and I
could not locate it. The REAL selector, derived from the exact source
signature via `cast sig`, is 0x4300a4e6.

This script:
  1. searches Arc's deployed bytecode for the correct selectors
  2. CONFIRMS by live eth_call (behaviour, not byte-pattern)
  3. compares against our locally compiled ABI as a third source
"""
import json
import sys

sys.path.insert(0, '/webapp/arc-nft')
from arclib import rpc, MAINNET  # noqa: E402

SEADROP = '0x00005EA00Ac477B1030CE78506496e8C2dE24bf5'
ABI_PATH = '/webapp/arc-nft/seadrop/out/SeaDrop.sol/SeaDrop.json'

# selectors computed with `cast sig` from the exact source signatures
SELECTORS = {
    'mintPublic':             '161ac21f',
    'mintAllowList':          '4300a4e6',   # CORRECTED (was 7d19bebe)
    'mintSigned':             '4b61cd6f',
    'mintAllowedTokenHolder': 'd734375a',   # CORRECTED (was edf7c6a2)
    'updateAllowList':        '20351c01',
    'getAllowListMerkleRoot': '32bf11f5',
    'updatePublicDrop':       '01308e65',
    'getPublicDrop':          'bc6a629c',
    'updateCreatorPayoutAddress': '12738db8',
    'updateAllowedFeeRecipient':  '8e7d1e43',
}


def main():
    code = rpc(MAINNET, 'eth_getCode', [SEADROP, 'latest'])['result'][2:]
    print(f"Arc SeaDrop bytecode: {len(code)//2:,} bytes\n")

    print("=" * 66)
    print("1. BYTECODE SELECTOR SEARCH")
    print("=" * 66)
    found = {}
    for name, sel in SELECTORS.items():
        hit = sel in code
        found[name] = hit
        print(f"  {name:28s} 0x{sel}  {'FOUND' if hit else '*** NOT FOUND ***'}")

    print()
    print("=" * 66)
    print("2. LIVE eth_call CONFIRMATION (behaviour, not bytes)")
    print("=" * 66)
    # getAllowListMerkleRoot(address) -> bytes32 ; should return 32 zero bytes
    # for an unconfigured token, NOT an 'invalid selector' style failure.
    probe = '0x32bf11f5' + '0' * 24 + '1' * 40
    r = rpc(MAINNET, 'eth_call', [{'to': SEADROP, 'data': probe}, 'latest'])
    if 'result' in r:
        print(f"  getAllowListMerkleRoot(dummy) -> {r['result']}")
        print(f"    returned {len(r['result'])-2} hex chars "
              f"({(len(r['result'])-2)//2} bytes)")
        print("    => function EXISTS and is callable "
              "(a missing function would revert)")
    else:
        print(f"  getAllowListMerkleRoot -> {r.get('error')}")

    # getPublicDrop for comparison (known-good control)
    probe2 = '0xbc6a629c' + '0' * 24 + '1' * 40
    r2 = rpc(MAINNET, 'eth_call', [{'to': SEADROP, 'data': probe2}, 'latest'])
    if 'result' in r2:
        print(f"  CONTROL getPublicDrop(dummy)  -> "
              f"{(len(r2['result'])-2)//2} bytes returned")

    print()
    print("=" * 66)
    print("3. LOCAL ABI CROSS-CHECK (third independent source)")
    print("=" * 66)
    abi = json.load(open(ABI_PATH))['abi']
    names = {e.get('name') for e in abi if e.get('type') == 'function'}
    for n in ('mintPublic', 'mintAllowList', 'mintSigned',
              'mintAllowedTokenHolder', 'updateAllowList',
              'getAllowListMerkleRoot'):
        print(f"  {n:28s} in compiled ABI: {n in names}")

    print()
    print("=" * 66)
    print("VERDICT")
    print("=" * 66)
    need = ['mintPublic', 'mintAllowList', 'updateAllowList',
            'getAllowListMerkleRoot', 'updatePublicDrop']
    missing = [n for n in need if not found.get(n)]
    if missing:
        print(f"  BLOCKED - not located in bytecode: {missing}")
    else:
        print("  ALL required functions present. Two-phase plan is feasible.")


if __name__ == '__main__':
    main()
