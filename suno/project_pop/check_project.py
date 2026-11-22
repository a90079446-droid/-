"""프로젝트 pop 곡 검수: python3 check_project.py <file.md> [...]"""
import re,sys,json,os
BAN=["neon","shadow","midnight","dark","static","echo","fade"]
ref=set(); refgrams=set()
pj=os.environ.get("REF_JSON")
if pj and os.path.exists(pj):
    for pc in json.load(open(pj))["playlist_clips"]:
        for l in pc["clip"]["metadata"].get("prompt","").split("\n"):
            if l.strip() and not l.startswith("["):
                w=re.findall(r"[a-z']+",l.lower()); ref.add(" ".join(w))
                for i in range(len(w)-4): refgrams.add(" ".join(w[i:i+5]))
RULES={
 "기본형":{"Intro":(2,2,None),"Verse 1":(8,8,(8,10)),"Pre-Chorus":(4,4,None),"Chorus":(8,8,(4,6)),"Breakdown":(1,1,None),"Verse 2":(8,8,(8,10)),"Bridge":(4,8,None),"Final Chorus":(8,8,(4,6)),"Outro":(2,2,None)},
 "Unlisted형":{"Verse 1":(8,8,(7,10)),"Pre-Chorus":(4,4,None),"Chorus":(8,8,(7,11)),"Verse 2":(8,8,(7,10)),"Bridge":(4,4,None),"Final Chorus":(8,8,(7,11))},
 "ASK WHY형":{"Hook":(8,8,(6,10)),"Verse 1":(16,16,(6,10)),"Bridge":(8,8,None),"Verse 2":(16,16,(6,10)),"Final Hook":(8,8,(6,10))},
}
def wc(l): return len(re.findall(r"[A-Za-z0-9']+",l))
bad=0
for f in sys.argv[1:]:
    t=open(f).read()
    for m in re.finditer(r"\n## (\d+)\. ([^\n]+)\n(.*?)(?=\n## \d+\. |\Z)",t,re.S):
        no,title,body=m.groups(); issues=[]
        ty=re.search(r"구조\**:?\**\s*(기본형|Unlisted형|ASK WHY형)",body); ty=ty.group(1) if ty else None
        if not ty: issues.append("구조 유형 표기 없음")
        lb=re.search(r"② 가사[^\n]*\n```\n(.*?)```",body,re.S)
        if not lb: print(no,title,"가사 블록 없음"); bad+=1; continue
        lyr=lb.group(1); secs=[]; cur=None
        for line in lyr.split("\n"):
            h=re.match(r"\[([^\]:]+)",line.strip())
            if h: cur=h.group(1).strip(); secs.append([cur,[]]); continue
            if line.strip() and cur: secs[-1][1].append(line.strip())
        first={}
        for n,L in secs: first.setdefault(n,L)
        if ty:
            for n,(lo,hi,wr) in RULES[ty].items():
                if n not in first: issues.append(f"{n} 없음"); continue
                L=first[n]
                if not lo<=len(L)<=hi: issues.append(f"{n} {len(L)}줄")
                if wr:
                    ws=[wc(x) for x in L]; avg=sum(ws)/len(ws) if ws else 0
                    if not wr[0]<=avg<=wr[1] or min(ws)<wr[0]-1 or max(ws)>wr[1]+1: issues.append(f"{n} 단어{ws}")
            ch="Hook" if ty=="ASK WHY형" else "Chorus"; fc="Final Hook" if ty=="ASK WHY형" else "Final Chorus"
            if ch in first and fc in first and first[ch][:1]!=first[fc][:1]: issues.append("핵사비 첫 줄이 사비와 다름")
        alllines=[l for n,L in secs for l in L]
        if not 44<=len(alllines)<=68: issues.append(f"총 {len(alllines)}줄")
        low=lyr.lower()+" "+body.lower()
        bw=[b for b in BAN if re.search(r"\b"+b,low)]
        if bw: issues.append(f"금지어 {bw}")
        cp=[l for l in alllines if " ".join(re.findall(r"[a-z']+",l.lower())) in ref]
        gr=set()
        for l in alllines:
            w=re.findall(r"[a-z']+",l.lower())
            for i in range(len(w)-4):
                g=" ".join(w[i:i+5])
                if g in refgrams: gr.add(g)
        if cp or gr: issues.append(f"기존 곡과 겹침 {cp[:2]} {list(gr)[:2]}")
        st=re.search(r"③ 스타일[^\n]*\n```\n(.*?)```",body,re.S)
        if not st: issues.append("스타일 없음")
        elif len(st.group(1))>1000: issues.append(f"스타일 {len(st.group(1))}자")
        for k in ["④ 제외","⑤ 기이함","⑥ 스타일 영향","⑦ 다양성"]:
            if k not in body: issues.append(f"{k} 없음")
        if issues: bad+=1
        print(f"{no:>2} {title[:28]:28} {ty} {len(alllines)}줄 {'OK' if not issues else issues}")
sys.exit(1 if bad else 0)
