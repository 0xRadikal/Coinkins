#!/usr/bin/env python3
"""
probe_evm.py - prove which EVM opcodes Arc supports.
Read-only eth_call against deployed-code-free execution.
No guessing: each test returns a DISTINCT value so support is unambiguous.

Method: eth_call with `to: null` executes the `data` as init code
(a constructor). We craft init code that RETURNS a value computed by the
opcode under test. If the opcode is unsupported the call reverts / returns
empty; if supported we get the exact expected bytes back.
"""
import sys
sys.path.insert(0, '/webapp/arc-nft')
from arclib import rpc, MAINNET, TESTNET  # noqa: E402


def run(url, data):
    d = rpc(url, "eth_call", [{"to": None, "data": data}, "latest"], tries=2)
    if "_err" in d:
        return ("TRANSPORT", d["_err"])
    if "error" in d:
        return ("REVERT", str(d["error"].get("message"))[:50])
    return ("OK", d.get("result"))


# Each program: push 32-byte value to memory, return it.
# Return 32 bytes from offset 0:  RETURN(0, 32) = 6020 6000 f3
RET32 = "602060 00f3".replace(" ", "")

TESTS = {
    # PUSH0 (0x5f, Shanghai). Program: PUSH0; PUSH0; MSTORE -> mem[0]=0
    # then return 32 bytes. If PUSH0 missing -> invalid opcode revert.
    "PUSH0 (0x5f, Shanghai)":
        "0x" + "5f" + "5f" + "52" + RET32,

    # Baseline sanity: PUSH1 0x2a; PUSH1 0; MSTORE; RETURN(0,32) -> 42
    "PUSH1 baseline (always valid)":
        "0x" + "602a" + "6000" + "52" + RET32,

    # MCOPY (0x5e, Cancun): store 42, mcopy 32 bytes 0->32, return mem[32]
    # PUSH1 2a PUSH1 00 MSTORE  PUSH1 20 PUSH1 00 PUSH1 20 MCOPY
    # then RETURN(32,32)
    "MCOPY (0x5e, Cancun)":
        "0x" + "602a600052" + "6020" + "6000" + "6020" + "5e"
        + "6020" + "6020" + "f3",

    # BASEFEE (0x48, London): return current basefee
    "BASEFEE (0x48, London)":
        "0x" + "48" + "6000" + "52" + RET32,

    # CHAINID (0x46, Istanbul): return chainid
    "CHAINID (0x46, Istanbul)":
        "0x" + "46" + "6000" + "52" + RET32,

    # TLOAD (0x5c, Cancun transient storage): tload slot0 -> return
    "TLOAD (0x5c, Cancun)":
        "0x" + "6000" + "5c" + "6000" + "52" + RET32,
}


def main():
    for label, url in (("MAINNET", MAINNET), ("TESTNET", TESTNET)):
        print("=" * 70)
        print(f"{label}  {url}")
        for name, data in TESTS.items():
            status, val = run(url, data)
            if status == "OK" and val and val != "0x":
                n = int(val, 16)
                print(f"  {name:32s} SUPPORTED  -> {n}")
            elif status == "OK":
                print(f"  {name:32s} empty return (inconclusive)")
            else:
                print(f"  {name:32s} {status}: {val}")
        print()


if __name__ == "__main__":
    main()
