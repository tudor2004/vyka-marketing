"""All static marketing cards from design ee0fa358, styled to match vyka.ro
(brand.py). Outputs to out/: shoppable 4:5, before/after 9:16 + 4:5, hero 9:16."""
import io, json, pathlib
import httpx
from PIL import Image, ImageDraw
import brand as B

R = pathlib.Path(__file__).parent
OUT = R / "out"
BEFORE = R / "src/ee_before.jpg"
AFTER = R / "src/ee_after.png"
WHITE = B.WHITE


def cover(path, w, h):
    im = Image.open(path).convert("RGB")
    s = max(w / im.width, h / im.height)
    nw, nh = round(im.width * s), round(im.height * s)
    im = im.resize((nw, nh), Image.LANCZOS)
    return im.crop(((nw - w) // 2, (nh - h) // 2, (nw - w) // 2 + w, (nh - h) // 2 + h))


def fetch(url):
    return Image.open(io.BytesIO(httpx.get(url, timeout=60).content)).convert("RGB")


def lei(minor):
    return f"{minor/100:,.0f}".replace(",", ".") + " lei"


def tag(d, x, y, text):
    f = B.font("bold", 26)
    s = " ".join(list(text.upper()))
    tw = d.textlength(s, font=f)
    d.rectangle([x, y, x + tw + 38, y + 52], fill=B.INK_700)
    d.text((x + 19, y + 13), s, font=f, fill=WHITE)


def band(card, top, h, hook, cta="vyka.ro"):
    d = ImageDraw.Draw(card)
    W = card.width
    d.rectangle([0, top, W, top + h], fill=B.BG)
    B.kicker(d, (44, top + h * 0.24))
    d.text((44, top + h * 0.40), hook, font=B.font("serif", 50), fill=B.HEADING)
    cf = B.font("sans", 30)
    d.text((W - 44 - d.textlength(cta, font=cf), top + h * 0.46), cta, font=cf, fill=B.ACCENT)


def before_after(W, H, band_h, hook, out, cta="vyka.ro"):
    cell_h = (H - band_h) // 2
    card = Image.new("RGB", (W, H), B.BG)
    card.paste(cover(BEFORE, W, cell_h), (0, 0))
    card.paste(cover(AFTER, W, cell_h), (0, cell_h))
    d = ImageDraw.Draw(card)
    d.line([(0, cell_h), (W, cell_h)], fill=B.BG, width=4)
    tag(d, 26, cell_h - 70, "Înainte")
    tag(d, 26, 2 * cell_h - 70, "După")
    band(card, 2 * cell_h, band_h, hook, cta)
    card.save(OUT / out, quality=92)
    print("wrote", out)


def hero(W, H, hook_lines, cta, out):
    card = cover(AFTER, W, H)
    scrim = Image.new("L", (1, H), 0)
    for y in range(H):
        t = max(0.0, (y - H * 0.52) / (H * 0.48))
        scrim.putpixel((0, y), int(185 * (t ** 1.35)))
    card = Image.composite(Image.new("RGB", (W, H), B.INK_700), card, scrim.resize((W, H)))
    d = ImageDraw.Draw(card)
    pad = 72
    hf, cf = B.font("serif", 76), B.font("sans", 31)
    lh = 92
    cta_y = H - pad - 30
    htop = cta_y - 44 - lh * len(hook_lines)
    B.kicker(d, (pad, htop - 60), fill=WHITE)
    d.line([(pad, htop - 22), (pad + 66, htop - 22)], fill=WHITE, width=2)
    for i, ln in enumerate(hook_lines):
        d.text((pad, htop + i * lh), ln, font=hf, fill=WHITE)
    d.text((pad, cta_y), cta, font=cf, fill=WHITE)
    card.save(OUT / out, quality=92)
    print("wrote", out)


def shoppable(out):
    prods = json.loads((R / "src/ee_products.json").read_text())
    want = ["Cadru pat KONGSBERG", "MALM Comodă", "Fotoliu HUNDESTED", "LINDBYN Oglindă"]
    feat = [next(p for p in prods if p["name"].startswith(w)) for w in want]
    total = sum(p["price_minor"] for p in prods) / 100
    W, H, ROOM_H = 1080, 1350, 620
    card = Image.new("RGB", (W, H), B.BG)
    card.paste(cover(AFTER, W, ROOM_H), (0, 0))
    d = ImageDraw.Draw(card)
    y = ROOM_H + 34
    B.kicker(d, (44, y))
    d.text((44, y + 34), "Fiecare piesă e reală.", font=B.font("serif", 56), fill=B.HEADING)
    d.text((44, y + 104), "Și o poți cumpăra — din magazine din România.", font=B.font("sans", 27), fill=B.BODY)
    chip_top = y + 162
    n = len(feat); margin, gap = 44, 22
    cw = (W - 2 * margin - (n - 1) * gap) // n
    for i, p in enumerate(feat):
        x = margin + i * (cw + gap)
        try:
            th = cover_img(fetch(p["primary_image_url"]), cw, cw)
        except Exception:
            th = Image.new("RGB", (cw, cw), B.CREAM_100)
        card.paste(th, (x, chip_top))
        # no store name on marketing assets — price only
        d.text((x, chip_top + cw + 14), lei(p["price_minor"]), font=B.font("bold", 24), fill=B.ACCENT)
    fy = H - 96
    d.line([(44, fy), (W - 44, fy)], fill=B.HAIRLINE, width=1)
    d.text((44, fy + 20), f"{len(prods)} produse · {total:,.0f}".replace(",", ".") + " lei · din magazine din România",
           font=B.font("bold", 24), fill=B.HEADING)
    cta = "vyka.ro"
    d.text((W - 44 - d.textlength(cta, font=B.font("sans", 27)), fy + 22), cta, font=B.font("sans", 27), fill=B.ACCENT)
    card.save(OUT / out, quality=92)
    print("wrote", out)


def cover_img(im, w, h):
    s = max(w / im.width, h / im.height)
    nw, nh = round(im.width * s), round(im.height * s)
    im = im.resize((nw, nh), Image.LANCZOS)
    return im.crop(((nw - w) // 2, (nh - h) // 2, (nw - w) // 2 + w, (nh - h) // 2 + h))


before_after(1080, 1920, 220, "Camera ta, transformată.", "ee_ba_9x16.png")
hero(1080, 1920, ["Încarcă o poză.", "Vezi-o transformată."], "Prima ta cameră, gratis · vyka.ro", "ee_hero_9x16.png")
before_after(1080, 1350, 180, "Din cum e — în cum visezi.", "ee_ba_4x5.png")
shoppable("ee_shoppable_4x5.png")
