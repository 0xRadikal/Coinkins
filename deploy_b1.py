#!/usr/bin/env python3
"""
deploy_b1.py - B1 TWO-PHASE MAINNET EXECUTION on Arc (chainId 5042).

REAL MONEY. 9 transactions. Stop-on-failure at every step.

Phase 1: allowlist merkle mint, FREE, our wallet only
Phase 2: public mint, PAID 0.1 USDC
Supply:  1000

SAFETY GATES
  1. chainId must be 5042 (mainnet - deliberate)
  2. derived address must equal the audited wallet
  3. hard TOTAL spend cap; abort before exceeding
  4. maxFeePerGas >= 20 gwei protocol floor
  5. balance sufficiency checked before every tx
  6. live gas re-read before every tx (never stale)
  7. abort immediately if receipt status != 0x1

All selectors were derived with `cast sig` from the exact source
signatures and verified present in the deployed bytecode. See doc 13.
"""
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, '/webapp/arc-nft')
from arclib import (rpc, to_int, MAINNET, CHAIN_ID_MAINNET,  # noqa: E402
                    sample_base_fee, priority_fee)

CAST = '/root/.foundry/bin/cast'
KEYFILE = '/root/wallet-test.env'
WALLET = '0xa842e3aB069562Db379c35Dd52C77ef214324004'
SEADROP = '0x00005EA00Ac477B1030CE78506496e8C2dE24bf5'
ART = '/webapp/arc-nft/seadrop/out/ERC721SeaDrop.sol/ERC721SeaDrop.json'
STATE = '/webapp/arc-nft/b1_state.json'

NAME = 'Arc Pathfinder Test'
SYMBOL = 'APFT'
MAX_SUPPLY = 1000
BASE_URI = 'https://arweave.net/apft-placeholder/'

PHASE2_PRICE_WEI = 100_000_000_000_000_000   # 0.1 USDC at 18 decimals

MIN_BASE_FEE_GWEI = 20.0      # protocol floor, documented
HARD_CAP_USD = 1.60           # total gas budget for the whole run
GAS_MULT = 1.5                # maxFee = baseFee_max * mult + tip


def key():
    m = re.search(r'0x[0-9a-fA-F]{64}', open(KEYFILE).read())
    if not m:
        sys.exit('FATAL: no private key')
    return m.group(0)


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {'spent_usd': 0.0, 'txs': [], 'token': None}


def save_state(s):
    json.dump(s, open(STATE, 'w'), indent=2)


def fees():
    """Live fee data. GATE 6 + GATE 4."""
    st = sample_base_fee(MAINNET, n=4, stride=2)
    pf = priority_fee(MAINNET)
    tip = pf['p50'] if pf else 1.0
    max_fee = max(st['max'] * GAS_MULT + tip, MIN_BASE_FEE_GWEI)
    return max_fee, tip, st


def balance():
    return to_int(rpc(MAINNET, 'eth_getBalance', [WALLET, 'latest'])['result'])


def run_cast(args, pk):
    env = dict(os.environ)
    p = subprocess.run([CAST] + args, capture_output=True, text=True,
                       env=env, timeout=300)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def send(label, args_tail, pk, gas_limit, value_wei=0, state=None):
    """
    Send one tx with all gates enforced. args_tail is the cast-send
    argument list AFTER the common flags.
    """
    print(f"\n{'='*66}\n{label}\n{'='*66}")

    max_fee, tip, st = fees()
    est_usd = gas_limit * max_fee / 1e9
    bal = balance()

    print(f"  baseFee max {st['max']:.2f} gwei  tip {tip:.3f} "
          f"-> maxFee {max_fee:.2f} gwei")
    print(f"  gasLimit {gas_limit:,}  worst-case gas ${est_usd:.4f}")
    if value_wei:
        print(f"  value {value_wei/1e18:.6f} USDC")

    # GATE 3: total cap
    if state['spent_usd'] + est_usd > HARD_CAP_USD:
        sys.exit(f"ABORT GATE3: would exceed cap "
                 f"${HARD_CAP_USD} (spent ${state['spent_usd']:.4f})")
    # GATE 5: balance
    need = gas_limit * max_fee / 1e9 + value_wei / 1e18
    if bal / 1e18 < need:
        sys.exit(f"ABORT GATE5: balance {bal/1e18:.6f} < need {need:.6f}")
    # GATE 4 already applied in fees()
    print(f"  GATE3 ok (spent ${state['spent_usd']:.4f})  "
          f"GATE4 ok  GATE5 ok (bal {bal/1e18:.6f})")

    cmd = ['send', '--rpc-url', MAINNET, '--private-key', pk,
           '--gas-limit', str(gas_limit),
           '--priority-gas-price', str(int(tip * 1e9)),
           '--gas-price', str(int(max_fee * 1e9)),
           '--json']
    if value_wei:
        cmd += ['--value', str(value_wei)]
    cmd += args_tail

    rc, out, err = run_cast(cmd, pk)
    if rc != 0:
        print('  STDERR:', err[:700])
        sys.exit(f'ABORT: {label} failed to send')
    try:
        r = json.loads(out)
    except Exception:
        print('  RAW:', out[:700])
        sys.exit(f'ABORT: {label} unparseable output')

    status = r.get('status')
    gas_used = to_int(r.get('gasUsed'))
    eff = to_int(r.get('effectiveGasPrice')) or 0
    actual = gas_used * eff / 1e18

    print(f"  status   {status}")
    print(f"  txHash   {r.get('transactionHash')}")
    print(f"  gasUsed  {gas_used:,}  @ {eff/1e9:.4f} gwei")
    print(f"  cost     ${actual:.6f}")

    # GATE 7
    if status not in ('0x1', 1):
        sys.exit(f"ABORT GATE7: status {status} - reverted")

    state['spent_usd'] += actual
    state['txs'].append({
        'label': label, 'hash': r.get('transactionHash'),
        'gasUsed': gas_used, 'costUsd': actual,
        'contractAddress': r.get('contractAddress'),
    })
    save_state(state)
    return r


def call(to, data):
    r = rpc(MAINNET, 'eth_call', [{'to': to, 'data': data}, 'latest'])
    return r.get('result')


def main():
    print("=" * 66)
    print("B1 TWO-PHASE MAINNET EXECUTION - Arc chainId 5042")
    print("=" * 66)

    # GATE 1
    cid = to_int(rpc(MAINNET, 'eth_chainId')['result'])
    assert cid == CHAIN_ID_MAINNET, f"GATE1 FAIL: chainId {cid}"
    print(f"  GATE1 PASS chainId {cid} (MAINNET - deliberate)")

    pk = key()
    rc, addr, err = run_cast(['wallet', 'address', '--private-key', pk], pk)
    assert rc == 0, f"cast failed: {err}"
    # GATE 2
    assert addr.lower() == WALLET.lower(), f"GATE2 FAIL: {addr}"
    print(f"  GATE2 PASS address {addr}")
    print(f"  balance {balance()/1e18:.6f} USDC")
    print(f"  hard cap ${HARD_CAP_USD}")

    state = load_state()
    if state['txs']:
        print(f"\n  RESUMING: {len(state['txs'])} txs already done, "
              f"spent ${state['spent_usd']:.4f}")

    art = json.load(open(ART))
    init_bin = art['bytecode']['object']
    init_bin = init_bin[2:] if init_bin.startswith('0x') else init_bin

    # ---------- TX1: deploy ----------
    if not state.get('token'):
        ctor = subprocess.run(
            [CAST, 'abi-encode', 'c(string,string,address[])',
             NAME, SYMBOL, f'[{SEADROP}]'],
            capture_output=True, text=True, timeout=60)
        if ctor.returncode != 0:
            sys.exit(f'ctor encode failed: {ctor.stderr}')
        cargs = ctor.stdout.strip()[2:]
        init = '0x' + init_bin + cargs
        print(f"\n  init code {(len(init)-2)//2:,} bytes "
              f"(ctor args {len(cargs)//2} bytes)")

        g = rpc(MAINNET, 'eth_estimateGas', [{'from': WALLET, 'data': init}])
        if 'result' not in g:
            sys.exit(f"estimateGas failed: {g}")
        gl = int(to_int(g['result']) * 1.2)
        r = send('TX1 deploy ERC721SeaDrop', ['--create', init],
                 pk, gl, 0, state)
        token = r.get('contractAddress')
        if not token:
            sys.exit('ABORT: no contract address')
        state['token'] = token
        save_state(state)
        print(f"\n  >>> TOKEN {token}")
    token = state['token']
    print(f"\n  token = {token}")

    # verify deployment
    code = rpc(MAINNET, 'eth_getCode', [token, 'latest']).get('result', '0x')
    print(f"  runtime code {(len(code)-2)//2:,} bytes")
    nm = call(token, '0x06fdde03')   # name()
    sy = call(token, '0x95d89b41')   # symbol()
    print(f"  name()   raw {nm[:10] if nm else None}...")
    print(f"  symbol() raw {sy[:10] if sy else None}...")

    done = {t['label'].split()[0] for t in state['txs']}

    # ---------- TX2: setMaxSupply ----------
    if 'TX2' not in done:
        send('TX2 setMaxSupply(1000)',
             [token, 'setMaxSupply(uint256)', str(MAX_SUPPLY)],
             pk, 80_000, 0, state)
    ms = call(token, '0xd5abeb01')   # maxSupply()
    print(f"\n  maxSupply() = {to_int(ms) if ms else None} (expect {MAX_SUPPLY})")

    # ---------- TX3: setBaseURI ----------
    if 'TX3' not in done:
        send('TX3 setBaseURI', [token, 'setBaseURI(string)', BASE_URI],
             pk, 110_000, 0, state)

    # ---------- TX4: creator payout ----------
    if 'TX4' not in done:
        send('TX4 updateCreatorPayoutAddress',
             [token, 'updateCreatorPayoutAddress(address,address)',
              SEADROP, WALLET], pk, 110_000, 0, state)

    # ---------- TX5: allowed fee recipient ----------
    if 'TX5' not in done:
        send('TX5 updateAllowedFeeRecipient',
             [token, 'updateAllowedFeeRecipient(address,address,bool)',
              SEADROP, WALLET, 'true'], pk, 110_000, 0, state)

    # ---------- TX6: allowlist merkle root ----------
    al = json.load(open('/webapp/arc-nft/allowlist_phase1.json'))
    root = al['merkleRoot']
    if 'TX6' not in done:
        send('TX6 updateAllowList',
             [token, 'updateAllowList(address,(bytes32,string[],string))',
              SEADROP, f'({root},[],"")'], pk, 150_000, 0, state)
    got = call(SEADROP, '0x32bf11f5' + '0'*24 + token[2:].lower())
    print(f"\n  getAllowListMerkleRoot(token) = {got}")
    print(f"  expected                      = {root}")
    print(f"  MATCH: {(got or '').lower() == root.lower()}")

    # ---------- TX7: PHASE 1 free allowlist mint ----------
    mp = al['mintParams']
    mp_tuple = (f"({mp['mintPrice']},{mp['maxTotalMintableByWallet']},"
                f"{mp['startTime']},{mp['endTime']},{mp['dropStageIndex']},"
                f"{mp['maxTokenSupplyForStage']},{mp['feeBps']},"
                f"{str(mp['restrictFeeRecipients']).lower()})")
    if 'TX7' not in done:
        send('TX7 mintAllowList PHASE1 FREE',
             [SEADROP,
              'mintAllowList(address,address,address,uint256,'
              '(uint256,uint256,uint256,uint256,uint256,uint256,uint256,bool),'
              'bytes32[])',
              token, WALLET, '0x0000000000000000000000000000000000000000',
              '1', mp_tuple, '[]'],
             pk, 300_000, 0, state)
    bo = call(token, '0x70a08231' + '0'*24 + WALLET[2:].lower())
    ts = call(token, '0x18160ddd')
    print(f"\n  balanceOf(us) = {to_int(bo) if bo else None}")
    print(f"  totalSupply() = {to_int(ts) if ts else None}")

    # ---------- TX8: PHASE 2 public drop config ----------
    now = int(time.time())
    p2_start = now + 30
    p2_end = now + 7 * 24 * 3600
    if 'TX8' not in done:
        pd = (f"({PHASE2_PRICE_WEI},{p2_start},{p2_end},5,0,false)")
        send('TX8 updatePublicDrop PHASE2 0.1 USDC',
             [token,
              'updatePublicDrop(address,(uint80,uint48,uint48,uint16,uint16,bool))',
              SEADROP, pd], pk, 150_000, 0, state)
        state['p2_start'] = p2_start
        save_state(state)
    gp = call(SEADROP, '0xbc6a629c' + '0'*24 + token[2:].lower())
    print(f"\n  getPublicDrop(token) = {gp}")

    # wait for phase 2 to open
    p2s = state.get('p2_start', p2_start)
    wait = p2s - int(time.time()) + 3
    if wait > 0:
        print(f"\n  waiting {wait}s for PHASE 2 to open...")
        time.sleep(wait)

    # ---------- TX9: PHASE 2 paid public mint ----------
    if 'TX9' not in done:
        send('TX9 mintPublic PHASE2 PAID 0.1 USDC',
             [SEADROP, 'mintPublic(address,address,address,uint256)',
              token, WALLET,
              '0x0000000000000000000000000000000000000000', '1'],
             pk, 300_000, PHASE2_PRICE_WEI, state)

    # ---------- FINAL ----------
    bo = call(token, '0x70a08231' + '0'*24 + WALLET[2:].lower())
    ts = call(token, '0x18160ddd')
    print("\n" + "=" * 66)
    print("FINAL STATE")
    print("=" * 66)
    print(f"  token         {token}")
    print(f"  balanceOf(us) {to_int(bo) if bo else None}")
    print(f"  totalSupply   {to_int(ts) if ts else None}")
    print(f"  maxSupply     {MAX_SUPPLY}")
    print(f"  gas spent     ${state['spent_usd']:.6f}")
    print(f"  balance left  {balance()/1e18:.6f} USDC")
    print(f"  txs           {len(state['txs'])}")
    for t in state['txs']:
        print(f"    {t['label'][:34]:36s} {t['hash'][:20]}... "
              f"${t['costUsd']:.6f}")


if __name__ == '__main__':
    main()
