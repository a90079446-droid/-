#!/usr/bin/env python3
"""에피소드 JSON + 장면 이미지 + (선택) 장면별 내레이션 → 완성 영상.

폴더 구조 (예: kr01):
    episodes/kr01_gojoseon.json
    work/kr01/img/s00.png ...  (장면 이미지, 없으면 자리표시 이미지 사용)
    work/kr01/voice/s00.wav ... (장면 내레이션, 없으면 글자 수로 길이 추정)

    python3 build_episode.py episodes/kr01_gojoseon.json            # 1080p
    python3 build_episode.py episodes/kr01_gojoseon.json --preview  # 540p 빠른 확인
"""
import argparse
import json
import math
import os
import subprocess
import sys
import wave
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import gaussian_filter, zoom as nd_zoom

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_B = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
FONT_R = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
KR, TC = 1, 3
W, H = 1920, 1080
FPS = 24
XFADE = 0.9          # 장면 전환 길이(초)
LEAD = 0.35          # 장면 시작 후 내레이션이 시작되기까지
TAIL = 0.75          # 내레이션 끝난 뒤 여유
MIN_SCENE = 4.2
SR = 44100
SEAL_RGB = (178, 40, 34)

# ------------------------------------------------------------------ util


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def fbm(h, w, seed, octaves=5, base=4):
    r = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp = tot = 0.0
    amp = 1.0
    for o in range(octaves):
        gh, gw = base * 2 ** o + 1, int(base * 2 ** o * w / h) + 1
        g = r.random((gh, gw)).astype(np.float32)
        up = nd_zoom(g, (h / gh, w / gw), order=1)[:h, :w]
        up = np.pad(up, ((0, h - up.shape[0]), (0, w - up.shape[1])), mode="edge")
        out += amp * up
        tot += amp
        amp *= 0.55
    out /= tot
    return (out - out.min()) / (out.max() - out.min() + 1e-6)


def wav_len(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def load_wav(path):
    """어떤 형식이든 ffmpeg 로 44.1k mono float 로 읽는다."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


# ------------------------------------------------------------ timeline


def build_timeline(ep, workdir):
    scenes = ep["scenes"]
    tl = []
    t = 0.0
    for i, sc in enumerate(scenes):
        vpath = None
        for ext in ("wav", "mp3"):
            p = os.path.join(workdir, "voice", f"s{i:02d}.{ext}")
            if os.path.exists(p):
                vpath = p
        if sc.get("title_card"):
            dur = sc.get("hold", 4.0)
            vlen = 0
        elif vpath:
            vlen = len(load_wav(vpath)) / SR
            dur = max(MIN_SCENE, LEAD + vlen + TAIL)
        else:
            vlen = len(sc["narr"].replace(" ", "")) / 6.8  # 한국어 약 6.8음절/초
            dur = max(MIN_SCENE, LEAD + vlen + TAIL)
        tl.append(dict(i=i, start=t, dur=dur + XFADE, voice=vpath, vlen=vlen))
        t += dur
    total = t + XFADE
    return tl, total


# ------------------------------------------------------------ graphics


def placeholder(i, sc):
    img = Image.new("RGB", (W, H), (205, 196, 178))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_R, 30, index=KR)
    d.text((80, 80), f"[장면 {i:02d} 자리표시]", font=f, fill=(60, 55, 50))
    y = 140
    words = sc["prompt"].split()
    line = ""
    for w_ in words:
        if len(line) + len(w_) > 80:
            d.text((80, y), line, font=f, fill=(90, 85, 80)); y += 44; line = ""
        line += w_ + " "
    d.text((80, y), line, font=f, fill=(90, 85, 80))
    return img


def load_scene_image(i, sc, workdir):
    for ext in ("png", "jpg", "jpeg", "webp"):
        p = os.path.join(workdir, "img", f"s{i:02d}.{ext}")
        if os.path.exists(p):
            im = Image.open(p).convert("RGB")
            break
    else:
        im = placeholder(i, sc)
    # 16:9 로 채우고 켄 번스 여유를 위해 1.15배 크게
    S = 1.15
    tw, th = int(W * S), int(H * S)
    r = max(tw / im.width, th / im.height)
    im = im.resize((math.ceil(im.width * r), math.ceil(im.height * r)), Image.LANCZOS)
    x0, y0 = (im.width - tw) // 2, (im.height - th) // 2
    return im.crop((x0, y0, x0 + tw, y0 + th))


MOVES = [  # (시작 줌, 끝 줌, 시작 중심, 끝 중심) 중심은 0..1
    (1.00, 1.10, (0.5, 0.5), (0.5, 0.45)),
    (1.10, 1.00, (0.45, 0.5), (0.55, 0.5)),
    (1.04, 1.12, (0.6, 0.55), (0.4, 0.5)),
    (1.12, 1.04, (0.5, 0.6), (0.5, 0.4)),
    (1.02, 1.08, (0.4, 0.45), (0.6, 0.55)),
]


def kb_frame(src, p, move, out_w, out_h):
    z0, z1, c0, c1 = move
    e = smooth(p) * 0.6 + p * 0.4
    z = z0 + (z1 - z0) * e
    cx = c0[0] + (c1[0] - c0[0]) * e
    cy = c0[1] + (c1[1] - c0[1]) * e
    sw, sh = src.size
    cw, ch = sw / 1.15 / z * 1.0, sh / 1.15 / z
    cw, ch = min(cw, sw), min(ch, sh)
    x0 = np.clip(cx * sw - cw / 2, 0, sw - cw)
    y0 = np.clip(cy * sh - ch / 2, 0, sh - ch)
    return src.resize((out_w, out_h), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


def text_with_shadow(size, lines, font, fill=(245, 240, 232), spacing=14, shadow=10):
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    return layer, d


def subtitle_layer(sub, seal, out_w, out_h):
    s = out_w / W
    img = Image.new("RGBA", (out_w, out_h), (0, 0, 0, 0))
    if not sub:
        return np.zeros((out_h, out_w, 4), np.float32)
    f = ImageFont.truetype(FONT_B, int(44 * s), index=KR)
    lines = sub.split("\n")
    lh = int(64 * s)
    y0 = out_h - int(80 * s) - lh * len(lines)
    mask = Image.new("L", (out_w, out_h), 0)
    md = ImageDraw.Draw(mask)
    txt = Image.new("L", (out_w, out_h), 0)
    td = ImageDraw.Draw(txt)
    for k, ln in enumerate(lines):
        bb = td.textbbox((0, 0), ln, font=f)
        x = (out_w - (bb[2] - bb[0])) // 2 - bb[0]
        td.text((x, y0 + k * lh), ln, font=f, fill=255)
    # 그림자: 번진 먹빛 띠
    sh = txt.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(14 * s))
    a_sh = np.asarray(sh, np.float32) / 255 * 0.85
    a_tx = np.asarray(txt, np.float32) / 255
    rgba = np.zeros((out_h, out_w, 4), np.float32)
    # 그림자(검정) 위에 글자(흰색) 합성 → premultiplied 로 저장
    col = np.array([246, 241, 232], np.float32) / 255
    alpha = a_tx + a_sh * (1 - a_tx)
    rgb = (col[None, None, :] * a_tx[..., None]) / np.maximum(alpha[..., None], 1e-4)
    rgba[..., :3] = rgb
    rgba[..., 3] = alpha
    # 자막 오른쪽 아래 작은 낙관
    if seal:
        ss = int(46 * s)
        last = lines[-1]
        bb = td.textbbox((0, 0), last, font=f)
        sx = (out_w + (bb[2] - bb[0])) // 2 + int(26 * s)
        sy = y0 + (len(lines) - 1) * lh + int(6 * s)
        sl = seal_image(seal, ss)
        sa = np.asarray(sl, np.float32) / 255
        h_, w_ = sa.shape[:2]
        reg = rgba[sy:sy + h_, sx:sx + w_]
        a2 = sa[..., 3:4]
        reg[..., :3] = sa[..., :3] * a2 + reg[..., :3] * (1 - a2)
        reg[..., 3:4] = a2 + reg[..., 3:4] * (1 - a2)
    return rgba


def seal_image(ch, size):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=max(2, size // 10), fill=SEAL_RGB + (235,))
    f = ImageFont.truetype(FONT_B, int(size * 0.68), index=TC)
    bb = d.textbbox((0, 0), ch, font=f)
    d.text(((size - (bb[2] - bb[0])) / 2 - bb[0], (size - (bb[3] - bb[1])) / 2 - bb[1]), ch, font=f,
           fill=(242, 230, 212, 255))
    a = np.asarray(im).astype(np.float32)
    worn = fbm(size, size, 7, 4, 3)
    a[..., 3] *= np.clip((worn - 0.2) * 3, 0, 1)
    return Image.fromarray(a.astype(np.uint8))


def title_layer(ep, out_w, out_h):
    s = out_w / W
    img = Image.new("RGBA", (out_w, out_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f_series = ImageFont.truetype(FONT_R, int(34 * s), index=KR)
    f_title = ImageFont.truetype(FONT_B, int(150 * s), index=KR)
    f_sub = ImageFont.truetype(FONT_R, int(40 * s), index=KR)
    cx = out_w // 2

    def ctext(y, t, f, fill):
        bb = d.textbbox((0, 0), t, font=f)
        d.text((cx - (bb[2] - bb[0]) // 2 - bb[0], y), t, font=f, fill=fill)
        return bb
    ctext(int(330 * s), ep["series"], f_series, (40, 34, 30, 255))
    bb = ctext(int(390 * s), ep["title"], f_title, (20, 18, 16, 255))
    ctext(int(610 * s), ep["subtitle"], f_sub, (40, 34, 30, 255))
    a = np.asarray(img, np.float32) / 255
    # 글자 뒤 한지빛 후광
    glow = Image.fromarray((a[..., 3] * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(15)).filter(
        ImageFilter.GaussianBlur(40 * s))
    g = np.asarray(glow, np.float32) / 255 * 0.85
    out = np.zeros_like(a)
    paper = np.array([236, 226, 205], np.float32) / 255
    alpha = a[..., 3] + g * (1 - a[..., 3])
    out[..., :3] = (a[..., :3] * a[..., 3:4] + paper * g[..., None] * (1 - a[..., 3:4])) / np.maximum(alpha[..., None], 1e-4)
    out[..., 3] = alpha
    # 큰 낙관
    ss = int(90 * s)
    sl = np.asarray(seal_image(ep["seal"], ss), np.float32) / 255
    bbw = bb[2] - bb[0]
    sx, sy = cx + bbw // 2 + int(30 * s), int(470 * s)
    reg = out[sy:sy + ss, sx:sx + ss]
    a2 = sl[..., 3:4]
    reg[..., :3] = sl[..., :3] * a2 + reg[..., :3] * (1 - a2)
    reg[..., 3:4] = a2 + reg[..., 3:4] * (1 - a2)
    return out


# ------------------------------------------------------------- render
G = {}


def init_worker(ep_path, workdir, out_w, out_h):
    ep = json.load(open(ep_path))
    tl, total = build_timeline(ep, workdir)
    G.update(ep=ep, tl=tl, workdir=workdir, ow=out_w, oh=out_h, cache={})
    grain = fbm(out_h, out_w, 99, 6, 8)
    G["grain"] = (0.93 + 0.1 * grain)[..., None].astype(np.float32)
    G["ink_noise"] = fbm(out_h, out_w, 123, 5, 3).astype(np.float32)
    yy, xx = np.mgrid[0:out_h, 0:out_w].astype(np.float32)
    G["vign"] = (1 - 0.28 * (((xx - out_w / 2) / (out_w / 2)) ** 2 + ((yy - out_h / 2) / (out_h / 2)) ** 2) ** 1.3)[..., None]


def scene_res(i):
    c = G["cache"]
    if i not in c:
        if len(c) > 3:
            c.pop(next(iter(c)))
        sc = G["ep"]["scenes"][i]
        src = load_scene_image(i, sc, G["workdir"])
        sub = subtitle_layer(sc.get("sub", ""), G["ep"]["seal"], G["ow"], G["oh"])
        title = title_layer(G["ep"], G["ow"], G["oh"]) if sc.get("title_card") else None
        c[i] = (src, sub, title)
    return c[i]


def scene_rgb(i, t_local):
    sc = G["ep"]["scenes"][i]
    seg = G["tl"][i]
    src, sub, title = scene_res(i)
    p = t_local / seg["dur"]
    frame = np.asarray(kb_frame(src, p, MOVES[i % len(MOVES)], G["ow"], G["oh"]), np.float32) / 255
    # 자막: 장면 시작 0.5초 후 부드럽게, 끝 0.4초 전 사라짐
    sa = smooth((t_local - 0.5) / 0.4) * smooth((seg["dur"] - XFADE - t_local + 0.1) / 0.35)
    if sa > 0 and sub[..., 3].max() > 0:
        a = sub[..., 3:4] * sa
        frame = frame * (1 - a) + sub[..., :3] * a
    if title is not None:
        ta = smooth((t_local - 0.4) / 0.8)
        a = title[..., 3:4] * ta
        frame = frame * (1 - a) + title[..., :3] * a
    return frame


def render(k):
    t = k / FPS
    tl = G["tl"]
    cur = [s for s in tl if s["start"] <= t < s["start"] + s["dur"]]
    if not cur:
        cur = [tl[-1]]
    if len(cur) == 1:
        frame = scene_rgb(cur[0]["i"], t - cur[0]["start"])
    else:
        a, b = cur[0], cur[1]
        fa = scene_rgb(a["i"], t - a["start"])
        fb = scene_rgb(b["i"], t - b["start"])
        p = (t - b["start"]) / XFADE
        # 먹 번짐 전환: 노이즈 문턱으로 번지듯 바뀜
        m = np.clip((p * 1.4 - G["ink_noise"] * 0.4) / 1.0, 0, 1)
        m = smooth(m)[..., None]
        frame = fa * (1 - m) + fb * m
    total = tl[-1]["start"] + tl[-1]["dur"]
    fade = min(smooth(t / 0.6), smooth((total - t) / 1.5))
    frame = frame * G["grain"] * G["vign"] * fade
    return (np.clip(frame, 0, 1) * 255).astype(np.uint8).tobytes()


# -------------------------------------------------------------- audio


def bgm(total, seed=7):
    """잔잔한 가야금풍 뜯기 + 저음 지속음 (약 99 BPM 박에 맞춤)."""
    r = np.random.default_rng(seed)
    n = int((total + 6) * SR)
    out = np.zeros(n, np.float32)
    t = np.arange(n) / SR
    out += (0.05 * np.sin(2 * np.pi * 73.42 * t) + 0.03 * np.sin(2 * np.pi * 110 * t)) * (
        0.6 + 0.4 * np.sin(2 * np.pi * t / 13))
    scale = [146.83, 174.61, 196.0, 220.0, 261.63, 293.66, 349.23, 392.0]
    beat = 60 / 99

    def pluck(f, dur, amp):
        N = int(SR / f)
        L = int(dur * SR)
        buf = gaussian_filter(r.uniform(-1, 1, N).astype(np.float32), 1.0)
        reps = L // N + 1
        # 벡터화된 근사 Karplus-Strong: 주기마다 저역 통과 + 감쇠
        y = np.empty(reps * N, np.float32)
        for k in range(reps):
            y[k * N:(k + 1) * N] = buf
            buf = 0.996 * 0.5 * (buf + np.roll(buf, -1))
        y = y[:L]
        return y * np.exp(-np.arange(L) / (SR * dur * 0.35)) * amp

    pos = 1.0
    while pos < total:
        f = scale[int(r.integers(len(scale)))]
        s = int(pos * SR)
        note = pluck(f, 3.2, r.uniform(0.15, 0.26))
        out[s:s + len(note)] += note[:max(0, n - s)]
        pos += beat * r.choice([2, 3, 4])
    from scipy.signal import fftconvolve
    ir_len = int(2.5 * SR)
    ir = r.standard_normal(ir_len).astype(np.float32) * np.exp(-np.arange(ir_len) / (SR * 0.6))
    ir /= np.sqrt((ir ** 2).sum())
    out = 0.7 * out + 0.4 * fftconvolve(out, ir)[:n]
    return out / (np.abs(out).max() + 1e-6)


def drum(seed=3):
    """전환점용 낮은 북 + 징."""
    L = int(3.5 * SR)
    t = np.arange(L) / SR
    f = 55 * np.exp(-t * 3) + 45
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4)
    gong = (np.sin(2 * np.pi * 196 * t) + 0.6 * np.sin(2 * np.pi * 196 * 2.4 * t) +
            0.3 * np.sin(2 * np.pi * 196 * 3.9 * t)) * np.exp(-t * 1.1) * 0.25
    return (boom + gong).astype(np.float32)


def build_audio(ep, tl, total, path):
    n = int(total * SR)
    voice = np.zeros(n, np.float32)
    for seg in tl:
        if seg["voice"]:
            v = load_wav(seg["voice"])
            s = int((seg["start"] + LEAD) * SR)
            voice[s:s + len(v)] += v[:max(0, n - s)]
    music = bgm(total)[:n]
    # 내레이션이 나올 때 음악을 낮춤 (덕킹)
    env = gaussian_filter((np.abs(voice) > 0.01).astype(np.float32), SR * 0.25)
    env = np.clip(env * 4, 0, 1)
    music *= (0.32 - 0.20 * env)
    hit = drum()
    for k in ep.get("impacts", []):
        s = int(tl[k]["start"] * SR)
        music[s:s + len(hit)] += hit[:max(0, n - s)] * 0.5
    mix = voice + music
    mix /= np.abs(mix).max() + 1e-6
    pcm = (mix * 0.9 * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


# --------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 2)
    a = ap.parse_args()
    ep = json.load(open(a.episode))
    workdir = os.path.join(HERE, "work", ep["id"])
    os.makedirs(workdir, exist_ok=True)
    tl, total = build_timeline(ep, workdir)
    sc = 0.5 if a.preview else 1.0
    ow, oh = int(W * sc) // 2 * 2, int(H * sc) // 2 * 2
    out = a.out or os.path.join(HERE, "out", f"{ep['id']}{'_preview' if a.preview else ''}.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    print(f"{ep['id']} {ep['title']}: 장면 {len(tl)}개, {total:.1f}초", flush=True)
    wav = os.path.join(workdir, "_mix.wav")
    build_audio(ep, tl, total, wav)
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ow}x{oh}", "-r", str(FPS), "-i", "-",
        "-i", wav,
        "-c:v", "libx264", "-preset", "veryfast" if a.preview else "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    nfr = int(total * FPS)
    with Pool(a.workers, initializer=init_worker, initargs=(a.episode, workdir, ow, oh)) as pool:
        for k, b in enumerate(pool.imap(render, range(nfr), chunksize=8)):
            ff.stdin.write(b)
            if k % (FPS * 15) == 0:
                print(f"  {k / FPS:5.0f}s / {total:.0f}s", flush=True)
    ff.stdin.close()
    ff.wait()
    print("완료:", out)


if __name__ == "__main__":
    main()
