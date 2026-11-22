import re,sys
t=open(sys.argv[1]).read()
banned=["neon","shadow","midnight","dark","static","echo","fade"]
songs=re.split(r'\n## \d\. ',t)[1:]
bpm={'Small':92,'Measure':90,'Spare':72,'Private':90,'Last':116,'Second':110,'Monaco':108,'Window':82,'Hold':72}
for s in songs:
    name=s.split('\n')[0]
    bars=[int(x) for x in re.findall(r'^\| [^|*]+\| (\d+) \|',s,re.M)]
    b=[v for k,v in bpm.items() if k in name][0]
    secs=sum(bars)*240/b
    lyr=re.findall(r'```\n(\[Intro.*?)```',s,re.S)[0]
    secs_l={}
    cur=None
    for line in lyr.split('\n'):
        m=re.match(r'\[([A-Za-z\- ]+?\d?)[:\]]',line)
        if m: cur=m.group(1).strip(); secs_l.setdefault(cur,[]); continue
        if line.strip() and cur: secs_l[cur].append(line.strip())
    issues=[]
    for v in ['Verse 1','Verse 2']:
        L=secs_l[v]; w=[len(x.split()) for x in L]
        if len(L)!=6 or min(w)<5 or max(w)>7: issues.append(f'{v} {w}')
    w=[len(x.split()) for x in secs_l['Bridge']]
    if len(w)!=4 or min(w)<4 or max(w)>7: issues.append(f'Bridge {w}')
    hook=secs_l['Chorus'][0]
    if not 4<=len(hook.split())<=7: issues.append('hook')
    fin=secs_l['Final Chorus']
    if fin[0]!=hook: issues.append('final hook differs')
    low=lyr.lower()
    bw=[x for x in banned if re.search(r'\b'+x,low)]
    print(f"{name:22} {sum(bars)} bars {int(secs)//60}:{int(secs)%60:02d} V1{[len(x.split()) for x in secs_l['Verse 1']]} V2{[len(x.split()) for x in secs_l['Verse 2']]} banned={bw} issues={issues}")
