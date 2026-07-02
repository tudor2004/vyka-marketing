"""Static elements for the 'Garsonieră comunistă -> glow-up' reel (1080x1920).
hook (the dated bloc room + nostalgic caption), shoppable proof card (after +
real products & prices), CTA. Brand-styled via brand.py. NO store names.

Reads a campaign folder under src/ (default src/gc01/): before.jpg, after.png,
products.json. Drop a real garsonieră before/after there (see src/gc01/INPUTS.md)."""
import io, json, pathlib, sys
import httpx
from PIL import Image, ImageDraw
import brand as B

R = pathlib.Path(__file__).resolve().parent.parent
OUT = R / "out"; WORK = R / "out/work"; WORK.mkdir(parents=True, exist_ok=True)
CAMP = sys.argv[1] if len(sys.argv) > 1 else "gc01"
SRC = R / "src" / CAMP
W, H = 1080, 1920

prods = json.loads((SRC / "products.json").read_text())
total = sum(p["price_minor"] for p in prods) / 100
# feature the 4 priciest pieces that have a photo (the hero items)
feat = sorted([p for p in prods if p.get("primary_image_url")],
              key=lambda p: -p["price_minor"])[:4]


def lei(m): return f"{m/100:,.0f}".replace(",", ".") + " lei"


def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    nw, nh = round(im.width * s), round(im.height * s)
    im = im.resize((nw, nh), Image.LANCZOS)
    return im.crop(((nw - w) // 2, (nh - h) // 2, (nw - w) // 2 + w, (nh - h) // 2 + h))


def fetch(u): return Image.open(io.BytesIO(httpx.get(u, timeout=60).content)).convert("RGB")


def grad(im, strength=185):
    sc = Image.new("L", (1, H), 0)
    for y in range(H):
        t = max(0.0, (y - H * 0.50) / (H * 0.50))
        sc.putpixel((0, y), int(strength * (t ** 1.35)))
    return Image.composite(Image.new("RGB", (W, H), B.INK_700), im, sc.resize((W, H)))


# HOOK — the dated bloc room + nostalgic serif caption
hook = grad(cover(Image.open(SRC / "before.jpg").convert("RGB"), W, H), strength=180)
d = ImageDraw.Draw(hook)
B.kicker(d, (60, H - 360), fill=B.WHITE, size=26)
d.text((60, H - 320), "Apartamentul ăsta", font=B.font("serif", 76), fill=B.WHITE)
d.text((60, H - 232), "n-a fost atins din '89.", font=B.font("serif", 76), fill=B.WHITE)
hook.save(WORK / "gc_hook.png"); print("gc_hook")

# SHOPPABLE PROOF — after room + real products (price only, no store names)
ROOM_H = 1040
shop = Image.new("RGB", (W, H), B.BG)
shop.paste(cover(Image.open(SRC / "after.png").convert("RGB"), W, ROOM_H), (0, 0))
d = ImageDraw.Draw(shop)
y = ROOM_H + 54
B.kicker(d, (54, y))
d.text((54, y + 40), "Fiecare piesă e reală.", font=B.font("serif", 66), fill=B.HEADING)
d.text((54, y + 124), "Și o poți cumpăra — din magazine din România.", font=B.font("sans", 30), fill=B.BODY)
chip_top = y + 196
n = len(feat); margin, gap = 54, 24
cw = (W - 2 * margin - (n - 1) * gap) // n
for i, p in enumerate(feat):
    x = margin + i * (cw + gap)
    try:
        th = cover(fetch(p["primary_image_url"]), cw, cw)
    except Exception:
        th = Image.new("RGB", (cw, cw), B.CREAM_100)
    shop.paste(th, (x, chip_top))
    d.text((x, chip_top + cw + 16), lei(p["price_minor"]), font=B.font("bold", 26), fill=B.ACCENT)
fy = chip_top + cw + 16 + 64
d.line([(54, fy), (W - 54, fy)], fill=B.HAIRLINE, width=1)
d.text((54, fy + 24), f"{len(prods)} produse · {total:,.0f}".replace(",", ".") + " lei",
       font=B.font("bold", 30), fill=B.HEADING)
d.text((54, fy + 66), "din magazine disponibile în România", font=B.font("sans", 26), fill=B.TEXT_MUTED)
d.text((W - 54 - d.textlength("vyka.ro", font=B.font("sans", 30)), fy + 30), "vyka.ro",
       font=B.font("sans", 30), fill=B.ACCENT)
shop.save(OUT / "gc_shop_9x16.png", quality=92); print("gc_shop_9x16")

# CTA — after + personal close
cta = grad(cover(Image.open(SRC / "after.png").convert("RGB"), W, H), strength=195)
d = ImageDraw.Draw(cta)
B.kicker(d, (60, H - 300), fill=B.WHITE, size=26)
d.text((60, H - 262), "Și a ta poate arăta așa.", font=B.font("serif", 68), fill=B.WHITE)
d.text((60, H - 150), "Prima cameră e gratis · vyka.ro", font=B.font("sans", 33), fill=B.WHITE)
cta.save(WORK / "gc_cta.png"); print("gc_cta")
