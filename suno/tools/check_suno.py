"""Suno 공통 규칙 검수 (suno/_suno_tag_rules.md)
사용: python3 check_suno.py <file.md> [...]   (곡: '## N. 제목', ② 가사/③ 스타일 코드블록)"""
import re,sys
bad=0
for f in sys.argv[1:]:
    t=open(f).read()
    for m in re.finditer(r"\n## (\d+)\. ([^\n]+)\n(.*?)(?=\n## |\Z)",t,re.S):
        no,title,b=m.groups(); iss=[]
        proj=("기본형" in b or "Unlisted형" in b or "ASK WHY형" in b or "프로젝트" in b)
        lb=re.search(r"② 가사[^\n]*\n```\n(.*?)```",b,re.S)
        if lb:
            tags={}
            for line in lb.group(1).split("\n"):
                s=line.strip()
                if not s: continue
                if "[" in s and not (s.startswith("[") and s.endswith("]")): iss.append(f"가사 줄 안 태그: {s[:30]}")
                mm=re.match(r"\[([^\]:]+):?([^\]]*)\]$",s)
                if mm:
                    name,cue=mm.group(1).strip(),mm.group(2).strip()
                    n=len([c for c in cue.split(",") if c.strip()]) if cue else 0
                    if n>3: iss.append(f"[{name}] 지시 {n}개")
                    tags.setdefault(name,set()).add(cue)
            for name in ("Chorus","Pre-Chorus","Hook"):
                if name in tags and len(tags[name])>1: iss.append(f"반복 [{name}] 태그가 서로 다름")
        st=re.search(r"③ 스타일[^\n]*\n```\n(.*?)```",b,re.S)
        if st:
            s=st.group(1).strip(); lo,hi=(300,450) if proj else (250,400)
            if not lo<=len(s)<=hi: iss.append(f"스타일 {len(s)}자 (권장 {lo}~{hi})")
            if re.search(r"\bno\s+(?!sub bass)\w+",s.lower()): iss.append("스타일에 부정어 'no'")
        if iss: bad+=1
        print(f"{no:>2} {title[:30]:30} {'OK' if not iss else iss}")
sys.exit(1 if bad else 0)
