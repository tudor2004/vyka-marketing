"""Calm 'Camera pe care o amâni' reel (1080x1920). Softer music, slower pace.
hook -> phone(vyka.ro) -> reveal(Veo) -> real-products proof -> CTA -> outro."""
import subprocess, pathlib, math, wave
import numpy as np
import imageio_ffmpeg

R = pathlib.Path(__file__).parent
OUT = R / "out"; TMP = R / "_cb"; TMP.mkdir(exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
SEGS = [("img", OUT / "c_hook.png", 4.0),
        ("img", OUT / "c_phone.png", 3.2),
        ("vid", OUT / "ee_veo_9x16.mp4", 5.5),
        ("img", OUT / "ee_shop_9x16.png", 3.5),
        ("img", OUT / "c_cta.png", 2.2),
        ("vid", OUT / "a3_outro.mp4", 3.0)]
TOTAL = sum(s[2] for s in SEGS)
VO = [("_vo/l1.mp3", 0.4), ("_vo/l2.mp3", 4.3), ("_vo/l3.mp3", 7.6),
      ("_vo/l4.mp3", 13.2), ("_vo/l5.mp3", 17.0)]


def music(path, dur, sr=44100):
    """Calm bed: warm pad forward, very soft slow pulse."""
    n = int(dur * sr); t = np.arange(n) / sr
    chords = [[174.6, 220, 261.6, 329.6], [196, 246.9, 293.7, 392],
              [220, 261.6, 329.6, 440], [164.8, 207.7, 261.6, 329.6]]
    seg = 4.0; pad = np.zeros(n)
    for i in range(int(math.ceil(dur / seg))):
        ch = chords[i % len(chords)]; s, e = int(i * seg * sr), min(n, int((i + 1) * seg * sr)); m = e - s
        if m <= 0: break
        env = np.sin(np.linspace(0, math.pi, m)) ** 0.7
        for f in ch: pad[s:e] += np.sin(2 * math.pi * f * t[s:e]) * env
    pad /= (np.max(np.abs(pad)) + 1e-9)
    pulse = np.zeros(n); beat = 60 / 68; kd = int(0.16 * sr); ke = np.exp(-np.linspace(0, 5, kd)); bt = 0.0
    while bt < dur:
        s = int(bt * sr)
        if s + kd <= n: pulse[s:s + kd] += np.sin(2 * math.pi * np.linspace(90, 50, kd) * (np.arange(kd) / sr)) * ke
        bt += beat
    mix = 0.32 * pad + 0.12 * pulse; mix /= (np.max(np.abs(mix)) + 1e-9); mix *= 0.8
    pcm = (mix * 32767).astype("<i2"); st = np.repeat(pcm[:, None], 2, axis=1).tobytes()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(st)


def ff(a): subprocess.run([FF, "-y", "-loglevel", "error", *a], check=True)
VF = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,format=yuv420p"

parts = []
for i, (kind, src, dur) in enumerate(SEGS):
    o = TMP / f"s{i:02d}.mp4"
    base = ["-loop", "1", "-t", str(dur), "-i", str(src)] if kind == "img" else ["-t", str(dur), "-i", str(src)]
    ff([*base, "-vf", VF, "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-an", str(o)])
    parts.append(o)
(TMP / "list.txt").write_text("".join(f"file '{p}'\n" for p in parts))
ff(["-f", "concat", "-safe", "0", "-i", str(TMP / "list.txt"), "-c", "copy", str(TMP / "silent.mp4")])
music(TMP / "bed.wav", TOTAL)
inp = ["-i", str(TMP / "silent.mp4"), "-i", str(TMP / "bed.wav")]
for f, _ in VO: inp += ["-i", str(R / f)]
fc = "[1:a]volume=0.26[m];"; labels = ["[m]"]
for idx, (f, off) in enumerate(VO):
    fc += f"[{idx+2}:a]aformat=channel_layouts=stereo,adelay={int(off*1000)}:all=1,volume=1.0[a{idx}];"
    labels.append(f"[a{idx}]")
fc += "".join(labels) + f"amix=inputs={len(labels)}:duration=longest:normalize=0,alimiter=limit=0.95[aout]"
final = OUT / "c_reel_1080.mp4"
ff([*inp, "-filter_complex", fc, "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac",
    "-b:a", "160k", "-shortest", str(final)])
print("FINAL", final, final.stat().st_size, "dur", round(TOTAL, 1))
