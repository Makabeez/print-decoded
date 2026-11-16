import json, numpy as np, time
from numpy.lib.stride_tricks import sliding_window_view as sw
H=3600_000
MAXLEV={'BTC':50,'ETH':50,'SOL':20,'XRP':20,'HYPE':20,'ENA':10,'ZEC':10,'NEAR':10,'LIT':10,'NVDA':10,'CL':10,'XAU':10,'SKHYNIX':10}
PRINTLEV={'BTC':40,'ETH':25,'SOL':20,'HYPE':20,'XRP':20,'ZEC':10,'LIT':10,'NEAR':10,'ENA':10,'SKHYNIX':10,'CL':10,'XAU':10,'NVDA':10}
LEVS=[1,2,3,5,10,15,20,25,40]
def windows(a,hours):
    r=np.array(json.load(open(f"raw/{a}.json"))); t=r[:,0].astype(np.int64); o,h,l,c=r[:,1],r[:,2],r[:,3],r[:,4]
    n=len(t); idx=np.arange(n-hours+1)
    ok=(t[idx+hours-1]-t[idx])==(hours-1)*H; idx=idx[ok]
    lo=sw(l,hours).min(axis=1)[idx]; hi=sw(h,hours).max(axis=1)[idx]
    return t[idx],o[idx],c[idx+hours-1],lo,hi
def prod(a,hours,dmax):
    t,S0,ST,lo,hi=windows(a,hours); mm=1/(2*MAXLEV[a])
    ds=[round(x,4) for x in np.arange(0.005,dmax+1e-9,0.005)]
    res={'n':int(len(t)),'indep':int(len(t)//hours),'from':int(t[0]),'to':int(t[-1]+hours*H),'d':ds,'long':{},'short':{}}
    for side in ['long','short']:
        cols={k:[] for k in ['touch','fill','mtm','pay','bounce','both']}
        liqT={x:[] for x in LEVS if x<=PRINTLEV[a]}; liqD={x:[] for x in liqT}
        for d in ds:
            if side=='long':
                K=S0*(1-d); touch=lo<=K; fill=ST<=K; m=np.where(fill,(K-ST)/K,0); b=np.where(touch&~fill,(ST-K)/K,0)
            else:
                K=S0*(1+d); touch=hi>=K; fill=ST>=K; m=np.where(fill,(ST-K)/K,0); b=np.where(touch&~fill,(K-ST)/K,0)
            cols['touch'].append(round(float(touch.mean()),4)); cols['fill'].append(round(float(fill.mean()),4))
            cols['mtm'].append(round(float(m[fill].mean()) if fill.any() else 0,5)); cols['pay'].append(round(float(m.mean()),6))
            cols['bounce'].append(round(float(b.mean()),6))
            for x in liqT:
                Q=x/K
                if side=='long': Lt=(K-1/Q)/(1-mm); Ld=K-K/x; lt=ST<=Lt; ld=ST<=Ld
                else: Lt=(K+1/Q)/(1+mm); Ld=K+K/x; lt=ST>=Lt; ld=ST>=Ld
                liqT[x].append(round(float(lt.mean()),5)); liqD[x].append(round(float(ld.mean()),5))
        cols['liqTrue']={str(k):v for k,v in liqT.items()}; cols['liqDocs']={str(k):v for k,v in liqD.items()}
        res[side]=cols
    return res
out={'generated':int(time.time()*1000),'mm':{a:1/(2*m) for a,m in MAXLEV.items()},'maxlev':MAXLEV,'printlev':PRINTLEV,'products':{}}
for a in MAXLEV: out['products'][a+'_24H']=prod(a,24,0.10)
out['products']['BTC_7D']=prod('BTC',168,0.20)
out['products']['BTC_1M']=prod('BTC',720,0.40)
# vol
for a in MAXLEV:
    r=np.array(json.load(open(f"raw/{a}.json"))); c=r[:,4]; ret=np.diff(np.log(c))
    out['products'][a+'_24H']['rv30']=float(ret[-720:].std()*np.sqrt(24*365)); out['products'][a+'_24H']['rvAll']=float(ret.std()*np.sqrt(24*365))
    out['products'][a+'_24H']['last']=float(c[-1])
out['iv']=json.load(open('data/out_iv.json'))
for r in out['iv']:
    for k,v in list(r.items()):
        if hasattr(v,'item'): r[k]=v.item()
s=json.dumps(out,separators=(',',':'))
open('data/dataset.json','w').write(s); print(len(s)/1024,'KB')
# reflection-principle summary
ph=[];
for k,p in out['products'].items():
    for side in ['long','short']:
        for i,d in enumerate(p['d']):
            if d<=0.05 and p[side]['touch'][i]>0.05: ph.append(p[side]['fill'][i]/p[side]['touch'][i])
print('fill/touch mean',np.mean(ph),np.median(ph),np.percentile(ph,[10,90]))
