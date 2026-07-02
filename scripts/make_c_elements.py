"""Elements for the calm 'Camera pe care o amâni' reel (1080x1920).
hook (before + soft caption), phone-with-vyka.ro, soft CTA. Brand-styled."""
import pathlib
from PIL import Image, ImageDraw
import brand as B

R = pathlib.Path(__file__).resolve().parent.parent
OUT = R / "out"; WORK = R / "out/work"; WORK.mkdir(parents=True, exist_ok=True); UI = R / "ui"
W, H = 1080, 1920


def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    nw, nh = round(im.width * s), round(im.height * s)
    im = im.resize((nw, nh), Image.LANCZOS)
    return im.crop(((nw - w) // 2, (nh - h) // 2, (nw - w) // 2 + w, (nh - h) // 2 + h))


def grad(im, top=False, bottom=True, strength=185):
    sc = Image.new("L", (1, H), 0)
    for y in range(H):
        t = 0.0
        if bottom and y > H * 0.52: t = max(t, (y - H * 0.52) / (H * 0.48))
        if top and y < H * 0.30: t = max(t, (H * 0.30 - y) / (H * 0.30))
        sc.putpixel((0, y), int(strength * (t ** 1.35)))
    return Image.composite(Image.new("RGB", (W, H), B.INK_700), im, sc.resize((W, H)))


def rounded_mask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w, h], radius=r, fill=255)
    return m


def phone(screen_path):
    SW, SH = 520, 1126
    body = Image.new("RGBA", (SW + 30, SH + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(body)
    d.rounded_rectangle([0, 0, SW + 30, SH + 30], radius=56, fill=(18, 16, 14, 255))
    sc = Image.open(screen_path).convert("RGB").resize((SW, SH), Image.LANCZOS)
    body.paste(sc, (15, 15), rounded_mask(SW, SH, 42))
    nw, nh = 150, 34
    d.rounded_rectangle([(SW + 30 - nw) // 2, 20, (SW + 30 + nw) // 2, 20 + nh], radius=17, fill=(18, 16, 14, 255))
    return body


# HOOK — dated room + soft serif caption
hook = grad(cover(Image.open(R / "src/ee0fa358/before.jpg").convert("RGB"), W, H), bottom=True, strength=175)
d = ImageDraw.Draw(hook)
B.kicker(d, (60, H - 360), fill=B.WHITE, size=26)
d.text((60, H - 320), "Ai o cameră", font=B.font("serif", 78), fill=B.WHITE)
d.text((60, H - 232), "pe care o tot amâni.", font=B.font("serif", 78), fill=B.WHITE)
hook.save(WORK / "c_hook.png"); print("c_hook")

# PHONE with vyka.ro (the website beat)
card = Image.new("RGB", (W, H), B.BG)
ph = phone(UI / "vyka_landing.png")
card.paste(ph, (W // 2 - ph.width // 2, H // 2 - ph.height // 2 - 40), ph)
d = ImageDraw.Draw(card)
sub = "Totul începe cu o poză, pe"
d.text(((W - d.textlength(sub, font=B.font("sans", 30))) // 2, H - 250), sub, font=B.font("sans", 30), fill=B.TEXT_MUTED)
wm = "vyka.ro"
d.text(((W - d.textlength(wm, font=B.font("serif", 56))) // 2, H - 205), wm, font=B.font("serif", 56), fill=B.HEADING)
card.save(WORK / "c_phone.png"); print("c_phone")

# CTA — after + soft close
cta = grad(cover(Image.open(R / "src/ee0fa358/after.png").convert("RGB"), W, H), bottom=True, strength=195)
d = ImageDraw.Draw(cta)
B.kicker(d, (60, H - 300), fill=B.WHITE, size=26)
d.text((60, H - 262), "Camera ta te așteaptă.", font=B.font("serif", 70), fill=B.WHITE)
d.text((60, H - 150), "Prima e gratis · vyka.ro", font=B.font("sans", 33), fill=B.WHITE)
cta.save(WORK / "c_cta.png"); print("c_cta")
