#!/usr/bin/env python3
"""
verify_allowlist2.py - FINAL verification of the two-phase (allowlist + public)
plan, using selectors derived from the EXACT source struct definitions.

Two selector mistakes I made and corrected:
  mintAllowList   0x7d19bebe (memory, WRONG) -> 0x4300a4e6 (cast sig, CORRECT)
  updateAllowList 0x20351c01 (bytes32, WRONG) -> 0xebb4a55f (AllowListData)

Key architectural fact found in source: configuration goes through the
TOKEN (ERC721SeaDrop), which then calls SeaDrop. SeaDrop's setters carry
`onlyINonFungibleSeaDropToken`, so the token must be the caller - not us.
"""
import json
import sys

sys.path.insert(0, '/webapp/arc-nft')
from arclib import rpc, MAINNET  # noqa: E402

SEADROP = '0x00005EA00Ac477B1030CE78506496e8C2dE24bf5'
SD_ABI = '/webapp/arc-nft/seadrop/out/SeaDrop.sol/SeaDrop.json'
TK_ABI = '/webapp/arc-nft/seadrop/out/ERC721SeaDrop.sol/ERC721SeaDrop.json'

# SeaDrop-side (called BY the token, or by minters)
SEADROP_SELS = {
    'mintPublic':             '161ac21f',
    'mintAllowList':          '4300a4e6',
    'updateAllowList(ALD)':   'ebb4a55f',
    'getAllowListMerkleRoot': '32bf11f5',
    'updatePublicDrop(PD)':   '01308e65',
    'getPublicDrop':          'bc6a629c',
}

# TOKEN-side (called BY US, the owner)
TOKEN_SELS = {
    'updateAllowList(addr,ALD)':        '3680620d',
    'updatePublicDrop(addr,PD)':        '1b73593c',
    'updateCreatorPayoutAddress(a,a)':  '66251b69',
    'updateAllowedFeeRecipient(a,a,b)': '48a4c101',
    'setMaxSupply':                     '6f8b44b0',
    'setBaseURI':                       '55f804b3',
}


def check(code, sels, label):
    print("=" * 66)
    print(label)
    print("=" * 66)
    ok = True
    for n, s in sels.items():
        hit = s in code
        if not hit:
            ok = False
        print(f"  {n:34s} 0x{s}  {'FOUND' if hit else '*** MISSING ***'}")
    return ok


def main():
    sd_code = rpc(MAINNET, 'eth_getCode', [SEADROP, 'latest'])['result'][2:]
    print(f"Arc SeaDrop deployed bytecode: {len(sd_code)//2:,} bytes\n")

    a = check(sd_code, SEADROP_SELS,
              "1. SEADROP-SIDE (deployed on Arc mainnet)")
    print()

    # token bytecode is ours, from the compiled artifact
    tk = json.load(open(TK_ABI))
    tk_code = tk['deployedBytecode']['object']
    tk_code = tk_code[2:] if tk_code.startswith('0x') else tk_code
    print(f"Our ERC721SeaDrop compiled bytecode: {len(tk_code)//2:,} bytes\n")
    b = check(tk_code, TOKEN_SELS,
              "2. TOKEN-SIDE (our contract, to be deployed)")

    print()
    print("=" * 66)
    print("3. LIVE CALL: confirm allowlist storage is readable on Arc")
    print("=" * 66)
    probe = '0x32bf11f5' + '0' * 24 + '1' * 40
    r = rpc(MAINNET, 'eth_call', [{'to': SEADROP, 'data': probe}, 'latest'])
    if 'result' in r:
        print(f"  getAllowListMerkleRoot(dummy) = {r['result']}")
        print("  => callable; unconfigured token returns zero root (expected)")
    else:
        print(f"  ERROR {r.get('error')}")

    print()
    print("=" * 66)
    print("4. ABI SANITY: exact function signatures we will encode")
    print("=" * 66)
    tabi = json.load(open(TK_ABI))['abi']
    for want in ('updateAllowList', 'updatePublicDrop',
                 'updateCreatorPayoutAddress', 'updateAllowedFeeRecipient',
                 'setMaxSupply'):
        for e in tabi:
            if e.get('type') == 'function' and e.get('name') == want:
                types = ','.join(
                    (i['type'] if i['type'] != 'tuple'
                     else '(' + ','.join(c['type'] for c in i['components']) + ')')
                    for i in e['inputs'])
                print(f"  {want}({types})")
                break

    print()
    print("=" * 66)
    print("VERDICT")
    print("=" * 66)
    if a and b:
        print("  ALL required functions verified on BOTH sides.")
        print("  Two-phase allowlist + public plan is FEASIBLE.")
    else:
        print("  BLOCKED - see MISSING entries above.")


if __name__ == '__main__':
    main()
