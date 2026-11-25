# Suno 작곡법 자료 조사 (2026-11-25)

> 공식 문서(help.suno.com, release notes)와 커뮤니티·업체 가이드를 나눠 정리. 커뮤니티 내용은 검증 안 된 경험담이 많고 모델 버전마다 다를 수 있음.

## 1. 공식 자료 (Suno)
- Creative Sliders (help.suno.com/en/articles/6141377)
  - Weirdness: Safe ~ Chaos, **50%가 '보통' 결과**
  - Style Influence: 스타일 입력을 얼마나 따를지 Loose ~ Strong
  - Audio Influence: **오디오를 업로드했을 때만** 나오는 세 번째 슬라이더
- Exclude (help.suno.com/en/articles/3161921): Custom Mode의 Advanced Options에 있음. 빼고 싶은 악기·요소를 넣는 공식 방법
- Exclude Styles 출시 노트 (2024-09-19): 제외 항목은 Styles에 '-piano'처럼 마이너스로 표시. 당시 Pro/Premier 베타 (현재 등급 제한은 확인 못 함)
- 지식 베이스: help.suno.com/en/categories/2827585 / 안드로이드 Custom Mode: help.suno.com/en/articles/3726721

## 2. 모델 현황
- v6 출시 2026-09-09: v6, v6-wild(유료), v6-mini(무료). 이전 모델은 전부 은퇴 (aimusicpreneur, sunomaster, scriptbyai)
- v6는 "후렴만 바꿔 줘" 같은 자연어로 곡 일부 수정, 가사 한 줄 교체 가능하다는 보도 (3자 매체)
- Studio 2.0(브라우저 DAW) 2026-08-13 Premier 대상, 10-29 업데이트로 Clip Settings·Studio Chat 추가 (scriptbyai)
- 내 플레이리스트 Unlisted가 v6로 생성된 곡

## 3. 커뮤니티 공통 의견 (출처 여러 곳에서 반복)
### Style 칸
- 장르를 맨 앞에. 앞쪽 단어에 가중치가 있다는 주장 (r/SunoAI 인용, 미검증)
- 순서 예: 장르·시대 → 무드 → 악기 2~3개 → 보컬 성격 → 프로덕션
- 길이: 120~250자(songaifarm·tonedraft) 또는 100단어 이하(r/SunoAI 요약). v5/v5.5는 약 1,000자에서 잘림
- 구조 태그([Verse] 등)는 Style에 넣지 않는다
- 장르 하나를 중심에. 장르를 쌓으면 결과가 무작위
- 부정어는 Style보다 Exclude 칸에
- 보이스 클론·페르소나를 쓰면 보컬 성별 묘사는 빼라는 조언
### 가사 칸·메타태그
- 태그는 '명령'이 아니라 '제안'으로 작동
- 태그는 줄 하나에 따로. 가사 줄 안에 넣은 태그는 무시됨
- 섹션당 지시는 1~2개면 충분. 연속 태그 2~3개까지는 괜찮고 5개 넘으면 혼란
- 구조·에너지 태그를 보컬 태그보다 앞에
- **반복되는 후렴은 태그를 똑같이** 유지하면 일관성이 좋아짐
- [Instrumental, 8 bars] 같은 연주 구간 지시로 숨 쉴 틈을 줌
- 가사는 짧은 줄, 한 호흡에 부를 수 있게. 장르·악기 지시는 Style로
- 가사 길이 100~120단어 권장이라는 r/SunoAI 요약도 있으나, 내 플레이리스트 곡(약 480~520단어)은 문제없이 생성됨 → 참고만
- 비영어 가사여도 섹션 태그는 영어로
### 보컬
- 'male vocals'를 Style에 명시 (가사 태그보다 잘 먹힘)
- 랩: "rapped, rhythmic spoken flow", 웅얼거림 방지 "clear vocals, crisp enunciation"
- v5 계열: 가사 전 허밍·'ooh'·말하는 인트로가 생기기 쉬움 → Exclude

## 4. 지금 지침에 반영할 만한 점 (제안)
1. **반복 사비 태그 통일**: 지금은 첫 사비 "Half energy", 둘째 "Full energy"처럼 다르게 씀. 커뮤니티는 같게 하라고 함. 내 플레이리스트 곡도 같은 태그를 반복함 → 첫 사비와 반복 사비 태그를 같게, 에너지 차이는 핵사비 태그에서만
2. **섹션 태그 지시 줄이기**: 지금 태그에 지시가 4~6개 붙는 경우가 많음 → 2~3개로
3. **스타일 길이**: 지금 350~600자. 커뮤니티 권장은 더 짧음 → 데일리형은 250~400자로 줄이는 버전을 A/B 테스트
4. **슬라이더 해석**: 공식 기준 기이함 50%가 보통. 지금 15~40%는 '안전 쪽'이 맞음. 세 번째 슬라이더는 공식 이름이 Audio Influence이고 오디오 업로드 때만 나옴 → 만들기 탭의 '다양성'이 무엇인지는 여전히 확인 못 함 (화면 캡처를 주면 확정 가능)
5. **v6 부분 수정**: 결과 중 후렴만 마음에 안 들면 곡 전체를 다시 만들지 말고 v6 자연어 수정으로 그 부분만 고치기

## 출처
- https://help.suno.com/en/articles/6141377 (Creative Sliders, 공식)
- https://help.suno.com/en/articles/3161921 (Exclude, 공식)
- https://suno.com/release-notes/exclude-styles (Exclude Styles 출시 노트, 공식)
- https://help.suno.com/en/categories/2827585 (지식 베이스, 공식)
- https://www.aimusicpreneur.com/ai-tools-news/suno-v6-v6-wild-v6-mini-launch/
- https://sunomaster.com/blog/suno-v6-explained
- https://www.scriptbyai.com/suno-ai-timeline/
- https://www.songaifarm.com/blog/suno-prompts-v5-5
- https://www.tonedraft.com/en/blog/suno-ai-prompt-guide-2026
- https://blakecrosley.com/guides/suno
- https://blakecrosley.com/blog/suno-style-field-style-influence
- https://hookgenius.app/learn/suno-metatags-complete-list/
- https://hookgenius.app/learn/suno-v5-5-guide/
- https://roo.beehiiv.com/p/suno-prompting
- https://niller2005.github.io/suno/guide/meta-tags.html
- https://jackrighteous.com/pages/suno-ai-meta-tags-guide
- https://medium.com/@aitooldiscovery/suno-reddit-tips-and-prompts-what-r-sunoai-users-actually-do-65b59d51bcad
- https://github.com/mttkllr/suno-field-guide
