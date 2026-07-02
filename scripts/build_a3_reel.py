"""Assemble the longer TikTok-style reel for a3cdba11 — 1080x1920.
hook -> Veo reveal -> 6 product cards -> USP -> CTA -> animated vyka.ro outro.
Luisa VO + ducked music. Light ffmpeg-on-files path."""
import subprocess, pathlib, math, wave
import numpy as np
import imageio_ffmpeg
import brand as B

R = pathlib.Path(__file__).resolve().parent.parent
OUT = R / "out"; WORK = R / "out/work"; WORK.mkdir(parents=True, exist_ok=True); TMP = R / "_a3b"; TMP.mkdir(exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30

# (kind, source, duration)
MONT = 1.6
SEGS = [("img", WORK / "a3_hook.png", 3.0),
        ("vid", WORK / "a3_veo_9x16.mp4", 5.0),
        ("img", WORK / "a3_p1.png", MONT), ("img", WORK / "a3_p2.png", MONT),
        ("img", WORK / "a3_p3.png", MONT), ("img", WORK / "a3_p4.png", MONT),
        ("img", WORK / "a3_p5.png", MONT), ("img", WORK / "a3_p6.png", MONT),
        ("img", OUT / "a3_shop_9x16.png", 4.0),
        ("img", WORK / "a3_cta.png", 2.8),
        ("vid", WORK / "a3_outro.mp4", 3.0)]
TOTAL = sum(s[2] for s in SEGS)  # 27.4

# VO line -> absolute start offset
def at(*names):
    t = 0.0
    pos = {}
    return pos
VO = [("_vo/l1.mp3", 0.3),
      ("_vo/l2.mp3", 3.4),
      ("_vo/l3.mp3", 8.3),
      ("_vo/l4.mp3", 18.0),
      ("_vo/l5.mp3", 21.8)]


def music(path, dur, sr=44100):
    n = int(dur * sr); t = np.arange(n) / sr
    chords = [[220, 261.6, 329.6, 440], [174.6, 220, 261.6, 349.2],
              [261.6, 329.6, 392, 523.3], [196, 246.9, 392, 392]]
    seg = 4.0; pad = np.zeros(n)
    for i in range(int(math.ceil(dur / seg))):
        ch = chords[i % len(chords)]
        s, e = int(i * seg * sr), min(n, int((i + 1) * seg * sr)); m = e - s
        if m <= 0: break
        env = np.sin(np.linspace(0, math.pi, m)) ** 0.6
        for f in ch:
            pad[s:e] += np.sin(2 * math.pi * f * t[s:e]) * env
    pad /= (np.max(np.abs(pad)) + 1e-9)
    kick = np.zeros(n); beat = 60 / 92; kd = int(0.13 * sr); ke = np.exp(-np.linspace(0, 6, kd)); bt = 0.0
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


def main():
    parts = []
    for i, (kind, src, dur) in enumerate(SEGS):
        o = TMP / f"s{i:02d}.mp4"
        if kind == "img":
            ff(["-loop", "1", "-t", str(dur), "-i", str(src), "-vf", VF, "-r", str(FPS),
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-an", str(o)])
        else:
            ff(["-t", str(dur), "-i", str(src), "-vf", VF, "-r", str(FPS),
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-an", str(o)])
        parts.append(o)
    (TMP / "list.txt").write_text("".join(f"file '{p}'\n" for p in parts))
    ff(["-f", "concat", "-safe", "0", "-i", str(TMP / "list.txt"), "-c", "copy", str(TMP / "silent.mp4")])
    music(TMP / "bed.wav", TOTAL)
    inputs = ["-i", str(TMP / "silent.mp4"), "-i", str(TMP / "bed.wav")]
    for f, _ in VO:
        inputs += ["-i", str(R / f)]
    fc = "[1:a]volume=0.20[m];"
    labels = ["[m]"]
    for idx, (f, off) in enumerate(VO):
        ms = int(off * 1000)
        fc += f"[{idx+2}:a]aformat=channel_layouts=stereo,adelay={ms}:all=1,volume=1.0[a{idx}];"
        labels.append(f"[a{idx}]")
    fc += "".join(labels) + f"amix=inputs={len(labels)}:duration=longest:normalize=0,alimiter=limit=0.95[aout]"
    final = OUT / "a3_reel_1080.mp4"
    ff([*inputs, "-filter_complex", fc, "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", str(final)])
    print("FINAL", final, final.stat().st_size, "dur", TOTAL)


main()
