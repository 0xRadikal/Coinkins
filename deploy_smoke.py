#!/usr/bin/env python3
"""
deploy_smoke.py - FIRST REAL TRANSACTION on Arc testnet.

Deploys SmokeTest.sol to Arc TESTNET to prove the full signing +
broadcast + receipt pipeline works, BEFORE investing in the SeaDrop build.

Safety:
  - TESTNET ONLY. Hard-asserts chainId == 5042002. Refuses mainnet.
  - Reads gas live (never hardcoded).
  - Caps spend; aborts if cost exceeds the cap.
  - Never prints the private key.

Uses `cast` (Foundry v1.8.1, already installed) for signing so we do not
need to install web3.py / eth-account on a 96%-full disk.
"""
import subprocess
import sys
import json
import os

sys.path.insert(0, '/webapp/arc-nft')
from arclib import rpc, to_int, TESTNET, CHAIN_ID_TESTNET, sample_base_fee, priority_fee  # noqa: E402

CAST = "/root/.foundry/bin/cast"
KEYFILE = "/root/wallet-test.env"
BIN = "/webapp/arc-nft/contracts/out/SmokeTest.bin"
EXPECTED_ADDR = "0xa842e3aB069562Db379c35Dd52C77ef214324004"

# Abort if a single tx would cost more than this many native units.
MAX_SPEND_NATIVE = 1.0


def read_key():
    """Read key from file. Returned value is never printed."""
    import re
    txt = open(KEYFILE).read()
    m = re.search(r'0x[0-9a-fA-F]{64}', txt)
    if not m:
        sys.exit("FATAL: no 64-hex private key found in " + KEYFILE)
    return m.group(0)


def run(cmd, key=None):
    """Run cast. Key passed via env, never argv, so it cannot leak to ps."""
    env = dict(os.environ)
    if key:
        env["CAST_PRIVATE_KEY"] = key
    p = subprocess.run(cmd, capture_output=True, text=True, env=env,
                       timeout=180)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def main():
    # ---- SAFETY GATE 1: must be testnet ----
    cid = to_int(rpc(TESTNET, "eth_chainId")["result"])
    print(f"chainId = {cid}")
    assert cid == CHAIN_ID_TESTNET, f"ABORT: expected testnet {CHAIN_ID_TESTNET}, got {cid}"
    print("  SAFETY GATE 1 PASS: this is Arc TESTNET\n")

    key = read_key()

    # ---- SAFETY GATE 2: address must match the audited wallet ----
    rc, addr, err = run([CAST, "wallet", "address", "--private-key", key])
    if rc != 0:
        sys.exit(f"FATAL: cast wallet address failed: {err}")
    print(f"derived address = {addr}")
    assert addr.lower() == EXPECTED_ADDR.lower(), \
        f"ABORT: address mismatch. audited {EXPECTED_ADDR}, got {addr}"
    print("  SAFETY GATE 2 PASS: matches the wallet audited as zero-mainnet-value\n")

    # ---- balance ----
    bal = to_int(rpc(TESTNET, "eth_getBalance", [addr, "latest"])["result"])
    print(f"balance = {bal / 1e18:.18f} native")
    if bal == 0:
        sys.exit("FATAL: zero testnet balance; fund at faucet.circle.com")

    # ---- live gas ----
    init = open(BIN).read().strip()
    if init.startswith("0x"):
        init = init[2:]
    init = "0x" + init + hex(42)[2:].rjust(64, '0')

    g = rpc(TESTNET, "eth_estimateGas", [{"from": addr, "data": init}])
    if "result" not in g:
        sys.exit(f"FATAL: estimateGas failed: {g}")
    gas = to_int(g["result"])
    gas_limit = int(gas * 1.25)  # headroom

    st = sample_base_fee(TESTNET, n=5, stride=3)
    pf = priority_fee(TESTNET)
    tip = pf["p50"] if pf else 1.0
    max_fee = st["median"] * 2.0 + tip

    cost = gas_limit * max_fee / 1e9
    print(f"gas estimate = {gas:,}  limit = {gas_limit:,}")
    print(f"baseFee median = {st['median']:.2f} gwei  tip p50 = {tip:.3f} gwei")
    print(f"maxFeePerGas = {max_fee:.2f} gwei")
    print(f"worst-case cost = {cost:.8f} native")

    # ---- SAFETY GATE 3: spend cap ----
    assert cost <= MAX_SPEND_NATIVE, \
        f"ABORT: cost {cost} exceeds cap {MAX_SPEND_NATIVE}"
    print(f"  SAFETY GATE 3 PASS: cost within cap {MAX_SPEND_NATIVE}\n")

    # ---- broadcast ----
    print("broadcasting deploy to Arc TESTNET ...")
    # NOTE: `--create` consumes the remaining args, so it MUST come last.
    # Verified via `cast send --help` (Foundry v1.8.1).
    cmd = [
        CAST, "send", "--rpc-url", TESTNET,
        "--private-key", key,
        "--gas-limit", str(gas_limit),
        "--priority-gas-price", str(int(tip * 1e9)),
        "--json",
        "--create", init,
    ]
    rc, out, err = run(cmd)
    if rc != 0:
        print("STDERR:", err[:900])
        sys.exit("FATAL: deploy failed")

    try:
        r = json.loads(out)
    except Exception:
        print("raw:", out[:900])
        sys.exit("FATAL: could not parse cast output")

    print()
    print("=" * 62)
    print(f"  status           {r.get('status')}")
    print(f"  txHash           {r.get('transactionHash')}")
    print(f"  contractAddress  {r.get('contractAddress')}")
    print(f"  blockNumber      {to_int(r.get('blockNumber'))}")
    print(f"  gasUsed          {to_int(r.get('gasUsed')):,}")
    eff = to_int(r.get('effectiveGasPrice'))
    if eff:
        print(f"  effectiveGasPrice {eff / 1e9:.4f} gwei")
        print(f"  actual cost      {to_int(r.get('gasUsed')) * eff / 1e18:.10f} native")
    print("=" * 62)

    # ---- POST-VERIFY: read the contract back ----
    ca = r.get("contractAddress")
    if ca:
        sz = rpc(TESTNET, "eth_getCode", [ca, "latest"])
        code = sz.get("result", "0x")
        print(f"\ndeployed runtime code: {(len(code) - 2) // 2} bytes")
        # value() selector 0x3fa4f245 -> must return 42
        v = rpc(TESTNET, "eth_call", [{"to": ca, "data": "0x3fa4f245"}, "latest"])
        if "result" in v:
            got = to_int(v["result"])
            print(f"value() = {got}  (expected 42)  "
                  f"{'PASS' if got == 42 else 'FAIL'}")
        # owner() selector 0x8da5cb5b -> must be our address
        o = rpc(TESTNET, "eth_call", [{"to": ca, "data": "0x8da5cb5b"}, "latest"])
        if "result" in o:
            own = "0x" + o["result"][-40:]
            print(f"owner() = {own}")
            print(f"  matches deployer: "
                  f"{'PASS' if own.lower() == addr.lower() else 'FAIL'}")


if __name__ == "__main__":
    main()
