import math, os, sys, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
K = 6                      # 360x640 units -> 2160x3840 supersampled
SW, SH = 360 * K, 640 * K
FONT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
BG = (253, 253, 251); BLOB = (232, 246, 240); GREEN = (14, 150, 100)
BLACK = (20, 20, 20); PINK = (255, 150, 190); GOLD = (232, 170, 30); RED = (225, 50, 60)
SILVER = (196, 200, 208); DARKGREEN = (10, 90, 60)
OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
os.makedirs(OUT, exist_ok=True)

def f(sz): return ImageFont.truetype(FONT, int(sz * K))
def P(x, y): return (x * K, y * K)
def R(x0, y0, x1, y1): return [x0 * K, y0 * K, x1 * K, y1 * K]
LW = int(2.6 * K)

# ---------------- scenes ----------------
# text, highlight words, duration
SCENES = [
    ("Pendant 30 jours, une carte à gratter décide combien Maxime épargne.", {"30", "jours,", "carte", "gratter"}, 4.2),
    ("Jour 1. Il choisit sa fourchette : entre 1 et 10 euros.", {"Jour", "1.", "fourchette"}, 3.6),
    ("Son objectif : le cadeau de Noël de sa mère.", {"cadeau", "Noël"}, 3.0),
    ("Il gratte…", {"gratte…"}, 2.6),
    ("7 euros. Ça pique un peu.", {"7", "euros."}, 2.8),
    ("Mais pas le droit de tricher.", {"tricher."}, 2.6),
    ("Demain ? Peut-être 1. Peut-être 10.", {"1.", "10."}, 3.2),
    ("Abonne-toi pour voir combien il aura dans 30 jours.", {"Abonne-toi", "30", "jours."}, 3.8),
]
WORD_T = 0.27

def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3

def blob(d, cx, cy, rx, ry):
    d.ellipse(R(cx - rx, cy - ry, cx + rx, cy + ry), fill=BLOB)

def maxime(d, cx, cy, s=1.0, t=0.0, face="smile", name=False, arm_up=False):
    bob = math.sin(t * 5) * 1.5
    cy = cy + bob
    def S(v): return v * s
    # legs
    d.line([P(cx - S(10), cy + S(40)), P(cx - S(12), cy + S(72))], fill=BLACK, width=int(LW * 1.6))
    d.line([P(cx + S(10), cy + S(40)), P(cx + S(12), cy + S(72))], fill=BLACK, width=int(LW * 1.6))
    # body
    d.rounded_rectangle(R(cx - S(26), cy - S(8), cx + S(26), cy + S(44)), radius=int(S(14) * K), fill=GREEN, outline=BLACK, width=LW)
    # arms
    if arm_up:
        d.line([P(cx + S(24), cy + S(4)), P(cx + S(44), cy - S(22))], fill=GREEN, width=int(LW * 3))
    else:
        d.line([P(cx + S(24), cy + S(4)), P(cx + S(40), cy + S(26))], fill=GREEN, width=int(LW * 3))
    d.line([P(cx - S(24), cy + S(4)), P(cx - S(40), cy + S(26))], fill=GREEN, width=int(LW * 3))
    # head
    d.ellipse(R(cx - S(24), cy - S(56), cx + S(24), cy - S(8)), fill="white", outline=BLACK, width=LW)
    ey = cy - S(34)
    if face == "shock":
        d.ellipse(R(cx - S(11), ey - S(4), cx - S(5), ey + S(4)), fill=BLACK)
        d.ellipse(R(cx + S(5), ey - S(4), cx + S(11), ey + S(4)), fill=BLACK)
        d.ellipse(R(cx - S(5), cy - S(22), cx + S(5), cy - S(14)), outline=BLACK, width=LW)
    else:
        d.ellipse(R(cx - S(10), ey - S(3), cx - S(5), ey + S(3)), fill=BLACK)
        d.ellipse(R(cx + S(5), ey - S(3), cx + S(10), ey + S(3)), fill=BLACK)
        if face == "grimace":
            d.line([P(cx - S(9), cy - S(19)), P(cx - S(3), cy - S(22)), P(cx + S(3), cy - S(18)), P(cx + S(9), cy - S(21))], fill=BLACK, width=LW)
        else:
            d.arc(R(cx - S(9), cy - S(30), cx + S(9), cy - S(16)), 20, 160, fill=BLACK, width=LW)
    if name:
        fn = f(11)
        tw = d.textlength("Maxime", font=fn) / K
        d.rounded_rectangle(R(cx - tw / 2 - 8, cy - S(80), cx + tw / 2 + 8, cy - S(62)), radius=9 * K, fill=GREEN)
        d.text(P(cx, cy - S(71)), "Maxime", font=fn, fill="white", anchor="mm")

def card(d, cx, cy, w=120, h=78, reveal=0.0, value="7 €", mystery=True, t=0.0, scratch_x=None):
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    d.rounded_rectangle(R(x0, y0, x1, y1), radius=10 * K, fill=(255, 248, 225), outline=BLACK, width=LW)
    d.rounded_rectangle(R(x0 + 6, y0 + 6, x1 - 6, y1 - 6), radius=7 * K, outline=GOLD, width=int(LW * 0.8))
    d.text(P(cx, cy + 3), value, font=f(30), fill=GREEN, anchor="mm")
    # silver coating covering the unrevealed part (from the right)
    if reveal < 1:
        cover_x0 = x0 + 10 + (w - 20) * reveal
        d.rounded_rectangle(R(cover_x0, y0 + 10, x1 - 10, y1 - 10), radius=5 * K, fill=SILVER)
        if mystery and reveal < 0.2:
            d.text(P(cx, cy + 2), "?", font=f(34), fill=RED, anchor="mm")
        # glitter
        for i in range(6):
            gx = cover_x0 + ((i * 37 + t * 40) % max(1, (x1 - 10 - cover_x0)))
            gy = y0 + 16 + (i * 13) % (h - 30)
            d.ellipse(R(gx - 1.2, gy - 1.2, gx + 1.2, gy + 1.2), fill="white")
    # tiny seal logo
    d.ellipse(R(x0 + 8, y1 - 22, x0 + 22, y1 - 8), fill=DARKGREEN)
    d.text(P(x0 + 15, y1 - 15), "€", font=f(8), fill=GOLD, anchor="mm")

def coin(d, x, y, r=7):
    d.ellipse(R(x - r, y - r, x + r, y + r), fill=GOLD, outline=BLACK, width=int(LW * 0.7))
    d.text(P(x, y + 0.5), "€", font=f(r * 1.2), fill=BLACK, anchor="mm")

def piggy(d, cx, cy, s=1.0, label=None):
    def S(v): return v * s
    d.ellipse(R(cx - S(42), cy - S(30), cx + S(42), cy + S(30)), fill=PINK, outline=BLACK, width=LW)
    d.ellipse(R(cx + S(32), cy - S(10), cx + S(52), cy + S(10)), fill=PINK, outline=BLACK, width=LW)
    d.ellipse(R(cx + S(38), cy - S(4), cx + S(42), cy), fill=BLACK); d.ellipse(R(cx + S(43), cy - S(4), cx + S(47), cy), fill=BLACK)
    d.polygon([P(cx + S(10), cy - S(28)), P(cx + S(20), cy - S(44)), P(cx + S(26), cy - S(24))], fill=PINK, outline=BLACK)
    d.ellipse(R(cx + S(16), cy - S(14), cx + S(22), cy - S(8)), fill=BLACK)
    d.line([P(cx - S(12), cy - S(30)), P(cx + S(6), cy - S(30))], fill=BLACK, width=int(LW * 1.3))
    for lx in (-S(26), S(16)):
        d.rectangle(R(cx + lx, cy + S(24), cx + lx + S(10), cy + S(40)), fill=PINK, outline=BLACK, width=LW)
    if label:
        d.text(P(cx - S(6), cy + S(4)), label, font=f(15 * s), fill=BLACK, anchor="mm")

def gift(d, cx, cy, s=1.0):
    def S(v): return v * s
    d.rectangle(R(cx - S(40), cy - S(26), cx + S(40), cy + S(36)), fill=(255, 225, 120), outline=BLACK, width=LW)
    d.rectangle(R(cx - S(46), cy - S(40), cx + S(46), cy - S(24)), fill=(255, 210, 90), outline=BLACK, width=LW)
    d.rectangle(R(cx - S(7), cy - S(40), cx + S(7), cy + S(36)), fill=RED, outline=BLACK, width=LW)
    d.ellipse(R(cx - S(26), cy - S(60), cx - S(2), cy - S(40)), outline=RED, width=int(LW * 1.6))
    d.ellipse(R(cx + S(2), cy - S(60), cx + S(26), cy - S(40)), outline=RED, width=int(LW * 1.6))

def tag(d, x, y, txt, fill=GREEN, col="white", sz=12):
    fn = f(sz); tw = d.textlength(txt, font=fn) / K
    d.rounded_rectangle(R(x - tw / 2 - 9, y - sz * 0.85, x + tw / 2 + 9, y + sz * 0.85), radius=int(sz * 0.8 * K), fill=fill)
    d.text(P(x, y), txt, font=fn, fill=col, anchor="mm")

def illus(i, d, t, dur):
    p = t / dur
    if i == 0:   # hook: mystery card + Maxime, day counter
        blob(d, 180, 395, 150, 120)
        maxime(d, 120, 410, 1.15, t, "shock", name=True)
        sc = 0.9 + 0.1 * ease(t / 0.4)
        card(d, 232, 380, 120 * sc, 78 * sc, 0, "7 €", True, t)
        tag(d, 232, 318, "30 JOURS", RED, sz=12)
    elif i == 1:  # range slider
        blob(d, 180, 400, 150, 115)
        maxime(d, 105, 430, 1.0, t, "smile")
        tag(d, 236, 330, "JOUR 1/30", GREEN, sz=12)
        x0, x1, y = 165, 300, 395
        d.line([P(x0, y), P(x1, y)], fill=(200, 200, 200), width=int(LW * 2.4))
        a = ease(t / 1.2)
        hx = x0 + (x1 - x0) * (0.25 + 0.75 * a)
        d.line([P(x0, y), P(hx, y)], fill=GREEN, width=int(LW * 2.4))
        for x, lab in ((x0, "1 €"), (hx, "10 €")):
            d.ellipse(R(x - 9, y - 9, x + 9, y + 9), fill="white", outline=BLACK, width=LW)
            d.text(P(x, y + 24), lab, font=f(15), fill=BLACK, anchor="mm")
        d.text(P(232, 448), "ta fourchette", font=f(11), fill=(110, 110, 110), anchor="mm")
    elif i == 2:  # goal: gift for mum
        blob(d, 180, 400, 150, 115)
        maxime(d, 110, 425, 1.0, t, "smile", arm_up=True)
        g = ease(t / 0.5)
        gift(d, 235, 415, 0.95 * (0.7 + 0.3 * g))
        tag(d, 235, 330, "Noël de maman", RED, sz=12)
    elif i == 3:  # scratching
        blob(d, 180, 400, 150, 115)
        rv = ease(t / (dur * 0.9)) * 0.28
        card(d, 200, 385, 160, 104, rv, "7 €", False, t)
        cx = 200 - 70 + 140 * rv / 0.28 * 0.3
        cy = 385 + math.sin(t * 22) * 22
        coin(d, cx, cy, 11)
        maxime(d, 62, 440, 0.75, t, "shock")
    elif i == 4:  # reveal 7€
        blob(d, 180, 400, 150, 115)
        card(d, 180, 362, 170, 110, 1, "7 €", False, t)
        for k in range(6):
            a = k / 6 * math.tau + 0.3
            r = 70 + 30 * ease(t / 0.6)
            x, y = 180 + math.cos(a) * r * 1.15, 362 + math.sin(a) * r * 0.7
            if 50 < x < 300: d.line([P(x, y), P(x + math.cos(a) * 8, y + math.sin(a) * 6)], fill=GOLD, width=int(LW * 1.3))
        maxime(d, 62, 470, 0.8, t, "grimace")
        piggy(d, 250, 465, 0.55)
        if t > 0.5:
            fy = 405 + 45 * ease((t - 0.5) / 0.8)
            if fy < 446: coin(d, 250, fy, 8)
    elif i == 5:  # no cheating
        blob(d, 180, 400, 150, 115)
        card(d, 230, 390, 120, 78, 1, "7 €", False, t)
        maxime(d, 110, 420, 1.0, t, "grimace")
        # red cross over a "re-scratch" hand
        sh = 1 + 0.15 * math.sin(min(t, 0.6) * 20) * (1 - min(t, 0.6) / 0.6)
        d.line([P(195 - 20 * sh, 355 - 20 * sh), P(265 + 20 * sh, 425 + 20 * sh)], fill=RED, width=int(LW * 3))
        d.line([P(265 + 20 * sh, 355 - 20 * sh), P(195 - 20 * sh, 425 + 20 * sh)], fill=RED, width=int(LW * 3))
        tag(d, 230, 455, "1 seule carte par jour", BLACK, sz=10)
    elif i == 6:  # tomorrow ? 1 or 10
        blob(d, 180, 400, 150, 115)
        fl = int(t * 4) % 2
        card(d, 118, 385, 110, 72, 1, "1 €", False, t)
        card(d, 242, 385, 110, 72, 1, "10 €", False, t)
        d.text(P(180, 385), "?", font=f(34), fill=RED if fl else BLACK, anchor="mm")
        tag(d, 180, 318, "DEMAIN", GREEN, sz=12)
        maxime(d, 180, 470, 0.65, t, "shock")
    elif i == 7:  # follow: piggy with counter
        blob(d, 180, 400, 150, 115)
        piggy(d, 205, 405, 1.15, None)
        tag(d, 205, 330, "7 € / ???", DARKGREEN, col=GOLD, sz=14)
        maxime(d, 95, 440, 0.85, t, "smile", arm_up=True)
        a = ease(t / 0.8)
        tag(d, 180, 500, "+ S'ABONNER", RED, sz=13 * (0.8 + 0.2 * a))

def layout_text(d, text, hl):
    fn = f(25); words = text.split(" ")
    lines, cur = [], []
    for w_ in words:
        test = " ".join(cur + [w_])
        if d.textlength(test, font=fn) / K > 270 and cur:
            lines.append(cur); cur = [w_]
        else:
            cur.append(w_)
    lines.append(cur)
    placed = []; y = 142; idx = 0
    space = d.textlength(" ", font=fn) / K
    for ln in lines:
        widths = [d.textlength(w_, font=fn) / K for w_ in ln]
        total = sum(widths) + space * (len(ln) - 1)
        x = 180 - total / 2
        for w_, ww in zip(ln, widths):
            placed.append((idx, w_, x, y, ww, w_ in hl)); x += ww + space; idx += 1
        y += 31
    return placed

def draw_text(d, placed, t):
    fn = f(25)
    for idx, w_, x, y, ww, h in placed:
        st = idx * WORD_T
        if t < st: continue
        a = min(1, (t - st) / 0.12)
        sc = 1.25 - 0.25 * a
        fs = f(25 * sc)
        col = (14, 150, 100) if h else BLACK
        if h and any(c.isdigit() for c in w_): col = RED
        d.text(P(x + ww / 2, y), w_, font=fs, fill=col, anchor="mm", stroke_width=int(0.5 * K), stroke_fill=col)

def render_scene(i):
    text, hl, dur = SCENES[i]
    n = int(round(dur * FPS))
    path = f"{OUT}/s{i}.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", path + ".tmp.mp4"]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    probe = Image.new("RGB", (SW, SH)); placed = layout_text(ImageDraw.Draw(probe), text, hl)
    for fi in range(n):
        t = fi / FPS
        im = Image.new("RGB", (SW, SH), BG); d = ImageDraw.Draw(im)
        illus(i, d, t, dur)
        if not os.environ.get('NOTEXT'): draw_text(d, placed, t)
        pr.stdin.write(im.resize((W, H), Image.LANCZOS).tobytes())
    pr.stdin.close(); pr.wait()
    os.rename(path + ".tmp.mp4", path)

# ---------------- sound ----------------
SR = 44100
def env(n, a=0.005, r=0.1):
    t = np.arange(n) / SR; e = np.minimum(1, t / a) * np.exp(-t / r); return e
def pop():
    n = int(0.08 * SR); t = np.arange(n) / SR
    return 0.35 * np.sin(2 * np.pi * (900 - 4000 * t) * t) * env(n, 0.002, 0.03)
def whoosh(d=0.35):
    n = int(d * SR); x = np.random.randn(n); x = np.convolve(x, np.ones(30) / 30, "same")
    return 0.5 * x * np.sin(np.pi * np.arange(n) / n) ** 2
def ding():
    n = int(0.9 * SR); t = np.arange(n) / SR
    return 0.4 * (np.sin(2 * np.pi * 1320 * t) + 0.5 * np.sin(2 * np.pi * 2640 * t)) * env(n, 0.002, 0.3)
def coins():
    out = np.zeros(int(0.8 * SR))
    for k in range(7):
        s = int((0.03 + k * 0.09 + np.random.rand() * 0.03) * SR); n = int(0.12 * SR); t = np.arange(n) / SR
        fr = 2500 + np.random.rand() * 2500
        seg = 0.25 * np.sin(2 * np.pi * fr * t) * env(n, 0.001, 0.04)
        out[s:s + n] += seg[:len(out) - s]
    return out
def scratch(d):
    n = int(d * SR); x = np.random.randn(n)
    x = x - np.convolve(x, np.ones(6) / 6, "same")
    mod = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 7 * np.arange(n) / SR))
    return 0.3 * x * mod * np.minimum(1, np.arange(n)[::-1] / (0.1 * SR))
def riser(d=1.2):
    n = int(d * SR); t = np.arange(n) / SR
    return 0.15 * np.sin(2 * np.pi * (200 + 500 * t / d) * t) * (t / d)
def buzz():
    n = int(0.35 * SR); t = np.arange(n) / SR
    return 0.25 * np.sign(np.sin(2 * np.pi * 140 * t)) * env(n, 0.002, 0.15)
def heartbeat():
    out = np.zeros(int(1.6 * SR))
    for s0 in (0, 0.25, 0.8, 1.05):
        n = int(0.12 * SR); t = np.arange(n) / SR
        seg = 0.5 * np.sin(2 * np.pi * 55 * t) * env(n, 0.003, 0.05); s = int(s0 * SR); out[s:s + n] += seg
    return out

def build_audio(path):
    total = sum(s[2] for s in SCENES); buf = np.zeros(int(total * SR) + SR)
    def add(x, at):
        s = int(at * SR); buf[s:s + len(x)] += x[:len(buf) - s]
    t0 = 0
    for i, (text, hl, dur) in enumerate(SCENES):
        if i > 0: add(whoosh(), max(0, t0 - 0.12))
        if not os.environ.get('NOTEXT'):
            for k in range(len(text.split(" "))): add(pop() * 0.6, t0 + k * WORD_T)
        if i == 0: add(riser(1.3), t0 + 0.2); add(ding() * 0.5, t0 + 0.05)
        if i == 3: add(scratch(dur * 0.9), t0 + 0.05)
        if i == 4: add(ding(), t0 + 0.05); add(coins(), t0 + 0.55)
        if i == 5: add(buzz(), t0 + 0.1)
        if i == 6: add(heartbeat(), t0 + 0.3)
        if i == 7: add(coins() * 0.8, t0 + 0.2); add(ding() * 0.6, t0 + 0.9)
        t0 += dur
    buf = buf[:int(total * SR)]
    buf = buf / max(1e-6, np.abs(buf).max()) * 0.8
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((buf * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    mode = sys.argv[2] if len(sys.argv) > 2 else "all"
    if mode == "contact":
        ims = []
        for i, (text, hl, dur) in enumerate(SCENES):
            im = Image.new("RGB", (SW, SH), BG); d = ImageDraw.Draw(im)
            illus(i, d, dur * 0.8, dur); draw_text(d, layout_text(d, text, hl), 99)
            ims.append(im.resize((270, 480)))
        sheet = Image.new("RGB", (270 * 4, 480 * 2), "white")
        for i, im in enumerate(ims): sheet.paste(im, ((i % 4) * 270, (i // 4) * 480))
        sheet.save(f"{OUT}/contact.png")
    else:
        from multiprocessing import Pool
        with Pool(2) as pool: pool.map(render_scene, range(len(SCENES)))
        with open(f"{OUT}/list.txt", "w") as fl:
            for i in range(len(SCENES)): fl.write(f"file 's{i}.mp4'\n")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{OUT}/list.txt", "-c", "copy", f"{OUT}/video.mp4"], check=True)
        build_audio(f"{OUT}/sfx.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/video.mp4", "-i", f"{OUT}/sfx.wav", "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", f"{OUT}/final.mp4"], check=True)
