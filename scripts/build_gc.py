"""Assemble the 'Garsonieră comunistă -> glow-up' reel (1080x1920, ~19s).
hook(before) -> reveal(after push-in) -> shoppable proof -> CTA -> vyka.ro outro.

Self-contained: the reveal is a local Ken-Burns push-in on after.png (NO Veo
needed). Voiceover is OPTIONAL — if ElevenLabs line mp3s exist in _vo/ they are
ducked over the music bed; otherwise the reel ships music-only. Run after
make_gc_elements.py. Usage: python scripts/build_gc.py [campaign=gc01]"""
import subprocess, pathlib, math, wave, sys
import numpy as np
import imageio_ffmpeg

R = pathlib.Path(__file__).resolve().parent.parent
OUT = R / "out"; WORK = R / "out/work"; WORK.mkdir(parents=True, exist_ok=True)
TMP = R / "_gcb"; TMP.mkdir(exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
CAMP = sys.argv[1] if len(sys.argv) > 1 else "gc01"
SRC = R / "src" / CAMP

# (kind, source, seconds) — "push" = Ken-Burns zoom-in on a still
SEGS = [("img",  WORK / "gc_hook.png",      4.0),
        ("push", SRC / "after.png",         5.0),
        ("img",  OUT / "gc_shop_9x16.png",  4.5),
        ("img",  WORK / "gc_cta.png",       3.0),
        ("vid",  WORK / "a3_outro.mp4",     3.0)]
TOTAL = sum(s[2] for s in SEGS)
# VO line -> start offset (s). Files are optional; missing ones are skipped.
VO = [("_vo/l1.mp3", 0.4), ("_vo/l2.mp3", 4.3), ("_vo/l3.mp3", 6.8),
      ("_vo/l4.mp3", 9.6), ("_vo/l5.mp3", 14.2)]
VO = [(f, off) for f, off in VO if (R / f).exists()]


def music(path, dur, sr=44100):
    """Warm, nostalgic pad bed with a very soft slow pulse."""
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


def push_filter(dur):
    # smooth slow zoom-in from a SINGLE input frame. zoompan d = TOTAL output
    # frames here (one input image, no -loop), so this is fast and bounded.
    frames = int(dur * FPS)
    return (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"zoompan=z='min(zoom+0.0010,1.16)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={frames}:s={W}x{H}:fps={FPS},setsar=1,format=yuv420p")


parts = []
for i, (kind, src, dur) in enumerate(SEGS):
    o = TMP / f"s{i:02d}.mp4"
    if kind == "vid":
        ff(["-t", str(dur), "-i", str(src), "-vf", VF, "-r", str(FPS),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-an", str(o)])
    elif kind == "push":
        # single image in, zoompan emits exactly dur*FPS frames (no -loop!)
        ff(["-i", str(src), "-vf", push_filter(dur), "-frames:v", str(int(dur * FPS)),
            "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-an", str(o)])
    else:  # img hold
        ff(["-loop", "1", "-t", str(dur), "-i", str(src), "-vf", VF, "-r", str(FPS),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-an", str(o)])
    parts.append(o)

(TMP / "list.txt").write_text("".join(f"file '{p}'\n" for p in parts))
ff(["-f", "concat", "-safe", "0", "-i", str(TMP / "list.txt"), "-c", "copy", str(TMP / "silent.mp4")])
music(TMP / "bed.wav", TOTAL)

final = OUT / "gc_reel_1080.mp4"
if VO:
    inp = ["-i", str(TMP / "silent.mp4"), "-i", str(TMP / "bed.wav")]
    for f, _ in VO: inp += ["-i", str(R / f)]
    fc = "[1:a]volume=0.26[m];"; labels = ["[m]"]
    for idx, (f, off) in enumerate(VO):
        fc += f"[{idx+2}:a]aformat=channel_layouts=stereo,adelay={int(off*1000)}:all=1,volume=1.0[a{idx}];"
        labels.append(f"[a{idx}]")
    fc += "".join(labels) + f"amix=inputs={len(labels)}:duration=longest:normalize=0,alimiter=limit=0.95[aout]"
    ff([*inp, "-filter_complex", fc, "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac",
        "-b:a", "160k", "-shortest", str(final)])
    print("FINAL (with VO)", final, final.stat().st_size, "dur", round(TOTAL, 1))
else:
    ff(["-i", str(TMP / "silent.mp4"), "-i", str(TMP / "bed.wav"),
        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", str(final)])
    print("FINAL (music only — add _vo/ mp3s for voiceover)", final, final.stat().st_size, "dur", round(TOTAL, 1))
