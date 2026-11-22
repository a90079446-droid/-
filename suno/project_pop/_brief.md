# 프로젝트 "pop" 플레이리스트 지침 (내 곡 4개 기준, 2026-11-22)

> 매일 작업 지침서(`suno/_suno_trend_prompt.md`)와 별개입니다. 이 플레이리스트 곡을 만들 때는 이 문서를 따릅니다.
> 기준 곡: TEMPERED · HAMMER AND STEEL · ASK WHY · Unlisted (분석: `suno/profile_analysis.md`)

## 사운드
- 장르: alternative pop rock + cinematic. 변주로 랩 섞기(ASK WHY), 락 세게 밀기(Unlisted)
- 대비 공식(필수):
  - 벌스: no sub bass, sparse drums, metallic hits, rapid rhythmic delivery
  - 프리코러스: mids swell, tension builds, sub bass held back
  - 사비: heavy sub bass and big drums hit together, long soaring held notes, doubled vocals
  - 브레이크다운(2절 전 1줄): drums drop out, quiet
  - 브릿지: sub and bass stripped out, rapid-fire short phrases (또는 half-time)
  - 마지막 사비: half-step lift 또는 maximum power
- 보컬: 남성, 낮은 음역. 벌스는 빠르고 리듬감 있게(또는 가깝게 속삭이듯), 사비는 길게 뻗거나 거칠게 조절된 벨팅. 리드 더블링
- 길이 3:00~3:30

## 구조 (기본형 = TEMPERED형)
Intro(조용한 노래 2줄, 드럼 없음) → Verse 1(8줄) → Pre(4줄) → Chorus(8줄) → Breakdown(1줄) → Verse 2(8줄) → Pre(4줄) → Chorus → Bridge(4~8줄 단타) → Final Chorus(키업) → Outro(인트로 2줄을 살짝 바꿔 되풀이)
- 변형 A (ASK WHY형, 랩): 연주 인트로 4마디 → Hook 먼저 → 1마디 정지 → Verse(16줄) → Hook → 챈트 Bridge → Verse(16줄) → 1마디 정지 → Final Hook → 808 한 방
- 변형 B (Unlisted형, 락): 인트로 없이 Verse부터 → Pre → Chorus → Verse 2 → Chorus → half-time Bridge(4줄) → Final Chorus → 2마디 기타 한 방으로 끝

## 가사
- 영어 100%. 태도: 선언형·앤섬. 시련을 버팀, 반격, 성장, 돈으로 못 사는 것
- 은유 하나를 곡 전체에 걸쳐 끌고 간다(예: 담금질, 망치, 자물쇠, 목록에 없는 것). 섞지 않는다
- Verse 8줄 · 줄당 8~10단어 · 2줄 라임. 2절은 장면으로 이야기를 진전시키거나 뒤집는다(후배에게 집게 건네기, "Thank you for the fire")
- Chorus 8줄 · 줄당 4~6단어(Unlisted형은 8~10단어). 첫 줄이 훅
- Pre 4줄, Bridge는 같은 구조의 짧은 문장을 반복해 쌓기
- 구어체 축약 허용: comin', ain't, I'ma, 'em
- 인트로·아웃트로 수미상관
- 실존 가수·곡 이름, 기존 가사 복사 금지

## Suno 입력 순서와 기본값
① 제목 → ② 가사 → ③ 스타일 → ④ 제외 스타일 → ⑤ 기이함 15% → ⑥ 스타일 영향 85% → ⑦ 다양성(지금 쓰시는 값 유지)
- 스타일은 v6용 문장형 편곡 설명으로 쓴다(템플릿은 `suno/profile_analysis.md`)
- 제외 스타일 기본: female vocals, falsetto, metal, screaming, EDM drop, country, autotune, lo-fi, muffled vocals, Christmas bells

## 이미 쓴 은유·제목 (겹치지 않게)
담금질(TEMPERED) · 망치와 강철(HAMMER AND STEEL) · 자물쇠·호기심(ASK WHY) · 돈으로 못 사는 것(Unlisted)
