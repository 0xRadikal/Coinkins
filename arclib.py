#!/usr/bin/env python3
"""
arclib.py - Arc chain JSON-RPC toolkit.

Written as a FILE (not a bash heredoc) because large heredocs were the
root cause of the Bash tool failures. Diagnosis:
  - `echo OK1`                  -> worked
  - small heredoc (2 lines)     -> worked
  - large heredoc (40+ lines)   -> failed
So all non-trivial logic lives in files from now on.

No hardcoded gas. No guessed values. Every number is read live.
"""
import json
import urllib.request
import time
import statistics

MAINNET = "https://rpc.mainnet.arc.io"
TESTNET = "https://rpc.testnet.arc.io"
TESTNET_ALT = "https://rpc.drpc.testnet.arc.io"

CHAIN_ID_MAINNET = 5042
CHAIN_ID_TESTNET = 5042002


class RpcError(Exception):
    pass


def rpc(url, method, params=None, tries=3, timeout=20):
    """JSON-RPC call with retry. Returns dict. Never silently returns bad data."""
    body = json.dumps({
        "jsonrpc": "2.0", "id": 1,
        "method": method, "params": params or []
    }).encode()
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(
                url, data=body,
                headers={'Content-Type': 'application/json',
                         'User-Agent': 'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(req, timeout=timeout))
        except Exception as e:
            last = str(e)[:80]
            time.sleep(1.2 * (i + 1))
    return {"_err": last}


def rpc_result(url, method, params=None, tries=3):
    """Return the .result or raise. Use when a missing result is fatal."""
    d = rpc(url, method, params, tries)
    if "_err" in d:
        raise RpcError(f"{method}: transport: {d['_err']}")
    if "error" in d:
        raise RpcError(f"{method}: rpc error: {d['error']}")
    if "result" not in d:
        raise RpcError(f"{method}: no result field: {d}")
    return d["result"]


def to_int(h):
    """Hex-quantity -> int. Tolerates ints already decoded."""
    if isinstance(h, int):
        return h
    if h is None:
        return None
    return int(h, 16)


def code_size(url, addr):
    """Bytecode size in bytes. -1 means the query itself failed."""
    d = rpc(url, "eth_getCode", [addr, "latest"])
    if "_err" in d or "result" not in d:
        return -1
    return (len(d["result"]) - 2) // 2


def chain_id(url):
    return to_int(rpc_result(url, "eth_chainId"))


def block_number(url):
    return to_int(rpc_result(url, "eth_blockNumber"))


def base_fee(url):
    """Current baseFeePerGas in wei. None if chain is pre-EIP1559."""
    b = rpc_result(url, "eth_getBlockByNumber", ["latest", False])
    return to_int(b.get("baseFeePerGas")) if b else None


def sample_base_fee(url, n=12, stride=10):
    """
    Sample baseFee across n blocks. Returns dict of stats in GWEI.
    Used instead of any hardcoded gas figure.
    """
    head = block_number(url)
    fees = []
    for i in range(n):
        b = rpc(url, "eth_getBlockByNumber", [hex(head - i * stride), False])
        r = b.get("result")
        if r and r.get("baseFeePerGas"):
            fees.append(to_int(r["baseFeePerGas"]) / 1e9)
        time.sleep(0.15)
    if not fees:
        return None
    return {
        "n": len(fees),
        "min": min(fees),
        "max": max(fees),
        "median": statistics.median(fees),
        "mean": statistics.mean(fees),
        "spread": max(fees) / min(fees) if min(fees) else None,
    }


def priority_fee(url, blocks=10):
    """
    Priority fee percentiles in GWEI from eth_feeHistory.
    NOTE: eth_maxPriorityFeePerGas returns 0 on Arc (measured) and MUST NOT
    be trusted - using it would produce a stuck transaction.
    """
    d = rpc(url, "eth_feeHistory", [blocks, "latest", [10, 50, 90]])
    if "_err" in d or "result" not in d:
        return None
    rw = d["result"].get("reward") or []
    if not rw:
        return None
    return {
        "p10": statistics.median([to_int(x[0]) / 1e9 for x in rw]),
        "p50": statistics.median([to_int(x[1]) / 1e9 for x in rw]),
        "p90": statistics.median([to_int(x[2]) / 1e9 for x in rw]),
    }


def health(url):
    """One-shot connectivity + identity check for an endpoint."""
    out = {"url": url}
    try:
        out["chainId"] = chain_id(url)
        out["block"] = block_number(url)
        bf = base_fee(url)
        out["baseFeeGwei"] = round(bf / 1e9, 2) if bf else None
        out["ok"] = True
    except RpcError as e:
        out["ok"] = False
        out["err"] = str(e)
    return out


if __name__ == "__main__":
    print("=== ARC RPC HEALTH ===")
    for u in (MAINNET, TESTNET, TESTNET_ALT):
        h = health(u)
        if h.get("ok"):
            print(f"  OK   {u}")
            print(f"       chainId={h['chainId']} block={h['block']} "
                  f"baseFee={h['baseFeeGwei']} gwei")
        else:
            print(f"  FAIL {u}  {h.get('err')}")
    print()
    print("=== SELF-TEST: to_int ===")
    assert to_int("0x13b2") == 5042, "to_int broken"
    assert to_int("0x0") == 0
    assert to_int(5042) == 5042
    print("  to_int OK")
    print("=== SELF-TEST: chainId matches constants ===")
    assert chain_id(MAINNET) == CHAIN_ID_MAINNET, "mainnet chainId mismatch"
    assert chain_id(TESTNET) == CHAIN_ID_TESTNET, "testnet chainId mismatch"
    print(f"  mainnet={CHAIN_ID_MAINNET} testnet={CHAIN_ID_TESTNET} OK")
