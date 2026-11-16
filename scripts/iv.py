import json, numpy as np, time
from math import log, sqrt, exp, erf
def N(x): return 0.5*(1+erf(x/sqrt(2)))
def put(S,K,s,T):
    if s<=0: return max(K-S,0)
    d1=(log(S/K)+0.5*s*s*T)/(s*sqrt(T)); d2=d1-s*sqrt(T); return K*N(-d2)-S*N(-d1)
def call(S,K,s,T): return put(S,K,s,T)+S-K
MAXLEV={'BTC':50,'ZEC':10,'HYPE':20}
orders=[ # asset, dir(0 long,1 short), K, S0, lev, D, P, ts, outcome
 ('BTC',0,78703,81077,10,1094.99,3.279068,1792335413444,'user-ended'),
 ('ZEC',0,1233.35,1252.106789,5,1556.22,50.059381,1791445197610,'filled'),
 ('ZEC',1,1150.95,1088.977266,10,922.93,23.797135,1792070878664,'liquidated'),
 ('ZEC',1,1285.05,1220.124,5,2452.35,26.080065,1792160520605,'user-ended'),
 ('HYPE',1,73.4,71.629929,20,20.19,2.127622,1787233005945,'ended'),
]
def model_value(a,dr,K,S,lev,D,P,s,T):
    Nn=D*lev; Q=Nn/K; M=D+P; mm=1/(2*MAXLEV[a])
    if dr==0:
        L=(K-M/Q)/(1-mm)
        # loss = Q(K-S_T) for S_T>L ; M for S_T<L  ≈ Q*[put(K)-put(L)] + extra
        return Q*(put(S,K,s,T)-put(S,L,s,T)) + (M - Q*(K-L))*0  # approx spread
    else:
        L=(K+M/Q)/(1+mm)
        return Q*(call(S,K,s,T)-call(S,L,s,T))
def solve(a,dr,K,S,lev,D,P,T):
    lo,hi=0.01,5.0
    for _ in range(100):
        m=(lo+hi)/2
        if model_value(a,dr,K,S,lev,D,P,m,T)<P: lo=m
        else: hi=m
    return m
def rv(a,ts,hours):
    r=np.array(json.load(open(f"raw/{a}.json"))); t=r[:,0]
    i=np.searchsorted(t,ts)-1
    c=r[max(0,i-hours):i+1,4]; ret=np.diff(np.log(c))
    return ret.std()*sqrt(24*365)
def fwd(a,ts,hours):
    r=np.array(json.load(open(f"raw/{a}.json"))); t=r[:,0]
    i=np.searchsorted(t,ts)
    c=r[i:i+hours+1,4]; ret=np.diff(np.log(c)); return ret.std()*sqrt(24*365), c[-1]
out=[]
for a,dr,K,S,lev,D,P,ts,oc in orders:
    T=1/365; iv=solve(a,dr,K,S,lev,D,P,T)
    r1=rv(a,ts,24); r7=rv(a,ts,168); r30=rv(a,ts,720); fv,ST=fwd(a,ts,24)
    fair7=model_value(a,dr,K,S,lev,D,P,r7,T)
    d=abs(K/S-1)
    row=dict(asset=a,side='long' if dr==0 else 'short',dist=d,lev=lev,deposit=D,premium=P,prem_bp_notional=P/(D*lev)*1e4,
      apy_on_deposit=P/D*365, iv=iv, rv24=r1, rv7=r7, rv30=r30, fwd_rv24=fv, fair_at_rv7=fair7, ratio=P/fair7, date=time.strftime('%Y-%m-%d %H:%M',time.gmtime(ts/1000)), outcome=oc, ST=ST)
    out.append(row)
    print({k:(round(v,4) if isinstance(v,float) else v) for k,v in row.items()})
json.dump(out,open('data/out_iv.json','w'))
