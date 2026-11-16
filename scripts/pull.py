import json, time, urllib.request, sys, os
os.makedirs("raw", exist_ok=True)
assets = ["BTC","ETH","SOL","HYPE","ZEC","XRP","LIT","NEAR","ENA","SKHYNIX","CL","XAU","NVDA"]
H=3600_000
now = int(time.time()*1000)//H*H
for a in assets:
    rows={}
    end=now
    for k in range(4):  # up to ~16000h ≈ 1.8y
        start=end-3990*H
        url=f"https://api.pacifica.fi/api/v1/kline/mark?symbol={a}&interval=1h&start_time={start}&end_time={end}"
        try:
            d=json.load(urllib.request.urlopen(url,timeout=30))
        except Exception as e:
            print(a,"err",e); break
        x=d.get("data") or []
        for r in x: rows[r["t"]]=r
        if len(x)<100: break
        end=start
        time.sleep(0.3)
    rs=sorted(rows.values(), key=lambda r:r["t"])
    json.dump([[r["t"],float(r["o"]),float(r["h"]),float(r["l"]),float(r["c"])] for r in rs], open(f"raw/{a}.json","w"))
    if rs: print(a, len(rs), time.strftime('%Y-%m-%d',time.gmtime(rs[0]["t"]/1000)), time.strftime('%Y-%m-%d %H',time.gmtime(rs[-1]["t"]/1000)))
