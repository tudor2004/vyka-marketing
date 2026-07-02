"""Animated vyka.ro outro (3s, 1080x1920) — wordmark fades/drifts in, terracotta
hairline sweeps, tagline appears. Frames -> mp4 via ffmpeg (light)."""
import subprocess, pathlib, shutil
import imageio_ffmpeg
from PIL import Image, ImageDraw
import brand as B

R = pathlib.Path(__file__).resolve().parent.parent
OUT = R / "out"; WORK = R / "out/work"; WORK.mkdir(parents=True, exist_ok=True); TMP = R / "_outro";
if TMP.exists(): shutil.rmtree(TMP)
TMP.mkdir()
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS, N = 1080, 1920, 30, 90  # 3s


def ramp(f, a, b):
    if f <= a: return 0.0
    if f >= b: return 1.0
    t = (f - a) / (b - a)
    return t * t * (3 - 2 * t)


cx, cy = W // 2, H // 2
wf = B.font("serif", 150)
kf = B.font("sans", 30)
tf = B.font("sans", 34)
for f in range(N):
    im = Image.new("RGB", (W, H), B.BG)
    d = ImageDraw.Draw(im)
    # kicker
    ka = ramp(f, 0, 14)
    ktxt = " ".join("VYKA")
    kw = d.textlength(ktxt, font=kf)
    d.text((cx - kw / 2, cy - 150 + int((1 - ka) * 12)),
           ktxt, font=kf, fill=tuple(round(B.BG[i] + (B.TEXT_MUTED[i] - B.BG[i]) * ka) for i in range(3)))
    # wordmark vyka.ro — fade + slight upward drift
    wa = ramp(f, 6, 30)
    word = "vyka.ro"
    ww = d.textlength(word, font=wf)
    yoff = int((1 - wa) * 24)
    col = tuple(round(B.BG[i] + (B.HEADING[i] - B.BG[i]) * wa) for i in range(3))
    d.text((cx - ww / 2, cy - 80 + yoff), word, font=wf, fill=col)
    # terracotta hairline sweep under the wordmark
    sw = ramp(f, 26, 58)
    if sw > 0:
        full = int(ww * 0.9)
        x0 = cx - full / 2
        d.rectangle([x0, cy + 110, x0 + full * sw, cy + 114], fill=B.ACCENT)
    # tagline
    ta = ramp(f, 52, 78)
    if ta > 0:
        tt = "Designul camerei tale, reimaginat."
        tw = d.textlength(tt, font=tf)
        d.text((cx - tw / 2, cy + 150),
               tt, font=tf, fill=tuple(round(B.BG[i] + (B.BODY[i] - B.BG[i]) * ta) for i in range(3)))
    im.save(TMP / f"f{f:03d}.png")

final = WORK / "a3_outro.mp4"
subprocess.run([FF, "-y", "-loglevel", "error", "-framerate", str(FPS),
                "-i", str(TMP / "f%03d.png"),
                "-vf", "format=yuv420p", "-r", str(FPS), "-c:v", "libx264",
                "-preset", "veryfast", "-crf", "20", str(final)], check=True)
shutil.rmtree(TMP)
print("wrote", final, final.stat().st_size)
