#!/usr/bin/env python3
"""
probe_faucet.py - find the Arc testnet faucet and explorer.
Read-only. No transactions. No funds moved.
"""
import urllib.request
import json

CANDIDATES = [
    # faucet candidates
    "https://faucet.testnet.arc.io",
    "https://faucet.arc.io",
    "https://arc.io/faucet",
    "https://testnet.arc.io",
    "https://testnet.arc.io/faucet",
    # explorer candidates
    "https://explorer.testnet.arc.io",
    "https://explorer.mainnet.arc.io",
    "https://explorer.arc.io",
    "https://arcscan.io",
    "https://scan.arc.io",
    # docs
    "https://docs.arc.io",
    "https://developers.circle.com/arc",
]


def probe(url):
    try:
        req = urllib.request.Request(
            url, headers={'User-Agent': 'Mozilla/5.0'})
        r = urllib.request.urlopen(req, timeout=15)
        body = r.read(4000).decode('utf-8', 'ignore')
        return r.getcode(), len(body), body
    except urllib.error.HTTPError as e:
        return e.code, 0, ''
    except Exception as e:
        return None, 0, str(e)[:60]


def main():
    print("=== ARC FAUCET / EXPLORER PROBE ===")
    hits = []
    for u in CANDIDATES:
        code, n, body = probe(u)
        tag = "??"
        if code == 200:
            tag = "LIVE"
            hits.append(u)
        elif code in (301, 302, 307, 308):
            tag = "REDIR"
        elif code is None:
            tag = "DNS/CONN FAIL"
        else:
            tag = f"HTTP {code}"
        print(f"  {u:44s} {tag}")
        # surface faucet-ish keywords
        if code == 200 and body:
            low = body.lower()
            kws = [k for k in ("faucet", "drip", "claim", "testnet",
                               "explorer", "api", "verify")
                   if k in low]
            if kws:
                print(f"        keywords: {', '.join(kws)}")
    print()
    print(f"LIVE endpoints: {len(hits)}")
    for h in hits:
        print("   ", h)


if __name__ == "__main__":
    main()
