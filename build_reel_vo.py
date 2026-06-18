"""Full Reel WITH Romanian voiceover (ElevenLabs mp3s in _vo/) + music bed,
ducked under the voice. Light ffmpeg-on-files path, 720x1280."""
import subprocess, pathlib, math, wave
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw
import brand as B

R = pathlib.Path(__file__).parent
OUT = R / "out"; TMP = R / "_rb"; TMP.mkdir(exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 720, 1280, 30
# segment durations tuned so each VO line fits its beat
DUR = {"s1": 2.6, "s2": 5.0, "s3": 6.8, "s4": 4.9}
TOTAL = sum(DUR.values())  # 17.0
# absolute VO start offsets (s) + line files
VO = [("_vo/l1.mp3", 0.4),
      ("_vo/l2.mp3", DUR["s1"] + 0.4),
      ("_vo/l3.mp3", DUR["s1"] + DUR["s2"] + 0.35),
      ("_vo/l4.mp3", DUR["s1"] + DUR["s2"] + DUR["s3"] + 0.4)]


def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    nw, nh = round(im.width * s), round(im.height * s)
    im = im.resize((nw, nh), Image.LANCZOS)
    return im.crop(((nw - w) // 2, (nh - h) // 2, (nw - w) // 2 + w, (nh - h) // 2 + h))


def before_card():
    card = cover(Image.open(R / "src/ee_before.jpg").convert("RGB"), W, H)
    sc = Image.new("L", (1, H), 0)
    for y in range(H):
        t = max(0.0, (y - H * 0.5) / (H * 0.5)); sc.putpixel((0, y), int(190 * (t ** 1.4)))
    card = Image.composite(Image.new("RGB", (W, H), B.INK_700), card, sc.resize((W, H)))
    d = ImageDraw.Draw(card); pad = 48
    B.kicker(d, (pad, H - pad - 150), fill=B.WHITE, size=20)
    d.line([(pad, H - pad - 120), (pad + 50, H - pad - 120)], fill=B.WHITE, width=2)
    d.text((pad, H - pad - 100), "Așa arată acum.", font=B.font("serif", 58), fill=B.WHITE)
    p = TMP / "title.png"; card.save(p); return p


def music(path, dur, sr=44100):
    n = int(dur * sr); t = np.arange(n) / sr
    chords = [[220, 261.6, 329.6, 440], [174.6, 220, 261.6, 349.2],
              [261.6, 329.6, 392, 523.3], [196, 246.9, 392, 392]]
    seg = dur / len(chords); pad = np.zeros(n)
    for i, ch in enumerate(chords):
        s, e = int(i * seg * sr), int((i + 1) * seg * sr); m = e - s
        env = np.sin(np.linspace(0, math.pi, m)) ** 0.6
        for f in ch:
            pad[s:e] += np.sin(2 * math.pi * f * t[s:e]) * env
    pad /= (np.max(np.abs(pad)) + 1e-9)
    kick = np.zeros(n); beat = 60 / 90; kd = int(0.13 * sr); ke = np.exp(-np.linspace(0, 6, kd))
    bt = 0.0
    while bt < dur:
        s = int(bt * sr)
        if s + kd <= n:
            kick[s:s + kd] += np.sin(2 * math.pi * np.linspace(120, 48, kd) * (np.arange(kd) / sr)) * ke
        bt += beat
    mix = 0.20 * pad + 0.45 * kick; mix /= (np.max(np.abs(mix)) + 1e-9); mix *= 0.85
    pcm = (mix * 32767).astype("<i2"); st = np.repeat(pcm[:, None], 2, axis=1).tobytes()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(st)


def ff(args): subprocess.run([FF, "-y", "-loglevel", "error", *args], check=True)
VF = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,format=yuv420p"


def img_seg(img, dur, out):
    ff(["-loop", "1", "-t", str(dur), "-i", str(img), "-vf", VF, "-r", str(FPS),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-an", str(out)])


def vid_seg(vid, dur, out):
    ff(["-t", str(dur), "-i", str(vid), "-vf", VF, "-r", str(FPS),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-an", str(out)])


def main():
    tb = before_card()
    segs = [(TMP / "s1.mp4", lambda o: img_seg(tb, DUR["s1"], o)),
            (TMP / "s2.mp4", lambda o: vid_seg(OUT / "ee_veo_9x16.mp4", DUR["s2"], o)),
            (TMP / "s3.mp4", lambda o: img_seg(OUT / "ee_shop_9x16.png", DUR["s3"], o)),
            (TMP / "s4.mp4", lambda o: img_seg(OUT / "ee_hero_9x16.png", DUR["s4"], o))]
    for p, fn in segs:
        fn(p)
    (TMP / "list.txt").write_text("".join(f"file '{p}'\n" for p, _ in segs))
    ff(["-f", "concat", "-safe", "0", "-i", str(TMP / "list.txt"), "-c", "copy", str(TMP / "silent.mp4")])
    music(TMP / "bed.wav", TOTAL)
    # build audio mix: music ducked + 4 VO lines placed
    inputs = ["-i", str(TMP / "silent.mp4"), "-i", str(TMP / "bed.wav")]
    for f, _ in VO:
        inputs += ["-i", str(R / f)]
    fc = "[1:a]volume=0.22[m];"
    labels = ["[m]"]
    for idx, (f, off) in enumerate(VO):
        ai = idx + 2
        ms = int(off * 1000)
        fc += f"[{ai}:a]aformat=channel_layouts=stereo,adelay={ms}:all=1,volume=1.0[a{idx}];"
        labels.append(f"[a{idx}]")
    fc += "".join(labels) + f"amix=inputs={len(labels)}:duration=longest:normalize=0,alimiter=limit=0.95[aout]"
    final = OUT / "ee_reel_vo_9x16.mp4"
    ff([*inputs, "-filter_complex", fc, "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", str(final)])
    print("FINAL", final, final.stat().st_size)


main()
