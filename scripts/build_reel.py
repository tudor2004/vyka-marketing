"""Assemble the full Reel into ONE mp4 — light path (drive ffmpeg on files, no
raw-frame piping; 720x1280). Segments: before(+hook) -> after(Veo) -> shoppable
-> CTA. Adds a soft generated ambient music bed. Brand-styled via brand.py."""
import subprocess, pathlib, struct, math, wave
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw
import brand as B

R = pathlib.Path(__file__).resolve().parent.parent
OUT = R / "out"; WORK = R / "out/work"; WORK.mkdir(parents=True, exist_ok=True)
TMP = R / "_reelbuild"
TMP.mkdir(exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 720, 1280, 30


def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    nw, nh = round(im.width * s), round(im.height * s)
    im = im.resize((nw, nh), Image.LANCZOS)
    return im.crop(((nw - w) // 2, (nh - h) // 2, (nw - w) // 2 + w, (nh - h) // 2 + h))


# 1) Before title card (720x1280) with hook
def before_card():
    card = cover(Image.open(R / "src/ee0fa358/before.jpg").convert("RGB"), W, H)
    scrim = Image.new("L", (1, H), 0)
    for y in range(H):
        t = max(0.0, (y - H * 0.5) / (H * 0.5))
        scrim.putpixel((0, y), int(190 * (t ** 1.4)))
    card = Image.composite(Image.new("RGB", (W, H), B.INK_700), card, scrim.resize((W, H)))
    d = ImageDraw.Draw(card)
    pad = 48
    B.kicker(d, (pad, H - pad - 150), fill=B.WHITE, size=20)
    d.line([(pad, H - pad - 120), (pad + 50, H - pad - 120)], fill=B.WHITE, width=2)
    d.text((pad, H - pad - 100), "Așa arată acum.", font=B.font("serif", 58), fill=B.WHITE)
    p = TMP / "title_before.png"
    card.save(p)
    return p


# 2) Soft ambient music bed (warm pad + gentle kick), ~16s
def music(path, dur=16.0, sr=44100):
    n = int(dur * sr)
    t = np.arange(n) / sr
    chords = [[220.0, 261.6, 329.6, 440.0],   # Am
              [174.6, 220.0, 261.6, 349.2],   # F
              [261.6, 329.6, 392.0, 523.3],   # C
              [196.0, 246.9, 392.0, 392.0]]   # G
    seg = dur / len(chords)
    pad = np.zeros(n)
    for i, ch in enumerate(chords):
        s, e = int(i * seg * sr), int((i + 1) * seg * sr)
        m = e - s
        env = np.sin(np.linspace(0, math.pi, m)) ** 0.6  # slow swell
        for f in ch:
            pad[s:e] += np.sin(2 * math.pi * f * t[s:e]) * env
    pad /= (np.max(np.abs(pad)) + 1e-9)
    # gentle kick at 90 BPM
    kick = np.zeros(n)
    beat = 60.0 / 90.0
    kdur = int(0.13 * sr)
    ke = np.exp(-np.linspace(0, 6, kdur))
    bt = 0.0
    while bt < dur:
        s = int(bt * sr)
        if s + kdur <= n:
            sweep = np.sin(2 * math.pi * np.linspace(120, 48, kdur) * (np.arange(kdur) / sr))
            kick[s:s + kdur] += sweep * ke
        bt += beat
    mix = 0.20 * pad + 0.45 * kick
    mix /= (np.max(np.abs(mix)) + 1e-9)
    mix *= 0.85
    pcm = (mix * 32767).astype("<i2")
    stereo = np.repeat(pcm[:, None], 2, axis=1).tobytes()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(stereo)


def ff(args):
    subprocess.run([FF, "-y", "-loglevel", "error", *args], check=True)


VF = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,format=yuv420p"


def img_seg(img, dur, out):
    ff(["-loop", "1", "-t", str(dur), "-i", str(img), "-vf", VF, "-r", str(FPS),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-an", str(out)])


def vid_seg(vid, dur, out):
    ff(["-t", str(dur), "-i", str(vid), "-vf", VF, "-r", str(FPS),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-an", str(out)])


def main():
    tb = before_card()
    segs = [
        ("s1", lambda o: img_seg(tb, 2.5, o)),
        ("s2", lambda o: vid_seg(WORK / "ee_veo_9x16.mp4", 5.0, o)),
        ("s3", lambda o: img_seg(OUT / "ee_shop_9x16.png", 4.5, o)),
        ("s4", lambda o: img_seg(OUT / "ee_hero_9x16.png", 4.0, o)),
    ]
    files = []
    for name, fn in segs:
        p = TMP / f"{name}.mp4"
        fn(p); files.append(p)
        print("seg", name, "ok")
    # concat (same params -> stream copy)
    lst = TMP / "list.txt"
    lst.write_text("".join(f"file '{f}'\n" for f in files))
    silent = TMP / "silent.mp4"
    ff(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)])
    print("concat ok")
    mp3 = TMP / "bed.wav"
    music(mp3, dur=16.0)
    print("music ok")
    final = OUT / "ee_reel_9x16.mp4"
    ff(["-i", str(silent), "-i", str(mp3), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
        "-shortest", str(final)])
    print("FINAL", final, final.stat().st_size)


main()
