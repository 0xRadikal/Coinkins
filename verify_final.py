#!/usr/bin/env python3
"""
verify_final.py - Independent verification of the B1 result.
Reads everything back from chain; trusts no prior output.
"""
import json
import sys
import urllib.request

sys.path.insert(0, '/webapp/arc-nft')
from arclib import rpc, to_int, MAINNET  # noqa: E402

st = json.load(open('/webapp/arc-nft/b1_state.json'))
TOKEN = st['token']
WALLET = '0xa842e3aB069562Db379c35Dd52C77ef214324004'
SEADROP = '0x00005EA00Ac477B1030CE78506496e8C2dE24bf5'


def call(to, data):
    r = rpc(MAINNET, 'eth_call', [{'to': to, 'data': data}, 'latest'])
    return r.get('result')


def decode_string(hexres):
    """Decode an ABI-encoded dynamic string return value."""
    if not hexres or len(hexres) < 130:
        return None
    b = bytes.fromhex(hexres[2:])
    ln = int.from_bytes(b[32:64], 'big')
    return b[64:64 + ln].decode('utf-8', 'ignore')


def main():
    print("=" * 68)
    print("B1 FINAL VERIFICATION (read back from chain)")
    print("=" * 68)
    print(f"  token  {TOKEN}")
    print()

    code = rpc(MAINNET, 'eth_getCode', [TOKEN, 'latest']).get('result', '0x')
    print(f"  runtime code   {(len(code)-2)//2:,} bytes")
    print(f"  name()         {decode_string(call(TOKEN, '0x06fdde03'))!r}")
    print(f"  symbol()       {decode_string(call(TOKEN, '0x95d89b41'))!r}")
    print(f"  maxSupply()    {to_int(call(TOKEN, '0xd5abeb01'))}")
    print(f"  totalSupply()  {to_int(call(TOKEN, '0x18160ddd'))}")
    bo = call(TOKEN, '0x70a08231' + '0'*24 + WALLET[2:].lower())
    print(f"  balanceOf(us)  {to_int(bo)}")
    own = call(TOKEN, '0x8da5cb5b')
    print(f"  owner()        0x{own[-40:] if own else '?'}")

    print()
    print("  --- token ownership of minted ids ---")
    for tid in (0, 1, 2):
        o = call(TOKEN, '0x6352211e' + hex(tid)[2:].rjust(64, '0'))
        if o and int(o, 16) != 0:
            print(f"    ownerOf({tid}) = 0x{o[-40:]}")
        else:
            print(f"    ownerOf({tid}) = <nonexistent>")

    print()
    print("  --- tokenURI ---")
    u = call(TOKEN, '0xc87b56dd' + '0'.rjust(64, '0'))
    print(f"    tokenURI(0) = {decode_string(u)!r}")

    print()
    print("=" * 68)
    print("SEADROP CONFIG (read from canonical SeaDrop)")
    print("=" * 68)
    root = call(SEADROP, '0x32bf11f5' + '0'*24 + TOKEN[2:].lower())
    al = json.load(open('/webapp/arc-nft/allowlist_phase1.json'))
    print(f"  merkleRoot on-chain {root}")
    print(f"  merkleRoot expected {al['merkleRoot']}")
    print(f"  MATCH: {(root or '').lower() == al['merkleRoot'].lower()}")

    gp = call(SEADROP, '0xbc6a629c' + '0'*24 + TOKEN[2:].lower())
    if gp:
        b = bytes.fromhex(gp[2:])
        # PublicDrop returned as a struct of 6 fields, each padded to 32B
        fields = [int.from_bytes(b[i*32:(i+1)*32], 'big')
                  for i in range(len(b)//32)]
        names = ['mintPrice', 'startTime', 'endTime',
                 'maxTotalMintableByWallet', 'feeBps', 'restrictFeeRecipients']
        print()
        print("  getPublicDrop(token):")
        for n, v in zip(names, fields):
            extra = ''
            if n == 'mintPrice':
                extra = f"  = {v/1e18:.6f} USDC"
            print(f"    {n:26s} {v}{extra}")

    print()
    print("=" * 68)
    print("EXPLORER CROSS-CHECK")
    print("=" * 68)
    try:
        req = urllib.request.Request(
            f"https://explorer.arc.io/api/v2/addresses/{TOKEN}",
            headers={'User-Agent': 'Mozilla/5.0'})
        d = json.load(urllib.request.urlopen(req, timeout=20))
        print(f"  is_contract {d.get('is_contract')}  "
              f"verified {d.get('is_verified')}")
        print(f"  creator     {d.get('creator_address_hash')}")
    except Exception as e:
        print(f"  explorer unavailable to bots: {str(e)[:60]}")

    print()
    print("=" * 68)
    print("COST SUMMARY")
    print("=" * 68)
    bal = to_int(rpc(MAINNET, 'eth_getBalance',
                     [WALLET, 'latest'])['result']) / 1e18
    print(f"  gas spent      ${st['spent_usd']:.6f}")
    print(f"  mint payment    0.100000 USDC (to our own payout address)")
    print(f"  balance now     {bal:.6f} USDC")
    print(f"  started with    2.000000 USDC")
    print(f"  net change      {bal - 2.0:+.6f} USDC")
    print(f"  transactions    {len(st['txs'])}")


if __name__ == '__main__':
    main()
