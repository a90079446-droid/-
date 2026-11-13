# 인수인계 (클라우드 세션 → PC)

이 문서는 클라우드에서 한 대화와 작업을 PC의 Claude Code가 이어받도록 정리한 거야.
PC의 Claude Code에서 **"HANDOFF.md 읽고 이어서 해줘"**라고 하면 돼.

- 저장소: `a90079446-droid/-`, 작업 브랜치 `claude/install-iga-br80mb`
- 사용자는 **윈도우 PC**를 쓰고, Claude Code 2.1.323이 설치되어 있고, 작업 폴더는 `문서\클로드코드`(OneDrive 안)야.
- 영상처럼 큰 파일은 OneDrive 밖(`C:\video` 등)에서 작업하는 걸 권장해.

## 1. 사용자 성향과 규칙 (CLAUDE.md에도 있음)

- 쉬운 한국어로 짧게. 컴퓨터 없이 되는 일은 묻지 말고 바로 한다.
- 커밋 메시지는 알아서 쓰고, 끝나면 커밋·푸시한다.
- 스킬은 저장소 `.claude/skills/`에 넣는다.
- 스레드 글은 긴 썰, 친구한테 말하듯 반말, 유머, 누구나 공감할 주제, 홍보는 거의 없이.
- 별 100개 미만 저장소의 스킬은 "검증 안 됨"으로 보고 쓰지 않는다. (실제로 30개를 지웠음)
- 크레딧이 드는 일(Higgsfield 영상 등)은 비용을 알리고 확인을 받고 시작한다.
- 지어낸 이야기를 사실처럼 쓰지 않는다. 썰의 `[ ]`는 실제 경험으로 바꿔 쓰게 한다.

## 2. 사용자 상황

- 직업: 베란다 곰팡이 / 탄성코트 뿜칠 시공. 브랜드 중 하나는 "잼잼오프"(암막 블라인드, 릴스를 올림).
- 하려는 일: 스레드·인스타·유튜브로 계정을 키워서 수익 만들기. 유튜브는 경제 채널, 얼굴 없이 AI로 운영하는 방법을 알아보는 중.
- 실제 시공 순서(사용자가 알려 줌): **스크래퍼로 벽 긁기 → 베란다 청소 → 보양(비닐) → 실리콘 → 분사작업**.
  장비: 거실에 컴프레셔, 호스를 베란다로 끌고 와서 페인트 건으로 뿜칠. 출입 샤시와 바닥은 비닐 보양.

## 3. 만든 결과물 (모두 저장소에 있음)

| 위치 | 내용 |
|---|---|
| `plans/threads-2weeks.md` | 스레드 2주 플랜 v4 (반말·웃긴 썰 14개 전문) |
| `plans/threads-morning.md` | 스레드 아침용 공감글 1주 (7개 전문) |
| `plans/threads-monday-director.md` | 월요일 알람 글, 감독 버전 |
| `reels/jamjam_viral.mp4` | 잼잼오프 릴스 편집본 (8.5초) |
| `reels/tanseong_text_reel.mp4` | 탄성코트 글자 애니메이션 릴스 (17초) |
| `reels/tanseong_process_reel.mp4` | 시공 과정 2D 애니메이션 + 나레이션 + 자막 (32초) |
| `reels/tanseong_cartoon/` | Three.js 3D 카툰 작업자 소스와 테스트 이미지 (영상으로는 안 뽑음, 사용자가 만화풍을 원치 않음) |
| `reels/tanseong_blender/` | Blender(bpy) 베란다 장면 스크립트와 테스트 렌더 |
| `reels/tanseong_photo/` | 실사 AI 이미지: 베란다 뿜칠 2종 + 5단계(긁기·청소·보양·실리콘·분사) 키프레임 |
| `tools/SETUP.md` | 영상·3D 도구 설치 메모 |

**사용자가 원하는 최종 영상:** 자막·글자 없이, **진짜 사람처럼 보이는 실사 느낌**으로, **아파트 베란다**에서 위의 5단계 시공 과정을 보여 주는 영상. 만화·마네킹 느낌은 싫어함. 글자 없이 시공 장면만, 나레이션은 선택.
- 지금까지의 방법: Higgsfield MCP로 실사 이미지를 만듦(마음에 들어 함). 영상화는 5초 클립당 약 8.75 크레딧이라 사용자가 "그만해"라고 해서 멈춤. 남은 크레딧 약 65.
- 이어서 하려면: 5장의 키프레임(`reels/tanseong_photo/s1~s5`)을 시작 장면으로 이미지→영상 변환(예: kling3_0, 9:16, 5초), 비용 확인 후 진행. 영상 편집·이어 붙이기는 PC의 ffmpeg로.

## 4. 클라우드에서 막혔던 것 → PC에서 하면 되는 것

- **네이버 블로그**: https://m.blog.naver.com/smts91/224472131125 (시공 작업기). 이 글을 읽고 실제 작업 순서와 장비를 영상에 반영해 줘. 다른 글 https://m.blog.naver.com/mr_choo/224474951309 는 "타이포그래피 스킬" 소개글이었음(사용자는 뱅모션이 맞는 것 같다고 함, 설치됨).
- **인스타 릴스 참고 영상**: https://www.instagram.com/reel/DfpTC8Fkp6K/ (탄성코트 홍보 릴스 참고용)
- **스레드 참고 영상**: https://www.threads.com/share/BAWCWd8UTN (원하는 영상 느낌)
- 위 세 링크는 클라우드에서 못 열었어. PC에서 열 수 있으면 읽고 분석해서 반영해 줘.
- 유튜브·PLAYBOARD 등 순위 사이트도 클라우드에서는 막혔음 → PC에서 경제 채널·쇼츠 채널 순위 확인.

## 5. PC에 설치해야 할 것 (클라우드 임시 설치였거나 못 한 것)

클라우드는 세션이 끝나면 초기화돼서, 아래는 PC에 따로 설치해야 해. (명령은 일반적인 방법이고 이 문서를 쓸 때 PC에서 확인하지는 못했어. 안 되면 오류 문구를 보고 고쳐 줘.)

**기본 도구 (winget)**
```
winget install Git.Git
winget install OpenJS.NodeJS.LTS
winget install Python.Python.3.12
winget install Gyan.FFmpeg
```

**영상·3D 도구**
- Blender: `winget install BlenderFoundation.Blender` (스크립트용은 `pip install bpy`)
- Godot: `winget install GodotEngine.GodotEngine`
- Unreal Engine: Epic Games Launcher(`winget install EpicGames.EpicGamesLauncher`)로 설치 (계정 필요, 용량 큼)
- Unity: Unity Hub(`winget install Unity.UnityHub`)로 설치 (계정 필요)
- Three.js: `npm install three` (Canvas 2D는 브라우저 내장)
- 하이퍼프레임즈: `npx hyperframes init my-video` (클라우드에서 0.9.39로 확인됨)
- 리모션: `npx create-video@latest --yes --blank my-series` (4.0.543으로 확인됨)

**파이썬 도구**
```
pip install faster-whisper yt-dlp
pip install graphifyy
pip install git+https://github.com/NVIDIA/SkillSpector
```
- `graphifyy`: Graphify 스킬이 쓰는 프로그램(클라우드에서 설치·확인함).
- SkillSpector: `skill-inspector` 스킬이 쓰는 검사 프로그램. 클라우드에서는 권한 검사에 막혀 설치하지 못했음.

**첫 사용 때 자동으로 받는 것**
- `lemo-opuscar` 스킬은 처음 쓸 때 라이브러리(155MB)를 GitHub에서 받아 `~/lemo-opuscar`에 둠. (스타일 99개, 영상 스타일 갤러리 https://lemomo-ai.github.io/lemo-opuscar/ )
- `watch` 스킬(claude-video)은 첫 실행 때 설정 질문을 함(yt-dlp, ffmpeg 필요).

**연결(MCP) — 계정 단위라서 PC에서 다시 확인**
- Higgsfield MCP: claude.ai 커넥터로 연결되어 있음(크레딧 있음).
- 카카오 PlayMCP: https://playmcp.kakao.com/mcp 를 claude.ai/customize/connectors 에서 커스텀 커넥터로 추가, 카카오 로그인, 도구함에 "카카오톡 나와의 채팅" 담기. (카톡으로 "나에게 보내기"만 가능하고 대화는 안 됨. 아직 연결 안 함.)

## 6. 설치된 스킬 (`.claude/skills/`, 309개)

PC에서 저장소를 받으면 그대로 따라와. 별 100개 이상 저장소만 남겼어. 큰 묶음:

- 인스타·스레드·SNS: claude-content-skills(55), Jakeschincariol/instagram-agent-skill(13), ScrapeCreators 리서치(12), sergebulaev/instagram-skills(9), blacktwist/social-media-skills(14), social-media-skills/skills(인스타·스레드 쪽 66), threads-carousel, head-of-content(2)
- 유튜브: Jakeschincariol/youtube-agent-skill(`yt-` 11개), `watch`(claude-video), `last30days`(최근 30일 반응 조사)
- 글쓰기: haowjy/creative-writing-skills(12: creative-writing-muse, writing-principles, character-sim, story-review 등)
- 디자인·개발: wondelai/skills(65), mattpocock/skills(27), impeccable, design-taste-frontend, security-audit, clean-user-facing-text, remove-ai-marks, reverse-engineer-anything
- 영상·애니메이션: bang-motion, line-art-animation, lemo-opuscar
- 도구: graphify, obsidian 스킬 7개, find-skills, skill-inspector
- 기타: content52-ko(리본랩스 안내 스킬, GitHub 저장소가 아니라 별 수 확인 불가라 남겨 둠. 지울지 사용자에게 물어봤고 답은 아직 없음)
- 라이선스: `.claude/skills/_licenses/`

참고: Matt Pocock의 `code-review`는 Claude Code 기본 `/code-review`와 이름이 같아서 헷갈릴 수 있어.

## 7. 앞으로 할 일 (사용자가 관심 보인 것)

1. 실사 시공 영상 만들기(위 3번), 블로그 글 읽고 순서 맞추기.
2. 스레드 글: 월요일 외 요일도 "감독 버전"으로 다시 쓰기(사용자가 제안에 답하지 않았음).
3. 유튜브 경제 채널: 콘셉트, 첫 10개 영상, 쇼츠 대본. 경제 채널은 AI 아바타가 전문가처럼 말하지 않고, 종목 추천·수익 보장 표현을 피한다. 한국 유료 투자 조언은 신고 의무가 있으니 법률 확인이 필요.
4. 카카오 PlayMCP 연결, GitHub 기본 브랜치 병합(PR)은 사용자가 원할 때.

## 8. 주의

- 이 저장소에는 비밀번호·API 키를 넣지 않았어. 키는 넣지 마.
- PC 연결은 `claude rc`로 되어 있고, 그 PowerShell 창을 닫으면 끊겨.
- 사진 속 인물은 모두 AI가 만든 가상의 사람이야. 실제 고객·인물의 얼굴이나 개인 정보는 없어.
