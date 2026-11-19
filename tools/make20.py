import sys, math, subprocess, os
import numpy as np
import make as m
from make import *

m.SCENES = [
    ("Tu n'arrives pas à épargner ? C'est pas ta faute.", {"épargner", "faute."}, 3.6),
    ("C'est ta méthode.", {"méthode."}, 2.2),
    ("Garder 100 euros en fin de mois ? Presque personne n'y arrive.", {"100", "euros", "personne"}, 4.0),
    ("Alors Maxime fait l'inverse : chaque jour, il gratte une carte.", {"l'inverse", "carte."}, 4.0),
    ("Elle tire un petit montant au hasard, dans la fourchette qu'il a choisie.", {"hasard,", "fourchette"}, 4.2),
    ("Aujourd'hui : 3 euros. Hier : 8.", {"3", "8."}, 2.8),
    ("Ça passe sans douleur.", {"douleur."}, 2.2),
    ("Et toi, ta fourchette, ce serait combien ? Dis-le en commentaire.", {"fourchette,", "commentaire."}, 4.0),
]

def wallet(d, cx, cy, s=1.0, empty=True, t=0):
    def S(v): return v * s
    d.rounded_rectangle(R(cx - S(42), cy - S(28), cx + S(42), cy + S(28)), radius=int(S(8) * K), fill=(150, 95, 60), outline=BLACK, width=LW)
    d.rounded_rectangle(R(cx + S(14), cy - S(10), cx + S(46), cy + S(10)), radius=int(S(5) * K), fill=(175, 115, 75), outline=BLACK, width=LW)
    if empty:
        for k in range(3):
            y = cy - S(40) - k * 10 - (t * 20) % 10
            d.line([P(cx - S(20) + k * 15, y), P(cx - S(14) + k * 15, y - 6)], fill=(150, 150, 150), width=LW)

def calendar(d, cx, cy, s=1.0, day="30"):
    def S(v): return v * s
    d.rectangle(R(cx - S(34), cy - S(30), cx + S(34), cy + S(34)), fill="white", outline=BLACK, width=LW)
    d.rectangle(R(cx - S(34), cy - S(30), cx + S(34), cy - S(12)), fill=RED, outline=BLACK, width=LW)
    d.text(P(cx, cy + S(12)), day, font=f(24 * s), fill=BLACK, anchor="mm")

def illus(i, d, t, dur):
    blob(d, 180, 400, 150, 115)
    if i == 0:
        maxime(d, 125, 425, 1.15, t, "grimace", name=True)
        wallet(d, 245, 410, 0.9, True, t)
        tag(d, 245, 350, "0 € de côté", RED, sz=11)
    elif i == 1:
        maxime(d, 120, 425, 1.0, t, "smile")
        a = ease(t / 0.5)
        tag(d, 240, 380, "LA MÉTHODE", GREEN, sz=14 * (0.7 + 0.3 * a))
        d.text(P(240, 425), "?", font=f(40), fill=RED, anchor="mm")
    elif i == 2:
        calendar(d, 115, 400, 1.0, "30")
        tag(d, 115, 345, "fin du mois", BLACK, sz=10)
        tag(d, 240, 375, "100 €", GREEN, sz=18)
        d.line([P(205, 355), P(275, 395)], fill=RED, width=int(LW * 2.5))
        maxime(d, 240, 450, 0.6, t, "shock")
    elif i == 3:
        card(d, 210, 390, 120, 80, ease(t / 3) * 0.25, "€", True, t)
        coin(d, 165 + 30 * ease(t / 3), 390 + math.sin(t * 20) * 18, 10)
        maxime(d, 95, 425, 1.0, t, "smile", arm_up=True)
        tag(d, 210, 332, "CHAQUE JOUR", GREEN, sz=12)
    elif i == 4:
        x0, x1, y = 120, 260, 360
        d.line([P(x0, y), P(x1, y)], fill=GREEN, width=int(LW * 2.4))
        for x, lab in ((x0, "1 €"), (x1, "10 €")):
            d.ellipse(R(x - 9, y - 9, x + 9, y + 9), fill="white", outline=BLACK, width=LW)
            d.text(P(x, y + 22), lab, font=f(14), fill=BLACK, anchor="mm")
        # dice-like random number cycling
        n = [2, 9, 5, 1, 7, 4, 10, 3][int(t * 6) % 8] if t < dur * 0.75 else 3
        d.rounded_rectangle(R(155, 400, 225, 460), radius=10 * K, fill=(255, 248, 225), outline=BLACK, width=LW)
        d.text(P(190, 431), f"{n} €", font=f(22), fill=GREEN, anchor="mm")
        maxime(d, 75, 440, 0.7, t, "shock")
    elif i == 5:
        card(d, 125, 385, 110, 72, 1, "3 €", False, t)
        tag(d, 125, 335, "aujourd'hui", GREEN, sz=10)
        card(d, 240, 385, 110, 72, 1, "8 €", False, t)
        tag(d, 240, 335, "hier", BLACK, sz=10)
        maxime(d, 180, 470, 0.65, t, "smile")
    elif i == 6:
        maxime(d, 115, 425, 1.0, t, "smile", arm_up=True)
        piggy(d, 245, 420, 0.85)
        fy = 330 + 55 * ease((t % 0.9) / 0.6)
        coin(d, 245, min(fy, 385), 8)
    elif i == 7:
        maxime(d, 115, 430, 1.0, t, "smile")
        d.rounded_rectangle(R(185, 360, 300, 420), radius=14 * K, fill="white", outline=BLACK, width=LW)
        d.polygon([P(200, 418), P(195, 438), P(215, 418)], fill="white", outline=BLACK)
        d.text(P(242, 380), "Moi : entre", font=f(11), fill=BLACK, anchor="mm")
        d.text(P(242, 400), "… et … €", font=f(14), fill=GREEN, anchor="mm")
        tag(d, 242, 460, "💬 Commente", RED, sz=11) if False else tag(d, 242, 460, "COMMENTE", RED, sz=11)

m.illus = illus

def build_audio(path):
    S = m.SCENES; SR = m.SR
    total = sum(s[2] for s in S); buf = np.zeros(int(total * SR) + SR)
    def add(x, at):
        s = int(at * SR); buf[s:s + len(x)] += x[:len(buf) - s]
    t0 = 0
    for i, (text, hl, dur) in enumerate(S):
        if i > 0: add(whoosh(), max(0, t0 - 0.12))
        if not os.environ.get('NOTEXT'):
            for k in range(len(text.split(" "))): add(pop() * 0.6, t0 + k * WORD_T)
        if i == 0: add(buzz(), t0 + 0.05)
        if i == 1: add(riser(1.2), t0 + 0.1)
        if i == 2: add(buzz() * 0.8, t0 + 0.4)
        if i == 3: add(scratch(1.5), t0 + 1.2)
        if i == 4: add(heartbeat(), t0 + 0.4); add(ding() * 0.6, t0 + dur * 0.75)
        if i == 5: add(ding(), t0 + 0.05); add(coins(), t0 + 0.6)
        if i == 6: add(coins(), t0 + 0.3)
        if i == 7: add(ding() * 0.6, t0 + 0.4)
        t0 += dur
    buf = buf[:int(total * SR)]; buf = buf / max(1e-6, np.abs(buf).max()) * 0.8
    import wave
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((buf * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    OUT = m.OUT; mode = sys.argv[2] if len(sys.argv) > 2 else "all"
    if mode == "contact":
        from PIL import Image, ImageDraw
        sheet = Image.new("RGB", (270 * 4, 480 * 2), "white")
        for i, (text, hl, dur) in enumerate(m.SCENES):
            im = Image.new("RGB", (SW, SH), BG); d = ImageDraw.Draw(im)
            illus(i, d, dur * 0.8, dur); draw_text(d, layout_text(d, text, hl), 99)
            sheet.paste(im.resize((270, 480)), ((i % 4) * 270, (i // 4) * 480))
        sheet.save(f"{OUT}/contact.png")
    else:
        from multiprocessing import Pool
        with Pool(2) as pool: pool.map(m.render_scene, range(len(m.SCENES)))
        with open(f"{OUT}/list.txt", "w") as fl:
            for i in range(len(m.SCENES)): fl.write(f"file 's{i}.mp4'\n")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{OUT}/list.txt", "-c", "copy", f"{OUT}/video.mp4"], check=True)
        build_audio(f"{OUT}/sfx.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/video.mp4", "-i", f"{OUT}/sfx.wav", "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", f"{OUT}/final.mp4"], check=True)
