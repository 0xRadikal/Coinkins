#!/usr/bin/env python3
"""
build_allowlist.py - Compute the merkle root for a SINGLE-ENTRY allowlist.

PROVEN from source (SeaDrop.sol:301):
    leaf = keccak256(abi.encode(minter, mintParams))

PROVEN from OpenZeppelin MerkleProof.processProof:
    with an EMPTY proof, computedHash == leaf
    => therefore root == leaf for a 1-entry tree, and proof = []

MintParams struct field order (SeaDropStructs.sol:87), all uint256 + bool:
    mintPrice, maxTotalMintableByWallet, startTime, endTime,
    dropStageIndex, maxTokenSupplyForStage, feeBps, restrictFeeRecipients

abi.encode (NOT encodePacked) => every field padded to 32 bytes.
Total: address(32) + 8 fields(32 each) = 288 bytes.

Cross-checked against `cast abi-encode` + `cast keccak` independently.
"""
import subprocess
import sys

CAST = '/root/.foundry/bin/cast'
MINTER = '0xa842e3aB069562Db379c35Dd52C77ef214324004'


def keccak_via_cast(hexdata):
    p = subprocess.run([CAST, 'keccak', hexdata],
                       capture_output=True, text=True, timeout=60)
    if p.returncode != 0:
        sys.exit(f"cast keccak failed: {p.stderr}")
    return p.stdout.strip()


def abi_encode_via_cast(sig, *args):
    cmd = [CAST, 'abi-encode', sig] + [str(a) for a in args]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if p.returncode != 0:
        sys.exit(f"cast abi-encode failed: {p.stderr}")
    return p.stdout.strip()


def python_keccak(data: bytes):
    """Independent keccak256 via pysha3/eth_hash if available, else None."""
    try:
        from Crypto.Hash import keccak as _k
        h = _k.new(digest_bits=256)
        h.update(data)
        return '0x' + h.hexdigest()
    except Exception:
        pass
    try:
        import sha3
        return '0x' + sha3.keccak_256(data).hexdigest()
    except Exception:
        return None


def main():
    # ---- PHASE 1 (allowlist) MintParams ----
    # Free mint for our own wallet.
    import time
    now = int(time.time())
    mp = {
        'mintPrice': 0,
        'maxTotalMintableByWallet': 5,
        'startTime': now - 300,
        'endTime': now + 7 * 24 * 3600,
        'dropStageIndex': 1,           # MUST be non-zero per source comment
        'maxTokenSupplyForStage': 1000,
        'feeBps': 0,
        'restrictFeeRecipients': False,
    }

    print("=" * 70)
    print("PHASE 1 ALLOWLIST - MintParams")
    print("=" * 70)
    for k, v in mp.items():
        print(f"  {k:26s} {v}")
    print(f"  minter                     {MINTER}")
    print()

    # abi.encode(address minter, MintParams mintParams)
    # `cast abi-encode` requires a function-style signature (name + params).
    # The name is irrelevant to the encoding - only the parameter types are
    # encoded, and abi-encode omits the 4-byte selector.
    sig = ('leaf(address,(uint256,uint256,uint256,uint256,'
           'uint256,uint256,uint256,bool))')
    tup = (f"({mp['mintPrice']},{mp['maxTotalMintableByWallet']},"
           f"{mp['startTime']},{mp['endTime']},{mp['dropStageIndex']},"
           f"{mp['maxTokenSupplyForStage']},{mp['feeBps']},"
           f"{str(mp['restrictFeeRecipients']).lower()})")

    encoded = abi_encode_via_cast(sig, MINTER, tup)
    nbytes = (len(encoded) - 2) // 2
    print("=" * 70)
    print("ABI ENCODING")
    print("=" * 70)
    print(f"  signature : {sig}")
    print(f"  encoded   : {nbytes} bytes "
          f"(expected 288 = 32 addr + 8*32 fields)")
    print(f"  match     : {nbytes == 288}")
    print(f"  hex       : {encoded[:74]}...")
    print()

    leaf = keccak_via_cast(encoded)
    print("=" * 70)
    print("LEAF / ROOT")
    print("=" * 70)
    print(f"  leaf (cast keccak) = {leaf}")

    pk = python_keccak(bytes.fromhex(encoded[2:]))
    if pk:
        print(f"  leaf (python)      = {pk}")
        print(f"  INDEPENDENT MATCH  : {pk.lower() == leaf.lower()}")
    else:
        print("  (no python keccak lib available; cast is the single source)")

    print()
    print(f"  merkleRoot = leaf  = {leaf}")
    print("  proof      = []    (empty; processProof returns leaf unchanged)")
    print()
    print("=" * 70)
    print("WRITING CONFIG")
    print("=" * 70)
    import json
    cfg = {
        'minter': MINTER,
        'mintParams': mp,
        'mintParamsTuple': tup,
        'abiEncoded': encoded,
        'merkleRoot': leaf,
        'proof': [],
    }
    out = '/webapp/arc-nft/allowlist_phase1.json'
    json.dump(cfg, open(out, 'w'), indent=2)
    print(f"  saved -> {out}")


if __name__ == '__main__':
    main()
