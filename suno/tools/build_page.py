"""곡 패키지 .md → Copy 버튼 페이지 .html
사용: python3 build_page.py <in.md> <out.html> "<페이지 제목>" "<한 줄 소개>"
md 형식: '## 분석' 목록(선택), 곡마다 '## N. 제목' + '- 키: 값' 줄 + ② 가사/③ 스타일/④ 제외 코드블록 + ⑤⑥⑦ 줄"""
import re,json,sys,html,os
src,out,title,lede=sys.argv[1:5]
t=open(src).read()
ana=re.search(r"## 분석\n(.*?)(?=\n## )",t,re.S)
analysis=[re.sub(r"^- ","",l).strip() for l in (ana.group(1).split("\n") if ana else []) if l.strip().startswith("- ")]
songs=[]
for m in re.finditer(r"\n## (\d+)\. ([^\n]+)\n(.*?)(?=\n## |\Z)",t,re.S):
    no,name,b=m.groups()
    g=lambda p:(re.search(p,b,re.S).group(1).strip() if re.search(p,b,re.S) else "")
    meta=[l[2:].strip() for l in b.split("\n") if l.startswith("- ")]
    sl=re.search(r"⑤ 기이함\**:?\**\s*([^·\n]+)·\s*\**⑥ 스타일 영향\**:?\**\s*([^·\n]+)·\s*\**⑦ 다양성\**:?\**\s*([^\n]+)",b)
    w,si,v=[x.strip().strip('*') for x in sl.groups()] if sl else ("","","")
    songs.append(dict(no=no,title=name.strip(),meta=meta,lyrics=g(r"② 가사[^\n]*\n```\n(.*?)```"),
        style=g(r"③ 스타일[^\n]*\n```\n(.*?)```"),exclude=g(r"④ 제외[^\n]*\n```\n(.*?)```"),w=w,si=si,v=v.replace("지금 쓰시는 값 유지","유지")))
css=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"page.css")).read()
data=json.dumps(dict(songs=songs,analysis=analysis),ensure_ascii=False).replace("</","<\\/")
page=f'''<title>{html.escape(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400&display=swap">
<style>{css}</style>
<div class="wrap">
<header><h1>{html.escape(title)}</h1><p class="lede">{html.escape(lede)}</p></header>
<section id="ana"></section>
<main id="list" style="display:flex;flex-direction:column;gap:12px"></main>
</div>
<div class="toast" id="toast" hidden>Copied</div>
<script>
const D={data};
const toast=document.getElementById('toast');let tt;
function show(m){{toast.textContent=m;toast.hidden=false;clearTimeout(tt);tt=setTimeout(()=>toast.hidden=true,1400)}}
function esc(s){{return String(s).replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]))}}
if(D.analysis.length){{document.getElementById('ana').innerHTML='<details class="song"><summary><span class="no">i</span><span class="t">레퍼런스 분석</span><span class="sub">출처와 측정 한계 포함</span></summary><div class="body"><ul class="alist">'+D.analysis.map(a=>'<li>'+esc(a)+'</li>').join('')+'</ul></div></details>'}}
function field(label,id,text){{return text?`<div class="field"><div class="fh"><span class="label">${{label}}</span><button class="copy" data-copy="${{id}}">Copy</button></div><pre id="${{id}}">${{esc(text)}}</pre></div>`:''}}
document.getElementById('list').innerHTML=D.songs.map((s,i)=>`<details class="song" ${{i===0?'open':''}}><summary><span class="no">${{esc(s.no)}}</span><span class="t">${{esc(s.title)}}</span><span class="sub">${{esc((s.meta.find(m=>m.startsWith('방향'))||s.meta[0]||'').replace(/^방향: /,''))}}</span></summary><div class="body">
<ul class="meta">${{s.meta.map(m=>'<li>'+esc(m)+'</li>').join('')}}</ul>
${{field('① Song Title','t'+i,s.title)}}${{field('② Lyrics','l'+i,s.lyrics)}}${{field('③ Styles','s'+i,s.style)}}${{field('④ Exclude Styles','e'+i,s.exclude)}}
<div class="nums"><div class="num"><b>${{esc(s.w)}}</b><span>⑤ Weirdness</span></div><div class="num"><b>${{esc(s.si)}}</b><span>⑥ Style Influence</span></div><div class="num"><b>${{esc(s.v)}}</b><span>⑦ 다양성</span></div></div>
</div></details>`).join('');
document.addEventListener('click',e=>{{const b=e.target.closest('.copy');if(!b)return;const el=document.getElementById(b.dataset.copy);
 const sel=()=>{{const r=document.createRange();r.selectNodeContents(el);const w=getSelection();w.removeAllRanges();w.addRange(r);show('Selected — copy it')}};
 try{{navigator.clipboard.writeText(el.textContent).then(()=>show('Copied'),sel)}}catch(_){{sel()}}}});
</script>'''
open(out,"w").write(page); print(out,len(songs),"songs")
