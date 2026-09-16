#!/usr/bin/env python3
"""
Candidate generator with a PLAUSIBILITY FILTER.
v1 produced garbage ("Pennyy","Purseus") because brute-force suffixing
ignores English morphology. v2 rejects implausible strings.
"""
import re, sys
from name_science import score, syllables

def plausible(w):
    l=w.lower()
    if re.search(r'(.)\1\1', l):            return False   # triple letter
    if re.search(r'[aeiouy]{3,}', l):       return False   # 3+ vowels in a row
    if re.search(r'yy|ey e|ii|uu', l):      return False
    if l.endswith('yy') or l.endswith('yi'):return False
    # suffix must not follow a vowel-final root with a vowel-initial suffix
    if re.search(r'[aeiou](us|um|or|on|ex|ix|ia|ian|ard|ant|ent)$', l): return False
    # reject 'y' + consonant-suffix (penny+z, penny+s are ok-ish but penny+ard no)
    if re.search(r'y(ard|ant|ent|ex|ix|ia|ian|er|ers|or|on|um|us)$', l): return False
    if re.search(r'e(us|um|ix|ex|ian|ia|ers|er|ent|or|on|o)$', l): return False
    return True

# Curated morphologically sound candidates: real words, real blends,
# and diminutives that English actually forms.
CANDIDATES = """
Coin Coins Coinage Coiner Coiners Coinkin Coinkins Cointon Coinly
Cent Cents Centing Centry Centa Centro Centex
Copper Coppers Coppery Coppa
Coffer Coffers Cofferz
Cache Caches Cachet
Carat Carats Caratz
Capital Capita Capitol
Credit Credits Creditz
Penny Pennys Pennies Pennykin Pennyton
Pence Pences Pencil
Purse Purses Purser Pursers
Parity Parities
Peg Pegs Pegger Peggers Peggy
Pocket Pockets Pocketz
Keep Keeps Keeper Keepers
Karat Karats
Kopek Kopeks
Token Tokens Tokenz
Tender Tenders Tenderz
Tally Tallys Tallies Tallyman
Tab Tabs Tabby
Tick Ticks Ticker Tickers
Trust Trusts Truster
Till Tills Tiller Tillers
Troy Troys
Bank Banks Banker Bankers
Bond Bonds Bonder Bonders
Bill Bills Billet Billets
Buck Bucks Buckle
Bit Bits Bitkin
Dime Dimes Dimer
Ducat Ducats
Dollar Dollars
Gild Gilds Gilder Gilders Gilded Gildling Gildlings
Gold Golds Golder Goldling Goldlings
Guild Guilds Guilder Guilders Guildling Guildlings
Ledger Ledgers
Mint Mints Minter Minters Mintling Mintlings Minty Mintage
Mark Marks Marker Markka
Note Notes Noter
Par Pars Parr
Vault Vaults Vaulter Vaulters
Bullion Bullions
Specie Species
Denom Denoms
Tithe Tithes Tither
Scrip Scrips Scripling Scriplings
Kite Kites Kiter
Clip Clips Clipper Clippers
Cast Casts Caster Casters
Press Presses Presser Pressers
Punch Punches Puncher Punchers
Die Dies Dieling
Stamp Stamps Stamper Stampers
Proof Proofs Proofer
Blank Blanks Blanker
Flan Flans
Bezel Bezels
Obverse
Reverse
Legend Legends
Relief Reliefs
Pattern Patterns
""".split()

if __name__=="__main__":
    seen=set(); rows=[]
    for c in CANDIDATES:
        if c in seen: continue
        seen.add(c)
        if not plausible(c): continue
        sc,sy,notes=score(c)
        rows.append((sc,sy,c))
    rows.sort(reverse=True)
    top=int(sys.argv[1]) if len(sys.argv)>1 else 40
    print(f"{len(seen)} candidates, {len(rows)} passed plausibility filter")
    print(f"{'name':14}{'score':>7}{'syl':>5}")
    print("-"*28)
    for sc,sy,c in rows[:top]:
        print(f"{c:14}{sc:7.1f}{sy:5}")
