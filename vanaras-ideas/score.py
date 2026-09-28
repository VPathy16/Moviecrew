import re, glob, os, csv
rows=[]
for f in sorted(glob.glob(os.path.join(os.path.dirname(__file__),'ideas','idea_*.md'))):
    t=open(f).read()
    n=int(re.search(r'idea_(\d+)',f).group(1))
    title=t.splitlines()[0].lstrip('# ').strip()
    lens=(re.search(r'^Lens:\s*(.*)$',t,re.M) or [None,''])[1] if re.search(r'^Lens:',t,re.M) else ''
    def s(k):
        m=re.search(k+r'\s*:\s*(\d+)',t); return int(m.group(1)) if m else 0
    sc=dict(market=s('market_size'),defens=s('defensibility'),feas=s('feasibility_solo_30k'),fit=s('asset_fit'),excite=s('excitement'))
    total=sc['market']+sc['defens']+sc['feas']+sc['fit']+sc['excite']
    rows.append(dict(n=n,title=title,lens=lens,**sc,total=total))
rows.sort(key=lambda r:-r['total'])
with open(os.path.join(os.path.dirname(__file__),'scores.csv'),'w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for r in rows: print(f"{r['total']:2} m{r['market']} d{r['defens']} f{r['feas']} a{r['fit']} e{r['excite']} | {r['n']:03} {r['title'][:95]}")
print(len(rows))
