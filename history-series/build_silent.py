#!/usr/bin/env python3
"""내레이션 없는(음악·효과음·자막) 버전 편집기.

    python3 build_silent.py episodes/kr01_gojoseon_silent.json [--preview]

- work/<id>/img/sNN.png : 장면 이미지 (JSON 의 "img" 번호)
- work/<id>/music.mp3 (또는 .wav) : 배경음악. 있으면 박자를 분석해 장면 전환을 마디에 맞춘다.
  없으면 JSON 의 bpm 으로 박자 격자를 만들고 임시 합성 음악을 쓴다.
"""
import argparse
import json
import math
import os
import subprocess
import wave
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import gaussian_filter
from scipy.signal import butter, lfilter

import build_episode as be

HERE = be.HERE
W, H, FPS, SR = be.W, be.H, be.FPS, be.SR
XF = 0.8  # 전환 길이


# ------------------------------------------------------------ 박자 격자

def beat_grid(ep, workdir):
    music = None
    for ext in ("mp3", "wav", "m4a"):
        p = os.path.join(workdir, f"music.{ext}")
        if os.path.exists(p):
            music = p
    if music:
        import librosa
        y, sr = librosa.load(music, sr=22050, mono=True)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time")
        tempo = float(np.atleast_1d(tempo)[0])
        bar = 4 * 60 / tempo
        first = float(beats[0]) if len(beats) else 0.0
        return music, tempo, bar, first, len(y) / sr
    tempo = ep.get("bpm", 90)
    return None, tempo, 4 * 60 / tempo, 0.0, None


def reading_bars(sc, bar):
    if "bars" in sc:
        return sc["bars"]
    n = len(sc.get("sub", "").replace("\n", "").replace(" ", ""))
    need = max(4.6, n / 7.0 + 1.6)
    return max(1, math.ceil(need / bar - 0.15))


def build_timeline(ep, workdir):
    music, tempo, bar, first, mlen = beat_grid(ep, workdir)
    t = first if first < bar else 0.0
    tl = []
    for i, sc in enumerate(ep["scenes"]):
        nb = reading_bars(sc, bar)
        dur = nb * bar
        # 전환이 마디선 가운데에 오도록 앞뒤로 XF/2 씩 겹침
        tl.append(dict(i=i, start=max(0.0, t - XF / 2), end=t + dur + XF / 2, cut=t))
        t += dur
    total = t + 2.5  # 마지막 여운
    tl[-1]["end"] = total
    return dict(tl=tl, total=total, music=music, tempo=tempo, bar=bar)


# ------------------------------------------------------------ 그래픽

def era_layer(era, ow, oh):
    s = ow / W
    img = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(be.FONT_B, int(34 * s), index=be.KR)
    x, y = int(70 * s), int(56 * s)
    # 반투명 먹 띠 위에 한지색 글자
    bb = d.textbbox((x, y), era, font=f)
    pad = int(14 * s)
    bg = Image.new("L", (ow, oh), 0)
    ImageDraw.Draw(bg).rectangle([bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad], fill=255)
    bg = bg.filter(ImageFilter.GaussianBlur(10 * s))
    a_bg = np.asarray(bg, np.float32) / 255 * 0.55
    d.text((x, y), era, font=f, fill=(244, 236, 220, 255))
    d.line([(x, bb[3] + int(10 * s)), (x + int(60 * s), bb[3] + int(10 * s))], fill=be.SEAL_RGB + (255,), width=max(2, int(4 * s)))
    a = np.asarray(img, np.float32) / 255
    out = np.zeros_like(a)
    alpha = a[..., 3] + a_bg * (1 - a[..., 3])
    out[..., :3] = a[..., :3] * a[..., 3:4] / np.maximum(alpha[..., None], 1e-4)
    out[..., 3] = alpha
    return out


def paper(ow, oh, seed=5):
    n = be.fbm(oh, ow, seed, 6, 6)
    base = np.array([238, 222, 190], np.float32) / 255
    stains = gaussian_filter(np.random.default_rng(seed).random((oh, ow)).astype(np.float32), 30)
    stains = (stains - stains.min()) / (stains.max() - stains.min())
    return base[None, None, :] * (0.88 + 0.12 * n[..., None]) * (0.95 + 0.08 * stains[..., None])


def chapter_frame(sc, ow, oh, seal, next_img=None, workdir=None):
    s = ow / W
    bg = paper(ow, oh, 11)
    if next_img is not None:
        # 다음 장면 그림을 흐리고 옅게 깔아 시리즈 톤을 유지
        im = be.load_scene_image(next_img, {"prompt": ""}, workdir).resize((ow, oh), Image.LANCZOS)
        im = im.filter(ImageFilter.GaussianBlur(6 * s))
        a = np.asarray(im, np.float32) / 255
        bg = bg * 0.72 + a * 0.28
    img = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f1 = ImageFont.truetype(be.FONT_R, int(40 * s), index=be.KR)
    f2 = ImageFont.truetype(be.FONT_B, int(120 * s), index=be.KR)
    cx = ow // 2
    for txt, f, y, col in ((sc["num"], f1, 380, (150, 40, 34, 255)), (sc["name"], f2, 450, (24, 20, 18, 255))):
        bb = d.textbbox((0, 0), txt, font=f)
        d.text((cx - (bb[2] - bb[0]) // 2 - bb[0], int(y * s)), txt, font=f, fill=col)
    # 붓 획 밑줄
    r = np.random.default_rng(3)
    for k in range(40):
        yy = int(640 * s) + int(r.normal(0, 3 * s))
        x0 = cx - int(170 * s) + int(r.normal(0, 6 * s))
        d.line([(x0, yy), (x0 + int(340 * s * r.uniform(0.85, 1)), yy + int(r.normal(0, 2 * s)))],
               fill=(30, 26, 24, int(r.uniform(10, 40))), width=max(1, int(6 * s)))
    a = np.asarray(img, np.float32) / 255
    fr = bg * (1 - a[..., 3:4]) + a[..., :3] * a[..., 3:4]
    ss = int(70 * s)
    sl = np.asarray(be.seal_image(seal, ss), np.float32) / 255
    sx, sy = cx + int(230 * s), int(560 * s)
    reg = fr[sy:sy + ss, sx:sx + ss]
    reg[:] = sl[..., :3] * sl[..., 3:4] + reg * (1 - sl[..., 3:4])
    return fr.astype(np.float32)


# ------------------------------------------------------------ 렌더
G = {}


def init_worker(ep_path, workdir, ow, oh):
    ep = json.load(open(ep_path))
    info = build_timeline(ep, workdir)
    # 연도 표시는 앞 장면 값을 이어받는다
    era = None
    eras = []
    for sc in ep["scenes"]:
        if sc.get("chapter") or sc.get("title_card"):
            eras.append(None)
            continue
        era = sc.get("era", era)
        eras.append(era)
    G.update(ep=ep, info=info, tl=info["tl"], workdir=workdir, ow=ow, oh=oh, cache={}, eras=eras, era_cache={})
    G["grain"] = (0.93 + 0.1 * be.fbm(oh, ow, 99, 6, 8))[..., None].astype(np.float32)
    G["ink"] = be.fbm(oh, ow, 123, 5, 3).astype(np.float32)
    yy, xx = np.mgrid[0:oh, 0:ow].astype(np.float32)
    G["vign"] = (1 - 0.28 * (((xx - ow / 2) / (ow / 2)) ** 2 + ((yy - oh / 2) / (oh / 2)) ** 2) ** 1.3)[..., None]


def res(i):
    c = G["cache"]
    if i not in c:
        if len(c) > 3:
            c.pop(next(iter(c)))
        sc = G["ep"]["scenes"][i]
        if sc.get("chapter"):
            nxt = next((x.get("img") for x in G["ep"]["scenes"][i + 1:] if "img" in x), None)
            c[i] = ("chapter", chapter_frame(sc, G["ow"], G["oh"], G["ep"]["seal"], nxt, G["workdir"]))
        else:
            src = be.load_scene_image(sc["img"], {"prompt": ""}, G["workdir"])
            sub = be.subtitle_layer(sc.get("sub", ""), G["ep"]["seal"], G["ow"], G["oh"])
            title = be.title_layer(G["ep"], G["ow"], G["oh"]) if sc.get("title_card") else None
            c[i] = ("img", src, sub, title)
    return c[i]


def era_img(text):
    if text not in G["era_cache"]:
        G["era_cache"][text] = era_layer(text, G["ow"], G["oh"])
    return G["era_cache"][text]


def scene_rgb(i, t):
    seg = G["tl"][i]
    dur = seg["end"] - seg["start"]
    r = res(i)
    if r[0] == "chapter":
        z = 1 + 0.04 * (t / dur)
        fr = r[1]
        if z > 1.001:
            im = Image.fromarray((fr * 255).astype(np.uint8))
            w, h = im.size
            cw, ch = w / z, h / z
            im = im.resize((w, h), Image.BILINEAR, box=((w - cw) / 2, (h - ch) / 2, (w + cw) / 2, (h + ch) / 2))
            fr = np.asarray(im, np.float32) / 255
        return fr
    _, src, sub, title = r
    frame = np.asarray(be.kb_frame(src, t / dur, be.MOVES[i % len(be.MOVES)], G["ow"], G["oh"]), np.float32) / 255
    sa = be.smooth((t - XF / 2 - 0.3) / 0.5) * be.smooth((dur - XF / 2 - t) / 0.4)
    if sa > 0 and sub[..., 3].max() > 0:
        a = sub[..., 3:4] * sa
        frame = frame * (1 - a) + sub[..., :3] * a
    era = G["eras"][i]
    if era:
        prev = G["eras"][i - 1] if i > 0 else None
        ea = 1.0 if prev == era else be.smooth((t - XF / 2) / 0.6)
        e = era_img(era)
        a = e[..., 3:4] * ea
        frame = frame * (1 - a) + e[..., :3] * a
    if title is not None:
        ta = be.smooth((t - 0.6) / 0.9)
        a = title[..., 3:4] * ta
        frame = frame * (1 - a) + title[..., :3] * a
    return frame


def render(k):
    t = k / FPS
    tl = G["tl"]
    cur = [s for s in tl if s["start"] <= t < s["end"]] or [tl[-1]]
    if len(cur) == 1:
        fr = scene_rgb(cur[0]["i"], t - cur[0]["start"])
    else:
        a, b = cur[0], cur[1]
        fa = scene_rgb(a["i"], t - a["start"])
        fb = scene_rgb(b["i"], t - b["start"])
        p = (t - b["start"]) / XF
        m = be.smooth(np.clip(p * 1.4 - G["ink"] * 0.4, 0, 1))[..., None]
        fr = fa * (1 - m) + fb * m
    total = G["info"]["total"]
    fade = min(be.smooth(t / 0.4), be.smooth((total - t) / 2.0))
    fr = fr * G["grain"] * G["vign"] * fade
    return (np.clip(fr, 0, 1) * 255).astype(np.uint8).tobytes()


# ------------------------------------------------------------ 효과음

def _bp(x, lo, hi):
    b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], btype="band")
    return lfilter(b, a, x).astype(np.float32)


def sfx(kind, dur, seed):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = r.standard_normal(n).astype(np.float32)
    if kind == "wind":
        lfo = 0.5 + 0.5 * np.sin(2 * np.pi * t / r.uniform(3, 6) + r.uniform(0, 6))
        return _bp(noise, 200, 900) * (0.25 + 0.75 * lfo) * 0.5
    if kind == "fire":
        base = _bp(noise, 300, 3000) * 0.18
        pops = np.zeros(n, np.float32)
        for _ in range(int(dur * 14)):
            s = int(r.uniform(0, n - 400))
            L = int(r.uniform(60, 300))
            pops[s:s + L] += r.standard_normal(L) * np.exp(-np.arange(L) / (L / 4)) * r.uniform(0.3, 1)
        rumble = _bp(noise, 40, 160) * 0.6
        return base + _bp(pops, 1000, 6000) * 0.5 + rumble
    if kind == "drip":
        out = _bp(noise, 100, 400) * 0.08
        for k in range(int(dur / 1.3)):
            s = int((0.4 + k * 1.3 + r.uniform(-0.2, 0.2)) * SR)
            L = int(0.25 * SR)
            tt = np.arange(L) / SR
            f = r.uniform(900, 1500) * (1 + 0.8 * np.exp(-tt * 30))
            d = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 25) * 0.5
            out[s:s + L] += d[:max(0, n - s)]
        return out
    if kind == "forge":
        out = _bp(noise, 80, 400) * 0.2
        for k in range(int(dur / 0.9)):
            s = int((0.3 + k * 0.9) * SR)
            L = int(0.6 * SR)
            tt = np.arange(L) / SR
            ring = sum(np.sin(2 * np.pi * f * tt) * a for f, a in ((1830, 0.5), (2710, 0.35), (4120, 0.2)))
            hit = (ring * np.exp(-tt * 9) + r.standard_normal(L) * np.exp(-tt * 80)) * 0.35
            out[s:s + L] += hit[:max(0, n - s)]
        return out
    if kind == "crowd":
        out = np.zeros(n, np.float32)
        for k in range(10):
            env = gaussian_filter(np.abs(r.standard_normal(n // 400 + 1)), 3)
            env = np.repeat(env, 400)[:n]
            out += _bp(r.standard_normal(n).astype(np.float32), r.uniform(250, 500), r.uniform(900, 1600)) * env
        return out * 0.15
    if kind == "water":
        lfo = 0.5 + 0.5 * np.sin(2 * np.pi * t / 4.0)
        return (_bp(noise, 150, 1200) * (0.4 + 0.6 * lfo) + _bp(noise, 2000, 6000) * 0.15) * 0.4
    if kind == "drums":
        out = np.zeros(n, np.float32)
        hit = be.drum()
        step = 60 / G_AUDIO["tempo"]
        k = 0
        while k * step < dur:
            s = int(k * step * SR)
            amp = 0.5 if k % 4 == 0 else 0.25
            out[s:s + len(hit)] += hit[:max(0, n - s)] * amp
            k += 1
        return out * 0.5
    if kind == "forest":
        out = _bp(noise, 200, 800) * 0.12
        for k in range(int(dur * 0.8)):
            s = int(r.uniform(0, n - SR))
            L = int(0.15 * SR)
            tt = np.arange(L) / SR
            f = r.uniform(3000, 4500) + 600 * np.sin(2 * np.pi * 18 * tt)
            out[s:s + L] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / tt[-1]) * 0.12
        return out
    if kind == "room":
        return _bp(noise, 60, 300) * 0.12
    return np.zeros(n, np.float32)


G_AUDIO = {}


def build_audio(ep, info, path):
    G_AUDIO["tempo"] = info["tempo"]
    total = info["total"]
    n = int(total * SR)
    if info["music"]:
        music = be.load_wav(info["music"])[:n]
        music = np.pad(music, (0, n - len(music)))
        music /= np.abs(music).max() + 1e-6
    else:
        music = be.bgm(total)[:n] * 0.8
    fx = np.zeros(n, np.float32)
    hits = np.zeros(n, np.float32)
    duck = np.ones(n, np.float32)
    boom = be.drum()
    for seg, sc in zip(info["tl"], ep["scenes"]):
        s, e = int(seg["start"] * SR), int(seg["end"] * SR)
        kind = sc.get("sfx")
        if kind and kind != "silence":
            x = sfx(kind, (e - s) / SR, seg["i"] + 17)
            ramp = np.minimum(1, np.minimum(np.arange(len(x)) / (0.5 * SR), (len(x) - np.arange(len(x))) / (0.5 * SR)))
            fx[s:s + len(x)] += (x * ramp)[:max(0, n - s)]
        if kind == "silence":  # 음악을 잠시 비워 긴장감
            L = e - s
            env = 1 - 0.85 * np.sin(np.pi * np.arange(L) / L) ** 0.5
            duck[s:e] *= env[:len(duck[s:e])]
        if sc.get("impact"):
            c = int(seg["cut"] * SR)
            hits[c:c + len(boom)] += boom[:max(0, n - c)] * 0.9
    fx /= np.abs(fx).max() + 1e-6
    mix = music * duck * 0.75 + fx * 0.22 + hits * 0.45
    fade = np.minimum(1, (n - np.arange(n)) / (2.5 * SR))
    mix *= fade
    mix /= np.abs(mix).max() + 1e-6
    pcm = (mix * 0.92 * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 2)
    a = ap.parse_args()
    ep = json.load(open(a.episode))
    workdir = os.path.join(HERE, "work", ep["id"])
    info = build_timeline(ep, workdir)
    sc = 0.5 if a.preview else 1.0
    ow, oh = int(W * sc) // 2 * 2, int(H * sc) // 2 * 2
    out = a.out or os.path.join(HERE, "out", f"{ep['id']}_silent{'_preview' if a.preview else ''}.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    print(f"{ep['id']} 무음판: 장면 {len(info['tl'])}개, {info['total']:.1f}초, "
          f"템포 {info['tempo']:.1f} BPM, 음악={'있음' if info['music'] else '임시 합성'}", flush=True)
    wav = os.path.join(workdir, "_mix_silent.wav")
    build_audio(ep, info, wav)
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ow}x{oh}", "-r", str(FPS), "-i", "-", "-i", wav,
        "-c:v", "libx264", "-preset", "veryfast" if a.preview else "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    nfr = int(info["total"] * FPS)
    with Pool(a.workers, initializer=init_worker, initargs=(a.episode, workdir, ow, oh)) as pool:
        for k, b in enumerate(pool.imap(render, range(nfr), chunksize=8)):
            ff.stdin.write(b)
            if k % (FPS * 20) == 0:
                print(f"  {k / FPS:5.0f}s / {info['total']:.0f}s", flush=True)
    ff.stdin.close()
    ff.wait()
    print("완료:", out)


if __name__ == "__main__":
    main()
