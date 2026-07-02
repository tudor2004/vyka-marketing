"""Phone sequence for scenario v3 (1080x1920): snap the old room -> it lands in
vyka.ro on a phone -> quick wizard steps -> the design resolves -> zoom into the
phone. Real UI screenshots composited into a phone mockup. Frames -> mp4."""
import subprocess, pathlib, shutil
import imageio_ffmpeg
from PIL import Image, ImageDraw
import brand as B

R = pathlib.Path(__file__).resolve().parent.parent
OUT = R / "out"; WORK = R / "out/work"; WORK.mkdir(parents=True, exist_ok=True); UI = R / "ui"; TMP = R / "_phoneseq"
if TMP.exists(): shutil.rmtree(TMP)
TMP.mkdir()
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
SW, SH = 520, 1126            # phone screen size
BODY_W, BODY_H = SW + 30, SH + 30
CX, CY = W // 2, H // 2


def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    nw, nh = round(im.width * s), round(im.height * s)
    im = im.resize((nw, nh), Image.LANCZOS)
    return im.crop(((nw - w) // 2, (nh - h) // 2, (nw - w) // 2 + w, (nh - h) // 2 + h))


def rounded_mask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w, h], radius=r, fill=255)
    return m


def phone(screen_img):
    """Return an RGBA phone mockup at 1x with screen_img (already SWxSH) inside."""
    body = Image.new("RGBA", (BODY_W, BODY_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(body)
    d.rounded_rectangle([0, 0, BODY_W, BODY_H], radius=56, fill=(18, 16, 14, 255))
    sc = screen_img.convert("RGB").resize((SW, SH), Image.LANCZOS)
    body.paste(sc, (15, 15), rounded_mask(SW, SH, 42))
    # notch
    nw, nh = 150, 34
    d.rounded_rectangle([(BODY_W - nw) // 2, 20, (BODY_W + nw) // 2, 20 + nh], radius=17, fill=(18, 16, 14, 255))
    return body


def screen(name): return Image.open(UI / name).convert("RGB")


def result_screen():
    """Faux 'your design' result screen for the phone."""
    s = Image.new("RGB", (SW, SH), B.BG)
    d = ImageDraw.Draw(s)
    d.text((28, 30), " ".join("VYKA"), font=B.font("sans", 18), fill=B.TEXT_MUTED)
    d.text((28, 58), "Designul tău", font=B.font("serif", 40), fill=B.HEADING)
    img = cover(Image.open(R / "src/a3cdba11/after.png").convert("RGB"), SW - 40, 620)
    s.paste(img, (20, 130))
    d.text((28, 770), "14 produse · 16.135 lei", font=B.font("bold", 26), fill=B.HEADING)
    d.text((28, 808), "din magazine disponibile în România", font=B.font("sans", 19), fill=B.TEXT_MUTED)
    d.rounded_rectangle([20, 1010, SW - 20, 1086], radius=8, fill=B.ACCENT)
    t = "Deblochează gratis"
    d.text(((SW - d.textlength(t, font=B.font("bold", 26))) // 2, 1032), t, font=B.font("bold", 26), fill=B.BG)
    return s


def caption(d, text, sub=None):
    f = B.font("serif", 58)
    tw = d.textlength(text, font=f)
    y = H - 230
    # soft pill
    d.text(((W - tw) // 2, y), text, font=f, fill=B.HEADING)
    if sub:
        sf = B.font("sans", 30); sw = d.textlength(sub, font=sf)
        d.text(((W - sw) // 2, y + 76), sub, font=sf, fill=B.TEXT_MUTED)


def base():
    return Image.new("RGB", (W, H), B.BG)


def place_phone(img, ph, scale=1.0, alpha=255):
    if scale != 1.0:
        ph = ph.resize((round(ph.width * scale), round(ph.height * scale)), Image.LANCZOS)
    if alpha < 255:
        a = ph.split()[3].point(lambda v: v * alpha // 255)
        ph.putalpha(a)
    img.paste(ph, (CX - ph.width // 2, CY - ph.height // 2), ph)


def ease(t): return t * t * (3 - 2 * t)


fi = 0
def save(img):
    global fi
    img.save(TMP / f"f{fi:04d}.png"); fi += 1


# pre-render phones
ph_step1 = phone(screen("vyka_step1_filled.png"))
ph_step2 = phone(screen("vyka_step2_style.png"))
ph_step3 = phone(screen("vyka_step3_palette.png"))
ph_result = phone(screen("vyka_result_clean.png"))
before_full = cover(Image.open(R / "src/a3cdba11/before.jpg").convert("RGB"), W, H)

# A) snap the old room
for k in range(30):
    im = before_full.copy(); d = ImageDraw.Draw(im)
    # darken slightly + caption
    sc = Image.new("L", (1, H), 0)
    for y in range(H):
        t = max(0.0, (y - H * 0.62) / (H * 0.38)); sc.putpixel((0, y), int(170 * (t ** 1.3)))
    im = Image.composite(Image.new("RGB", (W, H), B.INK_700), im, sc.resize((W, H)))
    d = ImageDraw.Draw(im); caption(d, "Faci o poză.", "camerei tale")
    save(im)
for k in range(5):  # flash
    save(Image.new("RGB", (W, H), (255, 255, 255)))

# B) phone pops in with the upload screen
for k in range(16):
    t = ease((k + 1) / 16); im = base()
    place_phone(im, ph_step1, scale=0.86 + 0.14 * t, alpha=int(255 * t))
    d = ImageDraw.Draw(im); caption(d, "O încarci pe", "vyka.ro")
    save(im)
# C) wizard steps
for ph, cap in [(ph_step1, ("Alegi stilul", None)), (ph_step2, ("Alegi stilul", None)), (ph_step3, ("…și paleta", None))]:
    hold = 14 if ph is ph_step1 else 22
    for k in range(hold):
        im = base(); place_phone(im, ph); d = ImageDraw.Draw(im); caption(d, *cap); save(im)
# D) result resolves
for k in range(28):
    im = base(); place_phone(im, ph_result)
    d = ImageDraw.Draw(im); caption(d, "Primești designul.", None); save(im)
# E) zoom into the phone screen
for k in range(22):
    t = ease((k + 1) / 22); im = base()
    place_phone(im, ph_result, scale=1.0 + 1.25 * t)
    save(im)

out = WORK / "a3v3_phone.mp4"
subprocess.run([FF, "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(TMP / "f%04d.png"),
                "-vf", "format=yuv420p", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast",
                "-crf", "21", str(out)], check=True)
shutil.rmtree(TMP)
print("wrote", out, out.stat().st_size, "frames", fi, f"{fi/FPS:.1f}s")
