#!/usr/bin/env python3
"""수묵화 역사 영상 생성기

모든 그림(산수·대나무·소나무·물고기 등)은 numpy 로 절차적으로 그려지고,
자막은 Noto Serif CJK KR, 배경음은 Karplus-Strong 현악 합성으로 만든다.

사용법:
    python3 make_video.py                # 전체 영상 렌더 → ink_wash_history.mp4
    python3 make_video.py --stills       # 장면별 확인용 정지 이미지만 출력
    python3 make_video.py --fps 24 --scale 1.0
"""
import argparse
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
KR = 1  # ttc face index for Korean

W, H = 1920, 1080
FPS = 24
PAPER = np.array([238, 230, 214], np.float32)
INK = np.array([22, 20, 19], np.float32)
SEAL = np.array([178, 40, 34], np.float32)

# ---------------------------------------------------------------- 대본 ---
# (그림, 길이(초), 시대 표기, 제목, 본문 줄들, 낙관 글자)
SCENES = [
    ("enso", 9, "", "먹의 길",
     ["수묵화 천삼백 년의 역사", "", "墨 · 水 · 餘白"], "墨"),
    ("swatch", 11, "수묵화란", "먹과 물, 그리고 여백",
     ["색을 덜어내고 먹의 농담(濃淡)과 번짐만으로",
      "산과 물, 마음을 그리는 동아시아의 그림.",
      "‘묵분오색(墨分五色)’ — 먹 하나에 다섯 빛깔이 있다."], "水"),
    ("tang", 12, "8세기 · 당(唐)", "수묵의 탄생",
     ["시인이자 화가 왕유(王維)는 채색을 버리고",
      "먹의 번짐으로 산수를 그려 ‘수묵산수의 비조’로 불린다.",
      "먹을 뿌리고 번지게 하는 파묵·발묵 기법이 이때 싹텄다."], "唐"),
    ("song_north", 14, "10–11세기 · 북송(北宋)", "거대한 산의 시대",
     ["범관(范寬)의 「계산행려도」는 화면을 압도하는 주산으로",
      "자연의 장엄함을 담았다.",
      "곽희(郭熙)는 「조춘도」(1072)와 『임천고치』에서",
      "고원·심원·평원의 ‘삼원법’을 정리했다."], "宋"),
    ("song_south", 12, "12–13세기 · 남송(南宋)", "한 귀퉁이의 풍경",
     ["마원(馬遠)과 하규(夏珪)는 경물을 한쪽 구석에 두고",
      "나머지를 비워 ‘마일각(馬一角) 하반변(夏半邊)’이라 불렸다.",
      "목계(牧谿)·양해(梁楷)의 선종화는 몇 번의 붓질로 깨달음을 그렸다."], "禪"),
    ("yuan", 12, "13–14세기 · 원(元)", "문인의 마음을 그리다",
     ["이민족 왕조 아래 벼슬을 등진 선비들은",
      "그림을 ‘마음의 표현(寫意)’으로 삼았다.",
      "황공망 「부춘산거도」, 예찬의 텅 빈 강변 풍경이 대표적이다."], "元"),
    ("fish", 12, "15–18세기 · 명(明)·청(淸)", "법과 개성",
     ["심주·문징명의 오파(吳派)가 문인화를 이어가고,",
      "동기창(董其昌)은 ‘남북종론’으로 화론을 체계화했다.",
      "팔대산인과 석도는 파격적인 붓으로 개성의 시대를 열었다."], "淸"),
    ("dream", 12, "1447 · 조선 초기", "꿈속의 복숭아꽃 마을",
     ["안견(安堅)은 안평대군의 꿈을 「몽유도원도」로 그려",
      "현실과 이상향을 한 화면에 펼쳤다.",
      "강희안의 「고사관수도」는 선비의 사색을 담았다."], "夢"),
    ("bamboo", 11, "16–17세기 · 조선 중기", "붓끝의 기개",
     ["김명국(金明國)의 「달마도」는 거침없는 감필(減筆)로,",
      "이정(李霆)의 묵죽은 꼿꼿한 대나무로",
      "선비의 정신을 먹 한 빛에 담아냈다."], "竹"),
    ("inwang", 14, "1751 · 조선 후기", "우리 산을 우리 눈으로",
     ["겸재 정선(鄭敾)은 중국풍 관념산수에서 벗어나",
      "조선의 실제 산천을 그리는 ‘진경산수’를 열었다.",
      "비 갠 인왕산을 그린 「인왕제색도」, 「금강전도」가 대표작이다.",
      "단원 김홍도는 풍속과 산수 모두에서 일가를 이루었다."], "謙"),
    ("sehan", 12, "1844 · 조선 후기", "추운 겨울의 소나무",
     ["유배지 제주에서 추사 김정희가 그린 「세한도」.",
      "집 한 채와 나무 몇 그루, 극도로 절제된 붓질 속에",
      "변치 않는 의리에 대한 고마움을 담았다."], "歲"),
    ("pines", 11, "15–16세기 · 일본", "안개 속의 소나무",
     ["조선 수묵의 영향도 받은 일본 무로마치 시대,",
      "셋슈(雪舟)는 「추동산수도」로 날카로운 필선을,",
      "하세가와 도하쿠는 「송림도병풍」으로 안개의 정적을 그렸다."], "松"),
    ("modern", 12, "20세기 – 현재", "다시, 먹으로",
     ["제백석은 소박한 일상을, 이상범·변관식은 한국의 산하를",
      "새로운 수묵으로 그렸다.",
      "오늘날 수묵은 추상과 설치, 영상으로 확장되며",
      "여전히 ‘비움’의 미학을 묻는다."], "今"),
    ("enso_end", 10, "", "비워 둔 곳에 마음이 머문다",
     ["", "먹의 길 — 수묵화의 역사", "", "그림은 모두 코드로 그린 재현 이미지입니다."], "空"),
]

# ------------------------------------------------------------- 유틸 ----


def rng(seed):
    return np.random.default_rng(seed)


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def fbm(h, w, seed, octaves=6, base=4, persistence=0.55):
    r = rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        gh, gw = base * 2 ** o + 1, int(base * 2 ** o * w / h) + 1
        g = r.random((gh, gw)).astype(np.float32)
        up = nd_zoom(g, (h / gh, w / gw), order=3)[:h, :w]
        if up.shape != (h, w):
            up = np.pad(up, ((0, h - up.shape[0]), (0, w - up.shape[1])), mode="edge")
        out += amp * up
        tot += amp
        amp *= persistence
    out /= tot
    return (out - out.min()) / (out.max() - out.min() + 1e-6)


def noise1d(n, seed, octaves=6, base=3):
    r = rng(seed)
    out = np.zeros(n, np.float32)
    amp = 1.0
    for o in range(octaves):
        k = base * 2 ** o + 2
        g = r.standard_normal(k)
        out += amp * np.interp(np.linspace(0, k - 1, n), np.arange(k), g)
        amp *= 0.5
    return out


class Canvas:
    """darkness 0..1 float 캔버스 (1 = 짙은 먹)."""

    def __init__(self, seed):
        self.d = np.zeros((H, W), np.float32)
        self.seed = seed
        self.r = rng(seed)

    def add(self, layer, strength=1.0):
        # 먹을 덧칠: 1-(1-a)(1-b)
        self.d = 1 - (1 - self.d) * (1 - np.clip(layer * strength, 0, 1))

    def mountain(self, ridge, strength=0.9, wash=260, texture=0.5, edge=0.6, seed=0):
        """ridge: 길이 W 배열(각 열의 능선 y). 능선 아래를 담묵으로 채운다."""
        yy = np.arange(H, dtype=np.float32)[:, None]
        depth = yy - ridge[None, :]
        inside = depth > 0
        grad = np.exp(-np.clip(depth, 0, None) / wash)  # 능선에서 아래로 옅어지는 바림
        tex = fbm(H, W, self.seed + seed, octaves=6, base=6)
        # 준(皴): 세로 방향 결
        streak = gaussian_filter(rng(self.seed + seed + 7).random((H, W)).astype(np.float32), (14, 1.2))
        streak = (streak - streak.mean()) / (streak.std() + 1e-6)
        body = grad * (0.55 + texture * (tex - 0.5) + 0.12 * texture * streak)
        body = np.where(inside, body, 0)
        line = np.exp(-(depth ** 2) / (2 * 2.2 ** 2)) * (0.6 + 0.4 * tex)
        layer = np.clip(body * strength + line * edge, 0, 1)
        layer = gaussian_filter(layer, 1.0)
        self.add(layer)

    def mist(self, y0, y1, amount=0.9):
        yy = np.arange(H, dtype=np.float32)[:, None]
        band = smooth((yy - y0) / (y1 - y0 + 1e-6))
        band = np.minimum(band, smooth((y1 + (y1 - y0) - yy) / (y1 - y0 + 1e-6)))
        n = fbm(H, W, self.seed + 99, octaves=4, base=3)
        m = np.clip(band * amount * (0.7 + 0.6 * n), 0, 1)
        self.d *= 1 - m

    def strokes(self, fn, blur=1.2, strength=1.0, supersample=1):
        """PIL 로 그린 뒤 번짐(블러)을 주어 합성."""
        s = supersample
        img = Image.new("L", (W * s, H * s), 0)
        dr = ImageDraw.Draw(img)
        fn(dr, s)
        if s > 1:
            img = img.resize((W, H), Image.LANCZOS)
        a = np.asarray(img, np.float32) / 255.0
        wet = gaussian_filter(a, blur * 4) * 0.35  # 바깥 번짐
        a = np.clip(gaussian_filter(a, blur) + wet, 0, 1)
        grain = 0.85 + 0.3 * fbm(H, W, self.seed + 31, octaves=5, base=20)
        self.add(a * grain, strength)

    def dots(self, cx, cy, n, spread, size=(3, 7), strength=0.85, seed=0):
        r = rng(self.seed + seed)

        def f(dr, s):
            for _ in range(n):
                x = cx + r.normal() * spread[0]
                y = cy + r.normal() * spread[1]
                rad = r.uniform(*size)
                v = int(255 * r.uniform(0.5, 1.0))
                dr.ellipse([(x - rad * 1.4) * s, (y - rad * 0.7) * s,
                            (x + rad * 1.4) * s, (y + rad * 0.7) * s], fill=v)
        self.strokes(f, blur=1.0, strength=strength)


def brush_line(dr, pts, w0, w1, s, val=255, r=None):
    """두께가 변하는 붓선."""
    n = len(pts)
    for i in range(n - 1):
        t = i / max(1, n - 2)
        w = (w0 + (w1 - w0) * t) * (0.85 + 0.3 * (r.random() if r is not None else 0.5))
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        dr.line([(x0 * s, y0 * s), (x1 * s, y1 * s)], fill=val, width=max(1, int(w * s)))
        dr.ellipse([(x1 - w / 2) * s, (y1 - w / 2) * s, (x1 + w / 2) * s, (y1 + w / 2) * s], fill=val)


def curve(x0, y0, x1, y1, bend, n=40, wobble=0.0, r=None):
    t = np.linspace(0, 1, n)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0), (x1 - x0)
    L = math.hypot(nx, ny) + 1e-6
    cx, cy = mx + nx / L * bend, my + ny / L * bend
    xs = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x1
    ys = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t ** 2 * y1
    if wobble and r is not None:
        xs = xs + noise1d(n, int(r.integers(1e9)), 3, 2) * wobble
        ys = ys + noise1d(n, int(r.integers(1e9)), 3, 2) * wobble
    return list(zip(xs, ys))


def ridge_peak(cx, top, width, base_y, seed, rough=25, sharp=1.6):
    x = np.arange(W, dtype=np.float32)
    prof = np.exp(-np.abs((x - cx) / width) ** sharp)
    y = base_y - (base_y - top) * prof + noise1d(W, seed, 7, 4) * rough * (0.3 + prof)
    return y


def pine(c, x, y, height, lean, seed, scale=1.0, strength=1.0):
    r = rng(seed)

    def f(dr, s):
        pts = curve(x, y, x + lean, y - height, r.uniform(-30, 30) * scale, 30, 6 * scale, r)
        brush_line(dr, pts, 16 * scale, 6 * scale, s, 230, r)
        # 가지와 솔잎 덩어리
        for i in range(6):
            t = 0.35 + 0.65 * i / 5
            px, py = pts[int(t * (len(pts) - 1))]
            dirn = -1 if i % 2 else 1
            L = r.uniform(50, 110) * scale * (1.1 - 0.5 * t)
            ex, ey = px + dirn * L, py - r.uniform(0, 25) * scale
            brush_line(dr, curve(px, py, ex, ey, 10 * scale, 12), 6 * scale, 2 * scale, s, 210, r)
            for _ in range(int(40 * scale) + 10):
                a = r.uniform(-math.pi, 0)
                rr = r.uniform(4, 34) * scale
                qx, qy = ex + math.cos(a) * rr * 1.6, ey + math.sin(a) * rr * 0.5
                ln = r.uniform(8, 18) * scale
                ang = r.uniform(0, math.pi)
                dr.line([(qx * s, qy * s), ((qx + math.cos(ang) * ln) * s, (qy - math.sin(ang) * ln * 0.4) * s)],
                        fill=int(r.uniform(150, 250)), width=max(1, int(2 * scale * s)))
    c.strokes(f, blur=1.0, strength=strength, supersample=1)


def bare_tree(c, x, y, height, seed, scale=1.0, strength=0.95):
    r = rng(seed)

    def branch(dr, s, x0, y0, ang, L, w, depth):
        x1 = x0 + math.cos(ang) * L
        y1 = y0 - math.sin(ang) * L
        brush_line(dr, curve(x0, y0, x1, y1, r.uniform(-8, 8), 8), w, w * 0.6, s, 235, r)
        if depth > 0:
            for k in range(2):
                branch(dr, s, x1, y1, ang + r.uniform(0.25, 0.7) * (1 if k else -1),
                       L * r.uniform(0.55, 0.75), w * 0.6, depth - 1)

    def f(dr, s):
        branch(dr, s, x, y, math.pi / 2 + r.uniform(-0.1, 0.1), height * 0.45, 10 * scale, 4)
    c.strokes(f, blur=0.8, strength=strength)


# ----------------------------------------------------------- 장면 그림 ---
TEXT_FADE_X = (0.40, 0.55)  # 왼쪽 텍스트 영역을 비워 두기 위한 페이드


def paint(name):
    c = Canvas(abs(hash(name)) % 100000 if False else sum(map(ord, name)) * 131)
    r = c.r
    if name in ("enso", "enso_end"):
        cx, cy, R = (1260, 540, 300) if name == "enso" else (1500, 520, 230)

        def f(dr, s):
            start = r.uniform(0, 360)
            n = 220
            for i in range(n):
                t = i / n
                a = math.radians(start + t * 330)
                w = 46 * (1 - t) ** 0.5 + 6
                x, y = cx + math.cos(a) * R, cy + math.sin(a) * R
                v = int(255 * (1 - 0.55 * t))
                dr.ellipse([(x - w / 2) * s, (y - w / 2) * s, (x + w / 2) * s, (y + w / 2) * s], fill=v)
            # 비백(飛白): 붓 자국 결
        c.strokes(f, blur=1.3)
        streak = gaussian_filter(r.random((H, W)).astype(np.float32), (0.8, 0.8))
        c.d *= np.clip(0.75 + 0.6 * (streak - 0.5) * 4, 0.3, 1)
        return c.d, ("radial", cx, cy)

    if name == "swatch":
        ys = [300, 430, 560, 690, 820]
        vals = [1.0, 0.75, 0.52, 0.32, 0.15]
        for i, (y, v) in enumerate(zip(ys, vals)):
            def f(dr, s, y=y, i=i):
                pts = curve(1050, y, 1750, y + r.uniform(-20, 20), r.uniform(-25, 25), 60, 3, r)
                brush_line(dr, pts, 70, 18, s, 255, r)
            c.strokes(f, blur=1.6, strength=v)
        return c.d, ("leftright",)

    if name == "tang":
        c.mountain(ridge_peak(1500, 360, 360, 760, 11, 30, 1.3), 0.55, 300, 0.7, 0.25, 1)
        c.mountain(ridge_peak(1150, 520, 280, 800, 12, 20, 1.5), 0.5, 220, 0.8, 0.2, 2)
        c.mist(620, 720, 0.85)
        c.mountain(ridge_peak(1700, 700, 300, 1000, 13, 15, 1.5), 0.75, 160, 0.7, 0.35, 3)
        # 발묵(潑墨) 얼룩
        for k in range(5):
            splash = np.zeros((H, W), np.float32)
            x0, y0 = r.uniform(1000, 1800), r.uniform(450, 900)
            yy, xx = np.ogrid[:H, :W]
            splash = np.exp(-(((xx - x0) / r.uniform(60, 130)) ** 2 + ((yy - y0) / r.uniform(30, 70)) ** 2))
            splash *= fbm(H, W, 500 + k, 4, 5)
            c.add(gaussian_filter(splash.astype(np.float32), 6), 0.6)
        return c.d, ("bottomup",)

    if name == "song_north":
        c.mountain(ridge_peak(1330, 90, 260, 900, 21, 18, 2.2), 0.95, 420, 0.75, 0.6, 1)
        c.mountain(ridge_peak(1130, 540, 130, 1150, 22, 18, 1.8), 0.7, 200, 0.7, 0.45, 2)
        c.mountain(ridge_peak(1750, 450, 190, 1150, 23, 18, 1.8), 0.7, 200, 0.7, 0.45, 3)
        # 정상부 미점 수목
        for k, (x, y) in enumerate([(1250, 160), (1400, 170), (1330, 110), (1130, 560), (1760, 470)]):
            c.dots(x, y, 60, (40, 8), (3, 6), 0.8, k)
        c.mist(700, 800, 0.95)
        # 앞쪽 바위와 행려(行旅)
        c.mountain(ridge_peak(1500, 860, 380, 1100, 24, 12, 1.4), 0.85, 120, 0.8, 0.6, 4)

        def f(dr, s):
            for k in range(4):
                x = 1180 + k * 26
                dr.ellipse([(x - 5) * s, 930 * s, (x + 5) * s, 945 * s], fill=230)
                dr.line([(x * s, 945 * s), (x * s, 965 * s)], fill=230, width=4 * s)
        c.strokes(f, blur=0.6)
        return c.d, ("topdown",)

    if name == "song_south":
        # 오른쪽 아래 귀퉁이 절벽
        x = np.arange(W, dtype=np.float32)
        ridge = 1300 - np.clip((x - 1350) / 570, 0, 1) ** 0.6 * 900 + noise1d(W, 31, 7, 5) * 25
        c.mountain(ridge, 0.95, 380, 0.8, 0.8, 1)
        px = 1640
        pine(c, px, float(ridge[px]) + 8, 260, -240, 32, 1.0)
        # 고사(高士) 한 사람
        fx = 1560
        fy = float(ridge[fx]) + 4
        def f(dr, s):
            dr.ellipse([(fx - 7) * s, (fy - 70) * s, (fx + 7) * s, (fy - 54) * s], fill=240)
            dr.polygon([((fx - 12) * s, (fy - 52) * s), ((fx + 12) * s, (fy - 52) * s), ((fx + 20) * s, fy * s), ((fx - 20) * s, fy * s)], fill=220)
        c.strokes(f, blur=0.8)
        # 아득한 먼 산
        far = ridge_peak(820, 640, 220, 720, 33, 8, 1.6)
        c.mountain(far, 0.22, 60, 0.4, 0.15, 2)
        c.mist(660, 760, 0.9)
        return c.d, ("corner",)

    if name == "yuan":
        # 예찬식 일하양안(一河兩岸)
        x = np.arange(W, dtype=np.float32)
        near = 900 - np.exp(-((x - 1400) / 380) ** 2) * 120 + noise1d(W, 41, 6, 4) * 10
        c.mountain(near, 0.6, 90, 0.8, 0.7, 1)
        for k, tx in enumerate([1280, 1350, 1440, 1520]):
            bare_tree(c, tx, 800 - (k % 2) * 10, 380 + k * 30, 42 + k, 1.0)
        for k, tx in enumerate([1300, 1470]):
            c.dots(tx + 30, 560, 70, (50, 25), (3, 7), 0.75, 10 + k)

        def hut(dr, s):
            dr.line([(1580 * s, 790 * s), (1700 * s, 790 * s)], fill=220, width=4 * s)
            dr.line([(1590 * s, 790 * s), (1590 * s, 735 * s)], fill=220, width=3 * s)
            dr.line([(1690 * s, 790 * s), (1690 * s, 735 * s)], fill=220, width=3 * s)
            dr.line([(1570 * s, 738 * s), (1640 * s, 715 * s), (1712 * s, 738 * s)], fill=230, width=4 * s)
        c.strokes(hut, blur=0.6)
        far = ridge_peak(1350, 300, 420, 400, 44, 14, 1.4)
        c.mountain(far, 0.45, 70, 0.8, 0.5, 2)
        return c.d, ("bottomup",)

    if name == "fish":
        # 팔대산인풍 물고기와 바위
        def f(dr, s):
            cx, cy = 1350, 520
            body = []
            for t in np.linspace(0, 2 * math.pi, 80):
                bx = cx + 230 * math.cos(t)
                by = cy + 70 * math.sin(t) * (1 - 0.35 * math.cos(t))
                body.append((bx * s, by * s))
            dr.line(body + body[:1], fill=235, width=7 * s, joint="curve")
            dr.polygon([((cx + 220) * s, cy * s), ((cx + 330) * s, (cy - 70) * s),
                        ((cx + 300) * s, cy * s), ((cx + 330) * s, (cy + 70) * s)], fill=235)
            dr.polygon([((cx - 20) * s, (cy - 62) * s), ((cx + 60) * s, (cy - 120) * s),
                        ((cx + 80) * s, (cy - 55) * s)], fill=200)
            # 하늘을 흘겨보는 눈
            dr.ellipse([(cx - 165) * s, (cy - 28) * s, (cx - 125) * s, (cy + 4) * s], outline=245, width=5 * s)
            dr.ellipse([(cx - 150) * s, (cy - 30) * s, (cx - 132) * s, (cy - 14) * s], fill=255)
            dr.arc([(cx - 110) * s, (cy - 50) * s, (cx - 30) * s, (cy + 50) * s], 300, 60, fill=210, width=5 * s)
        c.strokes(f, blur=1.0, supersample=2)
        x = np.arange(W, dtype=np.float32)
        rock = 1080 - np.exp(-np.abs((x - 1650) / 230) ** 2.5) * 330 + noise1d(W, 51, 6, 4) * 20
        c.mountain(rock, 0.9, 200, 0.9, 0.7, 1)
        return c.d, ("leftright",)

    if name == "dream":
        # 몽유도원도풍: 기이한 봉우리 무리
        for k in range(9):
            cx = 1080 + k * 90 + r.uniform(-30, 30)
            top = r.uniform(150, 480)
            c.mountain(ridge_peak(cx, top, r.uniform(55, 110), 1250, 60 + k, 22, r.uniform(1.2, 2.0)),
                       0.7, 220, 0.9, 0.55, k)
        c.mist(560, 680, 0.9)
        # 복숭아꽃 마을: 옅은 점
        c.dots(1450, 780, 160, (200, 25), (3, 6), 0.45, 77)
        c.mountain(ridge_peak(1400, 880, 420, 1100, 69, 10, 1.6), 0.6, 120, 0.8, 0.5, 20)
        return c.d, ("leftright",)

    if name == "bamboo":
        def f(dr, s):
            for k, (x, lean) in enumerate([(1260, 40), (1420, -20), (1560, 60)]):
                y = 1100
                seg = r.uniform(130, 170)
                while y > -50:
                    y2 = y - seg
                    x2 = x + lean * seg / 1100
                    brush_line(dr, [(x, y - 6), (x2, y2 + 6)], 24 - k * 4, 22 - k * 4, s, 220 - k * 50, r)
                    x, y = x2, y2
            for _ in range(28):
                bx, by = r.uniform(1150, 1750), r.uniform(120, 750)
                ang = r.uniform(-2.6, -0.5)
                L = r.uniform(90, 170)
                pts = curve(bx, by, bx + math.cos(ang) * L, by - math.sin(ang) * L, r.uniform(-15, 15), 20)
                brush_line(dr, pts, 18, 1, s, int(r.uniform(170, 255)), r)
        c.strokes(f, blur=0.9)
        return c.d, ("bottomup",)

    if name == "inwang":
        # 인왕제색도풍: 거대한 바위 봉우리를 짙은 먹으로 쓸어내림
        ridge = ridge_peak(1460, 170, 280, 1150, 71, 12, 2.6)
        c.mountain(ridge, 1.0, 900, 0.5, 0.9, 1)
        # 적묵(積墨): 굵은 세로 붓질
        def f(dr, s):
            for _ in range(70):
                x = r.normal(1460, 190)
                top = float(np.interp(x, np.arange(W), ridge)) + r.uniform(5, 40)
                L = r.uniform(120, 380)
                brush_line(dr, curve(x, top, x + r.uniform(-30, 30), top + L, r.uniform(-15, 15), 15),
                           r.uniform(18, 40), 6, s, int(r.uniform(120, 230)), r)
        c.strokes(f, blur=2.0, strength=0.75)
        c.mist(600, 700, 1.0)
        for k, x in enumerate([1150, 1300, 1620, 1740]):
            c.dots(x, 850, 80, (50, 20), (4, 8), 0.85, 70 + k)
        c.mountain(ridge_peak(1450, 860, 450, 1100, 72, 14, 1.6), 0.8, 160, 0.8, 0.5, 2)
        return c.d, ("topdown",)

    if name == "sehan":
        def house(dr, s):
            x0, x1, yb = 1200, 1500, 760
            dr.line([(x0 * s, yb * s), (x1 * s, yb * s)], fill=220, width=4 * s)
            dr.line([(x0 * s, yb * s), (x0 * s, 640 * s)], fill=220, width=4 * s)
            dr.line([(x1 * s, yb * s), (x1 * s, 640 * s)], fill=220, width=4 * s)
            dr.line([((x0 - 40) * s, 645 * s), (1350 * s, 560 * s), ((x1 + 40) * s, 645 * s)], fill=235, width=5 * s)
            dr.ellipse([1325 * s, 680 * s, 1375 * s, 730 * s], outline=220, width=4 * s)  # 둥근 창
            dr.line([(1500 * s, 690 * s), (1600 * s, 690 * s), (1600 * s, 760 * s)], fill=200, width=3 * s)
            dr.line([(1050 * s, 790 * s), (1750 * s, 795 * s)], fill=120, width=2 * s)
        c.strokes(house, blur=0.6, supersample=2)
        pine(c, 1120, 790, 420, 30, 81, 0.9, 0.95)
        pine(c, 1040, 790, 360, -40, 82, 0.8, 0.85)
        pine(c, 1660, 790, 330, 10, 83, 0.75, 0.9)
        pine(c, 1740, 790, 300, -20, 84, 0.7, 0.8)
        return c.d, ("leftright",)

    if name == "pines":
        for k in range(9):
            depth = k % 3
            x = 900 + k * 115 + r.uniform(-20, 20)
            pine(c, x, 1000 - depth * 40, 520 - depth * 80, r.uniform(-60, 60), 90 + k,
                 1.0 - depth * 0.2, [0.95, 0.45, 0.22][depth])
        c.mist(820, 960, 0.6)
        return c.d, ("leftright",)

    if name == "modern":
        yy, xx = np.ogrid[:H, :W]
        blob = np.zeros((H, W), np.float32)
        for k in range(7):
            x0, y0 = r.uniform(1000, 1750), r.uniform(200, 900)
            sx, sy = r.uniform(40, 220), r.uniform(30, 160)
            blob += np.exp(-(((xx - x0) / sx) ** 2 + ((yy - y0) / sy) ** 2)).astype(np.float32) * r.uniform(0.4, 1)
        tex = fbm(H, W, 1300, 6, 4)
        layer = np.clip((blob * (0.5 + tex)) * 1.3, 0, 1)
        layer = np.where(layer > 0.15, layer, layer * 0.2)
        c.add(gaussian_filter(layer, 3), 0.9)

        def f(dr, s):
            pts = curve(980, 900, 1820, 260, -260, 80, 10, r)
            brush_line(dr, pts, 60, 4, s, 255, r)
        c.strokes(f, blur=1.4)
        return c.d, ("radial", 1400, 560)

    raise ValueError(name)


def reveal_map(kind, seed):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    n = fbm(H, W, seed, 5, 4)
    if kind[0] == "radial":
        _, cx, cy = kind
        base = np.hypot(xx - cx, yy - cy) / 900
    elif kind[0] == "topdown":
        base = yy / H
    elif kind[0] == "bottomup":
        base = 1 - yy / H
    elif kind[0] == "corner":
        base = np.hypot(W - xx, H - yy) / 1500
    else:
        base = (xx - 900) / (W - 900)
    m = 0.7 * np.clip(base, 0, 1) + 0.3 * n
    return (m - m.min()) / (m.max() - m.min())


# ------------------------------------------------------------ 종이 ------


def paper_texture():
    n = fbm(H, W, 4242, 6, 6)
    fibers = gaussian_filter(rng(7).random((H, W)).astype(np.float32), (0.6, 9))
    fibers = (fibers - fibers.mean()) / (fibers.std() + 1e-6)
    fibers2 = gaussian_filter(rng(8).random((H, W)).astype(np.float32), (9, 0.6))
    fibers2 = (fibers2 - fibers2.mean()) / (fibers2.std() + 1e-6)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vign = 1 - 0.18 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    shade = (0.94 + 0.08 * n + 0.012 * fibers + 0.012 * fibers2) * vign
    return PAPER[None, None, :] * shade[..., None]


# ------------------------------------------------------------ 글자 ------


def text_layer(era, title, lines, seal, centered):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    f_era = ImageFont.truetype(FONT_B, 34, index=KR)
    f_title = ImageFont.truetype(FONT_B, (96 if len(title) < 8 else 76) if centered else 74, index=KR)
    f_body = ImageFont.truetype(FONT_R, 33, index=KR)
    ink = (28, 25, 23, 255)
    red = (165, 42, 34, 255)
    items = []  # (y, 그리기 함수, 등장 지연)
    if centered:
        x = 150
        y = 360
        items.append((0.0, lambda d, y=y: d.text((x, y), title, font=f_title, fill=ink)))
        y += 150
        for i, ln in enumerate(lines):
            if ln:
                items.append((0.6 + i * 0.25, lambda d, y=y, ln=ln: d.text((x + 4, y), ln, font=f_body, fill=ink)))
            y += 56
    else:
        x, y = 120, 300
        items.append((0.0, lambda d, y=y: d.text((x, y), era, font=f_era, fill=red)))
        items.append((0.0, lambda d, y=y: d.line([(x, y + 58), (x + 70, y + 58)], fill=red, width=3)))
        y += 85
        items.append((0.3, lambda d, y=y: d.text((x - 4, y), title, font=f_title, fill=ink)))
        y += 130
        for i, ln in enumerate(lines):
            items.append((0.9 + i * 0.45, lambda d, y=y, ln=ln: d.text((x, y), ln, font=f_body, fill=ink)))
            y += 56
    # 낙관(도장)
    seal_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(seal_img)
    sx, sy, ss = (W - 230, H - 230, 110)
    sd.rounded_rectangle([sx, sy, sx + ss, sy + ss], radius=10, fill=tuple(int(v) for v in SEAL) + (230,))
    f_seal = ImageFont.truetype(FONT_B, 76, index=3)
    bb = sd.textbbox((0, 0), seal, font=f_seal)
    sd.text((sx + (ss - (bb[2] - bb[0])) / 2 - bb[0], sy + (ss - (bb[3] - bb[1])) / 2 - bb[1]),
            seal, font=f_seal, fill=(240, 228, 210, 255))
    a = np.asarray(seal_img).astype(np.float32)
    worn = fbm(H, W, 555, 5, 40)
    a[..., 3] *= np.clip((worn - 0.25) * 3, 0, 1)
    seal_img = Image.fromarray(a.astype(np.uint8))

    layers = []
    for delay, fn in items:
        li = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        fn(ImageDraw.Draw(li))
        layers.append((delay, np.asarray(li).astype(np.float32) / 255.0))
    return layers, np.asarray(seal_img).astype(np.float32) / 255.0


# ------------------------------------------------------------ 합성 ------
_CACHE = {}
_PAPER = None


def scene_assets(i):
    global _PAPER
    if _PAPER is None:
        _PAPER = paper_texture().astype(np.float32)
    if i not in _CACHE:
        name, dur, era, title, lines, seal = SCENES[i]
        d, kind = paint(name)
        centered = name.startswith("enso")
        if not centered and name != "swatch":
            fx = np.arange(W, dtype=np.float32) / W
            d = d * smooth((fx - TEXT_FADE_X[0]) / (TEXT_FADE_X[1] - TEXT_FADE_X[0]))[None, :]
        rm = reveal_map(kind, 900 + i)
        tl, sl = text_layer(era, title, lines, seal, centered)
        _CACHE.clear()  # 메모리 절약: 워커당 한 장면만 유지
        _CACHE[i] = (d.astype(np.float32), rm.astype(np.float32), tl, sl)
    return _CACHE[i]


def starts():
    s, out = 0.0, []
    for sc in SCENES:
        out.append(s)
        s += sc[1]
    return out, s


def render_frame(args):
    i, t_local, scale = args  # 장면 번호, 장면 내 시간(초)
    name, dur, *_ = SCENES[i]
    d, rm, tl, sl = scene_assets(i)
    p = t_local / dur
    # 먹이 번져 나타남 (장면 길이의 55% 동안)
    prog = min(1.0, t_local / (dur * 0.55))
    alpha = np.clip((prog * 1.25 - rm) / 0.18, 0, 1)
    alpha = alpha * alpha * (3 - 2 * alpha)
    dd = d * alpha
    # 아주 느린 줌 (Ken Burns)
    z = 1.0 + 0.035 * p
    if z > 1.0005:
        img = Image.fromarray(dd.astype(np.float32))
        cw, ch = W / z, H / z
        x0, y0 = (W - cw) * 0.6, (H - ch) * 0.5
        img = img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
        dd = np.asarray(img, np.float32)
    rgb = _PAPER * (1 - dd[..., None]) + INK[None, None, :] * dd[..., None]
    # 글자
    for delay, layer in tl:
        a = smooth((t_local - 0.8 - delay) / 0.9) * layer[..., 3]
        if a.max() > 0:
            rgb = rgb * (1 - a[..., None]) + layer[..., :3] * 255 * a[..., None]
    sa = smooth((t_local - dur * 0.55) / 0.5) * sl[..., 3]
    rgb = rgb * (1 - sa[..., None]) + sl[..., :3] * 255 * sa[..., None]
    # 장면 끝: 종이로 사라짐
    fade = smooth((dur - t_local) / 1.0)
    if i == 0:
        fade = min(fade, smooth(t_local / 1.0))
    rgb = _PAPER * (1 - fade) + rgb * fade
    if i == len(SCENES) - 1:  # 마지막 검은 화면 페이드
        rgb = rgb * smooth((dur - t_local) / 2.0)
    out = np.clip(rgb, 0, 255).astype(np.uint8)
    if scale != 1.0:
        out = np.asarray(Image.fromarray(out).resize((int(W * scale) // 2 * 2, int(H * scale) // 2 * 2), Image.LANCZOS))
    return out.tobytes()


# ------------------------------------------------------------ 음악 ------


def make_music(path, total, sr=44100):
    r = rng(2026)
    n = int(total * sr)
    out = np.zeros(n + sr * 8, np.float32)
    t = np.arange(len(out)) / sr
    # 저음 지속음 (D2 + A2)
    drone = 0.05 * np.sin(2 * np.pi * 73.42 * t) + 0.03 * np.sin(2 * np.pi * 110.0 * t)
    drone *= 0.6 + 0.4 * np.sin(2 * np.pi * t / 11.0)
    out += drone.astype(np.float32)
    # 거문고/고쟁 느낌의 Karplus-Strong 뜯기, D 단조 5음계
    scale = [146.83, 174.61, 196.0, 220.0, 261.63, 293.66, 349.23, 392.0, 440.0]

    def pluck(f, dur, amp):
        N = int(sr / f)
        buf = r.uniform(-1, 1, N).astype(np.float32)
        buf = gaussian_filter(buf, 1.0)
        L = int(dur * sr)
        y = np.zeros(L, np.float32)
        decay = 0.996
        idx = 0
        for k in range(L):
            v = buf[idx]
            nxt = buf[(idx + 1) % N]
            buf[idx] = decay * 0.5 * (v + nxt)
            y[k] = v
            idx = (idx + 1) % N
        env = np.exp(-np.arange(L) / (sr * dur * 0.35))
        return y * env * amp

    pos = 1.5
    starts_, _ = starts()
    while pos < total - 4:
        f = scale[int(r.integers(len(scale)))]
        s = int(pos * sr)
        note = pluck(f, 3.5, r.uniform(0.18, 0.3))
        out[s:s + len(note)] += note
        if r.random() < 0.35:  # 농현 느낌의 겹음
            note2 = pluck(f * 1.5 if f < 300 else f / 2, 3.0, 0.12)
            s2 = s + int(r.uniform(0.15, 0.4) * sr)
            out[s2:s2 + len(note2)] += note2
        pos += r.choice([1.2, 1.8, 2.4, 3.0])
    # 장면 전환마다 낮은 울림
    for st in starts_[1:]:
        s = int(st * sr)
        L = sr * 4
        tt = np.arange(L) / sr
        bell = (np.sin(2 * np.pi * 98 * tt) + 0.5 * np.sin(2 * np.pi * 98 * 2.76 * tt)) * np.exp(-tt / 1.4) * 0.08
        out[s:s + L] += bell.astype(np.float32)
    # 간단한 리버브: 감쇠 잡음 IR 컨볼루션
    ir_len = int(2.8 * sr)
    ir = r.standard_normal(ir_len).astype(np.float32) * np.exp(-np.arange(ir_len) / (sr * 0.7))
    ir /= np.sqrt((ir ** 2).sum())
    from scipy.signal import fftconvolve
    wet = fftconvolve(out, ir)[:len(out)]
    mix = (0.65 * out + 0.45 * wet)[:n]
    fade = np.minimum(1, np.minimum(np.arange(n) / (sr * 2), (n - np.arange(n)) / (sr * 3)))
    mix *= fade
    mix /= np.abs(mix).max() + 1e-6
    mix *= 0.8
    pcm = (mix * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


# ------------------------------------------------------------ main ------


def main():
    global FPS
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true")
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--out", default=os.path.join(HERE, "ink_wash_history.mp4"))
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 2)
    a = ap.parse_args()
    FPS = a.fps
    st, total = starts()

    if a.stills:
        os.makedirs(os.path.join(HERE, "stills"), exist_ok=True)
        jobs = [(i, SCENES[i][1] * 0.8, 0.5) for i in range(len(SCENES))]
        with Pool(a.workers) as pool:
            for (i, _, sc), b in zip(jobs, pool.imap(render_frame, jobs)):
                im = Image.frombytes("RGB", (int(W * sc) // 2 * 2, int(H * sc) // 2 * 2), b)
                im.save(os.path.join(HERE, "stills", f"{i:02d}_{SCENES[i][0]}.jpg"), quality=88)
                print("still", i, SCENES[i][0], flush=True)
        return

    wav = os.path.join(HERE, "_music.wav")
    print(f"총 길이 {total:.0f}초, 음악 합성 중…", flush=True)
    make_music(wav, total)
    ow, oh = int(W * a.scale) // 2 * 2, int(H * a.scale) // 2 * 2
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ow}x{oh}", "-r", str(FPS), "-i", "-",
        "-i", wav,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", a.out,
    ], stdin=subprocess.PIPE)
    jobs = []
    for i, sc in enumerate(SCENES):
        nfr = int(round(sc[1] * FPS))
        jobs += [(i, k / FPS, a.scale) for k in range(nfr)]
    with Pool(a.workers) as pool:
        for k, b in enumerate(pool.imap(render_frame, jobs, chunksize=12)):
            ff.stdin.write(b)
            if k % (FPS * 5) == 0:
                print(f"  {k / FPS:6.1f}s / {total:.0f}s", flush=True)
    ff.stdin.close()
    ff.wait()
    os.remove(wav)
    print("완료:", a.out)


if __name__ == "__main__":
    main()
