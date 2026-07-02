"""9:16 before->after wipe-reveal as a lightweight GIF (Pillow only, NO ffmpeg).
Downscaled to stay light. Also exports 3 key PNG frames for visual review.
Styled to match vyka.ro via brand.py."""
import pathlib
from PIL import Image, ImageDraw
import brand as B

R = pathlib.Path(__file__).resolve().parent.parent
OUT = R / "out"; WORK = R / "out/work"; WORK.mkdir(parents=True, exist_ok=True)
W, H = 540, 960          # half-res to stay light
FPS = 12
WHITE = B.WHITE


def cover(path, w, h):
    im = Image.open(path).convert("RGB")
    s = max(w / im.width, h / im.height)
    nw, nh = round(im.width * s), round(im.height * s)
    im = im.resize((nw, nh), Image.LANCZOS)
    return im.crop(((nw - w) // 2, (nh - h) // 2, (nw - w) // 2 + w, (nh - h) // 2 + h))


before = cover(R / "src/ee0fa358/before.jpg", W, H)
after = cover(R / "src/ee0fa358/after.png", W, H)

scrim = Image.new("L", (1, H), 0)
for y in range(H):
    t = max(0.0, (y - H * 0.55) / (H * 0.45))
    scrim.putpixel((0, y), int(200 * (t ** 1.4)))
scrim = scrim.resize((W, H))
black = Image.new("RGB", (W, H), B.INK_700)


def tag(d, text):
    f = B.font("bold", 18)
    s = " ".join(list(text.upper()))
    tw = d.textlength(s, font=f)
    x, y = 26, 36
    d.rectangle([x, y, x + tw + 26, y + 38], fill=B.INK_700)
    d.text((x + 13, y + 9), s, font=f, fill=WHITE)


def ease(t):
    return t * t * (3 - 2 * t)


def frame(p, show_band):
    img = before.copy()
    if p > 0:
        x = int(W * p)
        if x > 0:
            img.paste(after.crop((0, 0, x, H)), (0, 0))
    base = Image.composite(black, img, scrim)
    d = ImageDraw.Draw(base)
    if 0 < p < 1:
        x = int(W * p)
        d.line([(x, 0), (x, H)], fill=B.ACCENT, width=4)
    tag(d, "După" if p >= 0.5 else "Înainte")
    if show_band:
        pad = 38
        d.text((pad, H - pad - 16 - 50 - 34), " ".join("VYKA"), font=B.font("sans", 15), fill=WHITE)
        d.line([(pad, H - pad - 16 - 50 - 12), (pad + 38, H - pad - 16 - 50 - 12)], fill=WHITE, width=2)
        d.text((pad, H - pad - 16 - 50), "Camera ta, transformată.", font=B.font("serif", 40), fill=WHITE)
        d.text((pad, H - pad - 14), "Prima ta cameră, gratis · vyka.ro", font=B.font("sans", 17), fill=WHITE)
    return base


# timeline
frames = []
for _ in range(int(FPS * 0.8)):      # hold before
    frames.append(frame(0.0, False))
for k in range(int(FPS * 1.6)):      # wipe
    frames.append(frame(ease((k + 1) / (FPS * 1.6)), False))
for _ in range(int(FPS * 1.8)):      # hold after + band
    frames.append(frame(1.0, True))

frames[0].save(OUT / "ee_reveal.gif", save_all=True, append_images=frames[1:],
               duration=int(1000 / FPS), loop=0, optimize=True)
# key stills for review
frame(0.0, False).save(WORK / "kf_before.png")
frame(0.5, False).save(WORK / "kf_wipe.png")
frame(1.0, True).save(WORK / "kf_after.png")
sz = (OUT / "ee_reveal.gif").stat().st_size // 1024
print(f"wrote ee_reveal.gif {len(frames)} frames {W}x{H} {sz}KB + 3 key stills")
