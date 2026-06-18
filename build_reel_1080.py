"""Re-render the Reel at 1080x1920, reusing the already-timed audio from the
720p VO reel (no ElevenLabs re-call). Same beats/durations."""
import subprocess, pathlib
import imageio_ffmpeg
from PIL import Image, ImageDraw
import brand as B

R = pathlib.Path(__file__).parent
OUT = R / "out"; TMP = R / "_rb1080"; TMP.mkdir(exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
DUR = {"s1": 2.6, "s2": 5.0, "s3": 4.5, "s4": 4.6}
SRC_REEL = OUT / "ee_reel_vo_9x16.mp4"   # has the timed VO+music


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
    d = ImageDraw.Draw(card); pad = 72
    B.kicker(d, (pad, H - pad - 226), fill=B.WHITE, size=30)
    d.line([(pad, H - pad - 180), (pad + 74, H - pad - 180)], fill=B.WHITE, width=3)
    d.text((pad, H - pad - 150), "Așa arată acum.", font=B.font("serif", 86), fill=B.WHITE)
    p = TMP / "title.png"; card.save(p); return p


def ff(args): subprocess.run([FF, "-y", "-loglevel", "error", *args], check=True)
VF = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,format=yuv420p"


def img_seg(img, dur, out):
    ff(["-loop", "1", "-t", str(dur), "-i", str(img), "-vf", VF, "-r", str(FPS),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-an", str(out)])


def vid_seg(vid, dur, out):
    ff(["-t", str(dur), "-i", str(vid), "-vf", VF, "-r", str(FPS),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-an", str(out)])


tb = before_card()
segs = [(TMP / "s1.mp4", lambda o: img_seg(tb, DUR["s1"], o)),
        (TMP / "s2.mp4", lambda o: vid_seg(OUT / "ee_veo_9x16.mp4", DUR["s2"], o)),
        (TMP / "s3.mp4", lambda o: img_seg(OUT / "ee_shop_9x16.png", DUR["s3"], o)),
        (TMP / "s4.mp4", lambda o: img_seg(OUT / "ee_hero_9x16.png", DUR["s4"], o))]
for p, fn in segs:
    fn(p); print("seg", p.name, "ok")
(TMP / "list.txt").write_text("".join(f"file '{p}'\n" for p, _ in segs))
ff(["-f", "concat", "-safe", "0", "-i", str(TMP / "list.txt"), "-c", "copy", str(TMP / "silent.mp4")])
# pull timed audio from the existing reel + mux
ff(["-i", str(SRC_REEL), "-vn", "-c:a", "copy", str(TMP / "audio.m4a")])
final = OUT / "ee_reel_vo_1080.mp4"
ff(["-i", str(TMP / "silent.mp4"), "-i", str(TMP / "audio.m4a"),
    "-c:v", "copy", "-c:a", "copy", "-shortest", str(final)])
print("FINAL", final, final.stat().st_size)
