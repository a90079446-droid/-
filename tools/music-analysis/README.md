# 레퍼런스 곡 스타일 분석기

곡 파일 하나를 넣으면 아래 항목을 분석해서 표로 정리하고, **수노(Suno) 스타일 칸에 넣을 프롬프트 초안**을 만들어 줘요.

| 분석 항목 | 쓰는 도구 |
|---|---|
| 템포(BPM), 키(조성), 음량 | Essentia |
| 박자 (4박 계열 / 3박 계열, 추정) | Essentia 박 검출 + 저음 강세 패턴 |
| 장르·스타일 (400종) | Essentia Discogs 모델 |
| 악기 (40종) | Essentia MTG-Jamendo 악기 모델 |
| 분위기·테마 (56종) | Essentia MTG-Jamendo 분위기 모델 |
| 보컬 유무, 보컬 성별, 춤추기 좋은 정도 | Essentia 분류 모델 |
| 곡 구조 (반복 구간 A/B/C, 후렴 후보) | librosa |

## 설치

```bash
pip install essentia-tensorflow librosa
```

- 리눅스와 맥에서 돼요. **윈도우는 WSL(윈도우 안의 리눅스)에서** 실행하세요. Essentia가 윈도우용으로는 제공되지 않아요.
- 분석 모델(약 28MB)은 처음 실행할 때 `essentia.upf.edu`에서 자동으로 받아요. 수동으로 받으려면 `./download_models.sh`를 실행하세요.
- 그래픽카드는 필요 없어요. 곡 하나에 몇 초에서 수십 초 걸려요.

## 사용법

```bash
python3 analyze.py 곡.mp3                  # 곡과 같은 폴더에 곡이름_analysis.md / .json 저장
python3 analyze.py 곡.mp3 --out 결과폴더
python3 analyze.py 곡.mp3 --no-structure   # 곡 구조 분석 건너뛰기 (더 빠름)
```

mp3, wav, m4a, flac 등 대부분의 형식을 읽어요.

## 결과 예시 (합성 테스트 곡)

```
| 템포 | 100.0 BPM |
| 키   | C major (장조) |
| 박자 | 4박 계열 (4/4) · 추정 |

| 구간 | 시간 | 라벨 | 추정 |
| 1 | 0:00~0:28 | A |          |
| 2 | 0:28~0:48 | B | 후렴 후보 |
| 3 | 0:48~1:07 | A |          |
| 4 | 1:07~1:27 | B | 후렴 후보 |
| 5 | 1:27~1:46 | C |          |
| 6 | 1:46~2:04 | B | 후렴 후보 |

수노 스타일 프롬프트 초안:
ambient, deep house, female vocal, synthesizer, piano, bass, happy, relaxing, 100 BPM, C major
```

## 알아둘 점

- **점수는 모델의 추정치**예요. 장르·분위기는 곡 전체 평균이라 구간마다 다를 수 있어요.
- **박자**는 저음 강세 패턴으로 추정해요. 4/4와 3/4(6/8) 구분 정도만 믿으세요.
- **곡 구조**의 같은 글자는 "비슷하게 들리는 구간"이에요. intro/verse/chorus를 확정하는 게 아니라 후렴 후보만 표시해요.
- 프롬프트 초안은 출발점이에요. 들어보고 단어를 빼거나 더해서 쓰세요. **가수 이름이나 곡 이름은 수노에 넣지 마세요.**
- 분석은 **구조, 분위기, 사운드를 참고하는 데까지만** 쓰세요. 가사 문장이나 멜로디를 그대로 가져오면 저작권 문제가 생길 수 있어요.

## 라이선스

- Essentia: AGPL-3.0 / Essentia 모델: CC BY-NC-SA 4.0 (**비상업**) → 개인 레퍼런스 분석 용도로 사용하세요.
- librosa: ISC
- 이 스크립트(`analyze.py`, `download_models.sh`): 이 저장소 소유자 것
