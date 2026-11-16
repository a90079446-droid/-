#!/usr/bin/env python3
"""레퍼런스 곡 스타일 분석기 (Essentia 기반).

곡 파일 하나를 넣으면 템포, 키, 박자(추정), 장르·스타일, 악기, 분위기·테마,
보컬 유무·성별, 춤추기 좋은 정도를 뽑고, 수노(Suno) 스타일 칸에 넣을
영어 프롬프트 초안을 만든다. 결과는 화면에 출력하고 JSON/Markdown으로 저장한다.

사용법:
    python3 analyze.py 곡.mp3                # 결과를 곡 이름_analysis.{json,md} 로 저장
    python3 analyze.py 곡.mp3 --out 결과폴더
    python3 analyze.py 곡.mp3 --no-structure # 곡 구조 분석 건너뛰기 (더 빠름)

모델 파일은 models/ 폴더에 둔다. 없으면 처음 실행할 때 download_models.sh 로 자동으로 받는다.
분석은 개인 레퍼런스 용도. Essentia 모델은 CC BY-NC-SA 4.0 (비상업).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np  # noqa: E402

try:
    import essentia  # noqa: E402
    essentia.log.infoActive = False
    essentia.log.warningActive = False
    import essentia.standard as es  # noqa: E402
except ImportError:  # pragma: no cover
    sys.exit("essentia 가 없습니다. 먼저: pip install essentia-tensorflow")

HERE = Path(__file__).resolve().parent
MODELS = HERE / "models"
EMBED = "discogs-effnet-bs64-1.pb"

HEADS = {
    "genre": "genre_discogs400-discogs-effnet-1",
    "instrument": "mtg_jamendo_instrument-discogs-effnet-1",
    "moodtheme": "mtg_jamendo_moodtheme-discogs-effnet-1",
    "voice": "voice_instrumental-discogs-effnet-1",
    "gender": "gender-discogs-effnet-1",
    "danceability": "danceability-discogs-effnet-1",
}

# 수노 프롬프트에 쓰기 좋게 악기 라벨을 풀어 쓴다.
INSTRUMENT_WORDS = {
    "acousticbassguitar": "acoustic bass", "acousticguitar": "acoustic guitar",
    "electricguitar": "electric guitar", "classicalguitar": "classical guitar",
    "electricpiano": "electric piano", "doublebass": "double bass",
    "drummachine": "drum machine", "beat": "programmed beat",
    "computer": "electronic production", "brass": "brass section",
    "strings": "strings", "pad": "synth pad", "synthesizer": "synthesizer",
    "rhodes": "rhodes", "voice": "vocals",
}

KEY_KO = {"major": "장조", "minor": "단조"}


def head_io(name: str):
    meta = json.loads((MODELS / f"{name}.json").read_text())
    s = meta["schema"]
    inp = s["inputs"][0]["name"]
    out = next(o["name"] for o in s["outputs"] if o.get("output_purpose") == "predictions")
    return meta["classes"], inp, out


def check_models() -> None:
    missing = [f for f in [EMBED] + [f"{h}.pb" for h in HEADS.values()] + [f"{h}.json" for h in HEADS.values()]
               if not (MODELS / f).exists()]
    if missing:
        print("모델 파일이 없어 내려받습니다 (약 28MB)...", file=sys.stderr)
        import subprocess
        subprocess.run(["bash", str(HERE / "download_models.sh")], check=False)
        missing = [f for f in missing if not (MODELS / f).exists()]
        if missing:
            sys.exit("모델을 받지 못했습니다: " + ", ".join(missing)
                     + "\nessentia.upf.edu 접속이 막혀 있는지 확인하세요.")


def rhythm_and_key(path: str) -> dict:
    audio = es.MonoLoader(filename=path, sampleRate=44100)()
    duration = len(audio) / 44100.0

    bpm, beats, beats_conf, _, intervals = es.RhythmExtractor2013(method="multifeature")(audio)
    key, scale, strength = es.KeyExtractor(profileType="edma")(audio)
    loud = es.LoudnessEBUR128(sampleRate=44100)(es.StereoMuxer()(audio, audio))
    integrated_lufs = float(loud[2])
    dyn_range = float(loud[3])

    meter = estimate_meter(audio, beats)

    # BPM 이 아주 빠르거나 느리면 절반/두 배로 들릴 수 있음을 함께 알려준다.
    alt = None
    if bpm >= 150:
        alt = round(bpm / 2, 1)
    elif bpm <= 75:
        alt = round(bpm * 2, 1)

    return {
        "duration_sec": round(duration, 1),
        "bpm": round(float(bpm), 1),
        "bpm_alt": alt,
        "beat_confidence": round(float(beats_conf), 2),
        "key": key,
        "scale": scale,
        "key_strength": round(float(strength), 2),
        "loudness_lufs": round(integrated_lufs, 1),
        "loudness_range_lu": round(dyn_range, 1),
        "meter": meter,
        "_beats": [float(b) for b in beats],
    }


def estimate_meter(audio: np.ndarray, beats: np.ndarray) -> dict:
    """박마다 저음 에너지 패턴을 보고 3박 계열인지 4박 계열인지 추정한다.

    강박(마디 첫 박)은 보통 킥·베이스가 세다. 박 단위 저음 에너지의
    자기상관을 3·4 지연에서 비교한다. 정확한 박자표가 아니라 '추정'이다.
    """
    if len(beats) < 16:
        return {"guess": "unknown", "label_ko": "판단 불가 (박이 너무 적음)", "scores": {}}
    sr = 44100
    w = es.Windowing(type="hann")
    spec = es.Spectrum()
    energies = []
    for b in beats:
        start = int(b * sr)
        frame = audio[start:start + 2048]
        if len(frame) < 2048:
            break
        s = spec(w(frame))
        # 약 20~200Hz 대역 (킥·베이스)
        energies.append(float(np.sum(s[1:10] ** 2)))
    e = np.array(energies)
    if len(e) < 16 or np.std(e) == 0:
        return {"guess": "unknown", "label_ko": "판단 불가", "scores": {}}
    e = (e - e.mean()) / e.std()

    def ac(lag: int) -> float:
        return float(np.mean(e[:-lag] * e[lag:]))

    scores = {"2": ac(2), "3": ac(3), "4": ac(4)}
    triple = scores["3"]
    duple = max(scores["2"], scores["4"])
    if triple > duple + 0.05:
        guess, label = "3/4", "3박 계열 (3/4 또는 6/8)"
    else:
        guess, label = "4/4", "4박 계열 (4/4)"
    return {"guess": guess, "label_ko": label + " · 추정", "scores": {k: round(v, 3) for k, v in scores.items()}}


def structure(path: str, n_hint: int | None = None) -> list[dict]:
    """librosa 로 곡을 비슷한 소리끼리 구간으로 나누고 A/B/C 라벨을 붙인다.

    같은 글자는 비슷하게 들리는 구간(반복)이다. 가장 많이 반복되면서 에너지가
    높은 글자를 '후렴 후보'로 표시한다. intro/verse/chorus 를 확정하는 게 아니라 추정이다.
    """
    try:
        import librosa
    except ImportError:
        return []
    # librosa 는 m4a 등을 못 읽는 경우가 있어 Essentia(ffmpeg 기반)로 불러온다.
    sr = 22050
    y = es.MonoLoader(filename=path, sampleRate=sr)().astype(np.float32)
    dur = len(y) / sr
    hop = 512
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop)
    if len(beats) < 16:
        return []
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=hop)
    rms = librosa.feature.rms(y=y, hop_length=hop)[0]
    feat = np.vstack([librosa.util.normalize(chroma, axis=0),
                      librosa.util.normalize(mfcc[1:], axis=1)])
    sync = librosa.util.sync(feat, beats, aggregate=np.median)

    k = n_hint or int(np.clip(round(dur / 20), 4, 12))
    bounds = librosa.segment.agglomerative(sync, k)
    bound_frames = librosa.util.fix_frames(np.asarray(beats)[bounds], x_min=0)
    times = librosa.frames_to_time(bound_frames, sr=sr, hop_length=hop).tolist() + [dur]
    times = sorted(set(round(t, 2) for t in times))

    segs = []
    for a, b in zip(times[:-1], times[1:]):
        if b - a < 3:
            if segs:
                segs[-1]["end"] = b
            continue
        segs.append({"start": a, "end": b})
    if not segs:
        return []

    def seg_vec(s):
        fa, fb = librosa.time_to_frames([s["start"], s["end"]], sr=sr, hop_length=hop)
        v = np.concatenate([chroma[:, fa:fb].mean(axis=1), mfcc[1:, fa:fb].mean(axis=1) / 50.0])
        return v / (np.linalg.norm(v) + 1e-9), float(rms[fa:fb].mean())

    labels, protos = [], []
    for s in segs:
        v, e = seg_vec(s)
        s["energy"] = e
        best, best_sim = None, 0.0
        for i, p in enumerate(protos):
            sim = float(v @ p)
            if sim > best_sim:
                best, best_sim = i, sim
        if best is not None and best_sim >= 0.97:
            labels.append(best)
        else:
            protos.append(v)
            labels.append(len(protos) - 1)
    letters = "ABCDEFGHIJKLMNOP"
    max_e = max(s["energy"] for s in segs) or 1.0
    counts = {l: labels.count(l) for l in set(labels)}
    mean_e = {l: np.mean([s["energy"] for s, x in zip(segs, labels) if x == l]) for l in counts}
    repeated = [l for l in counts if counts[l] >= 2]
    chorus = max(repeated, key=lambda l: mean_e[l]) if repeated else None
    out = []
    for i, (s, l) in enumerate(zip(segs, labels)):
        hint = ""
        if l == chorus:
            hint = "후렴 후보"
        elif i == 0 and counts[l] == 1:
            hint = "인트로 후보"
        elif i == len(segs) - 1 and counts[l] == 1:
            hint = "아웃트로 후보"
        out.append({"start": round(s["start"], 1), "end": round(s["end"], 1),
                    "label": letters[l % len(letters)], "energy": round(s["energy"] / max_e, 2),
                    "hint": hint})
    return out


def fmt_t(t: float) -> str:
    return f"{int(t // 60)}:{int(t % 60):02d}"


def tag_models(path: str) -> dict:
    audio16 = es.MonoLoader(filename=path, sampleRate=16000, resampleQuality=4)()
    emb = es.TensorflowPredictEffnetDiscogs(
        graphFilename=str(MODELS / EMBED), output="PartitionedCall:1")(audio16)

    out = {}
    for key, name in HEADS.items():
        classes, inp, outp = head_io(name)
        preds = es.TensorflowPredict2D(
            graphFilename=str(MODELS / f"{name}.pb"), input=inp, output=outp)(emb)
        mean = np.mean(preds, axis=0)
        ranked = sorted(zip(classes, mean.tolist()), key=lambda x: -x[1])
        out[key] = [(c, round(p, 3)) for c, p in ranked]
    return out


def top(items, n, min_p=0.0):
    return [(c, p) for c, p in items[:n] if p >= min_p]


def genre_words(items, n=3):
    words = []
    for c, _ in items[:n]:
        parent, style = c.split("---") if "---" in c else ("", c)
        words.append(style.lower())
    return words


def build_prompt(r: dict, t: dict) -> str:
    parts = []
    parts += genre_words(t["genre"], 2)
    voice = dict(t["voice"])
    if voice.get("voice", 0) >= 0.5:
        g = t["gender"][0][0]
        parts.append(f"{g} vocal")
    else:
        parts.append("instrumental")
    inst = [INSTRUMENT_WORDS.get(c, c) for c, p in top(t["instrument"], 4, 0.1) if c != "voice"]
    parts += inst
    moods = [c for c, p in top(t["moodtheme"], 4, 0.05)]
    parts += moods
    parts.append(f"{round(r['bpm'])} BPM")
    parts.append(f"{r['key']} {r['scale']}")
    if r["meter"]["guess"] == "3/4":
        parts.append("3/4 waltz feel")
    seen, uniq = set(), []
    for p in parts:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return ", ".join(uniq)


def to_markdown(name: str, r: dict, t: dict, prompt: str, segs: list[dict] | None = None) -> str:
    def rows(items, n, min_p=0.0):
        return "\n".join(f"| {c} | {p:.2f} |" for c, p in top(items, n, min_p))

    voice = dict(t["voice"])
    dance = dict(t["danceability"])
    alt = f" (절반/두 배로 들리면 {r['bpm_alt']})" if r["bpm_alt"] else ""
    if segs:
        seg_md = "| 구간 | 시간 | 라벨 | 에너지 | 추정 |\n|---|---|---|---|---|\n" + "\n".join(
            f"| {i + 1} | {fmt_t(s['start'])}~{fmt_t(s['end'])} | {s['label']} | {s['energy']:.2f} | {s['hint']} |"
            for i, s in enumerate(segs))
        seg_md += "\n\n같은 글자는 비슷하게 들리는(반복되는) 구간이에요. 수노 가사 칸의 [Verse]·[Chorus] 순서를 짤 때 참고하세요."
    else:
        seg_md = "구조 분석을 건너뛰었어요 (librosa 없음 또는 곡이 너무 짧음)."
    md = f"""# 곡 스타일 분석: {name}

## 기본 정보
| 항목 | 값 |
|---|---|
| 길이 | {int(r['duration_sec'] // 60)}분 {int(r['duration_sec'] % 60)}초 |
| 템포 | **{r['bpm']} BPM**{alt} · 박 검출 신뢰도 {r['beat_confidence']} |
| 키 | **{r['key']} {r['scale']}** ({KEY_KO.get(r['scale'], r['scale'])}) · 확신도 {r['key_strength']} |
| 박자 | {r['meter']['label_ko']} |
| 음량 | {r['loudness_lufs']} LUFS · 다이내믹 레인지 {r['loudness_range_lu']} LU |
| 보컬 | {'있음' if voice.get('voice', 0) >= 0.5 else '거의 없음 (연주곡)'} ({voice.get('voice', 0):.2f}) · {t['gender'][0][0]} 쪽 {t['gender'][0][1]:.2f} |
| 춤추기 좋은 정도 | {dance.get('danceable', 0):.2f} |

## 장르·스타일 (상위 8)
| 스타일 | 점수 |
|---|---|
{rows(t['genre'], 8)}

## 악기 (상위 8)
| 악기 | 점수 |
|---|---|
{rows(t['instrument'], 8)}

## 분위기·테마 (상위 8)
| 분위기·테마 | 점수 |
|---|---|
{rows(t['moodtheme'], 8)}

## 곡 구조 (구간 추정)
{seg_md}

## 수노 스타일 프롬프트 초안
```
{prompt}
```

> 점수는 0~1 사이의 모델 추정치예요. 장르·분위기는 곡 전체 평균이라 구간별로 다를 수 있어요.
> 박자는 저음 강세 패턴으로 추정한 값이라 틀릴 수 있어요. 가수·곡 이름은 수노에 넣지 마세요.
"""
    return md


def main() -> None:
    ap = argparse.ArgumentParser(description="레퍼런스 곡 스타일 분석 (Essentia)")
    ap.add_argument("audio", help="분석할 곡 파일 (mp3, wav, m4a, flac 등)")
    ap.add_argument("--out", help="결과 저장 폴더 (기본: 곡 파일과 같은 폴더)")
    ap.add_argument("--no-structure", action="store_true", help="곡 구조 분석 건너뛰기")
    args = ap.parse_args()

    check_models()
    path = str(Path(args.audio).resolve())
    if not Path(path).exists():
        sys.exit(f"파일이 없습니다: {path}")

    print("[1/3] 템포·키·박자 분석 중...", file=sys.stderr)
    r = rhythm_and_key(path)
    print("[2/3] 장르·악기·분위기 분석 중...", file=sys.stderr)
    t = tag_models(path)
    prompt = build_prompt(r, t)
    print("[3/3] 곡 구조 분석 중...", file=sys.stderr)
    segs = [] if args.no_structure else structure(path)

    stem = Path(path).stem
    out_dir = Path(args.out) if args.out else Path(path).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    md = to_markdown(Path(path).name, r, t, prompt, segs)
    beats = r.pop("_beats")
    data = {"file": Path(path).name, "rhythm_key": r, "beats_sec": beats,
            "tags": {k: v[:20] for k, v in t.items()}, "structure": segs, "suno_style_prompt": prompt}
    (out_dir / f"{stem}_analysis.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))
    (out_dir / f"{stem}_analysis.md").write_text(md)
    print(md)
    print(f"\n저장: {out_dir / (stem + '_analysis.md')}", file=sys.stderr)


if __name__ == "__main__":
    main()
