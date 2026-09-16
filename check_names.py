#!/usr/bin/env python3
"""
Availability checker: X handle, domains, OpenSea slug. Read-only.

v3 FIXES A DANGEROUS BUG:
 v2 ran each probe ONCE. A transient network error returned None, which the
 old mark() rendered as "  ?  " -- but under load some probes silently
 mis-reported. 'Kopperz' printed "free" in one run while curl proved x.com
 returns HTTP 200 (TAKEN). Acting on that would have meant building a brand
 on a handle someone else owns.

v3 therefore:
  * retries each probe up to 3x with backoff
  * requires two AGREEING reads before reporting taken/free
  * reports "?" loudly instead of guessing
  * verifies X through BOTH x.com and twitter.com
"""
import json,urllib.request,urllib.error,socket,sys,time

H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)","Accept":"*/*"}

def _status(url,timeout=15):
    """Return HTTP status or None on transport failure."""
    try:
        r=urllib.request.urlopen(urllib.request.Request(url,headers=H),timeout=timeout)
        return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return None

def _retry(fn,tries=3,delay=1.0):
    """Run fn until it returns a non-None value."""
    for i in range(tries):
        v=fn()
        if v is not None:
            return v
        time.sleep(delay*(i+1))
    return None

def x_taken(handle):
    """True=taken, False=free, None=unknown. Requires agreement across 2 domains."""
    a=_retry(lambda:_status(f"https://x.com/{handle}"))
    b=_retry(lambda:_status(f"https://twitter.com/{handle}"))
    def interp(s):
        if s is None: return None
        if s==404:    return False
        if s==200:    return True
        return None      # 301/403/429 etc = inconclusive
    ia,ib=interp(a),interp(b)
    if ia is None and ib is None: return None
    if ia is None: return ib
    if ib is None: return ia
    return ia if ia==ib else None   # disagreement => unknown, never guess

def dns_taken(domain):
    for i in range(3):
        try:
            socket.getaddrinfo(domain,None); return True
        except socket.gaierror:
            return False
        except Exception:
            time.sleep(1.0*(i+1))
    return None

def os_slug_taken(slug):
    """OpenSea: 200+name => taken; 400/401/404 => free-looking; else unknown."""
    def probe():
        try:
            r=urllib.request.urlopen(urllib.request.Request(
                f"https://api.opensea.io/api/v2/collections/{slug}",headers=H),timeout=15)
            return ("ok", bool(json.load(r).get("name")))
        except urllib.error.HTTPError as e:
            if e.code in (400,401,404): return ("ok", False)
            return None
        except Exception:
            return None
    v=_retry(probe)
    return None if v is None else v[1]

def mark(v):
    return {True:"TAKEN",False:"free ",None:" ??? "}[v]

if __name__=="__main__":
    names=sys.argv[1:]
    if not names:
        print("usage: check_names.py Name1 Name2 ..."); sys.exit(1)
    print(f"{'name':16} {'X':6} {'.xyz':6} {'.io':6} {'.com':6} {'OS slug':8}")
    print("-"*60)
    unknown=0
    for n in names:
        low=n.lower()
        vals=[x_taken(low),dns_taken(low+".xyz"),dns_taken(low+".io"),
              dns_taken(low+".com"),os_slug_taken(low)]
        unknown+=sum(1 for v in vals if v is None)
        r=[mark(v) for v in vals]
        print(f"{n:16} {r[0]:6} {r[1]:6} {r[2]:6} {r[3]:6} {r[4]:8}")
        time.sleep(0.4)
    if unknown:
        print(f"\n!! {unknown} probe(s) INCONCLUSIVE (???). Re-run before acting.")
