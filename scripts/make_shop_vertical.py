"""9:16 shoppable card for the Reel's USP beat — after room + real products
(store badge + price). Matches vyka.ro via brand.py."""
import io, json, pathlib
import httpx
from PIL import Image, ImageDraw
import brand as B

R = pathlib.Path(__file__).resolve().parent.parent
OUT = R / "out"; WORK = R / "out/work"; WORK.mkdir(parents=True, exist_ok=True)
AFTER = R / "src/ee0fa358/after.png"
prods = json.loads((R / "src/ee0fa358/products.json").read_text())
want = ["Cadru pat KONGSBERG", "MALM Comodă", "Fotoliu HUNDESTED", "LINDBYN Oglindă"]
feat = [next(p for p in prods if p["name"].startswith(w)) for w in want]
total = sum(p["price_minor"] for p in prods) / 100


def lei(m): return f"{m/100:,.0f}".replace(",", ".") + " lei"


def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    nw, nh = round(im.width * s), round(im.height * s)
    im = im.resize((nw, nh), Image.LANCZOS)
    return im.crop(((nw - w) // 2, (nh - h) // 2, (nw - w) // 2 + w, (nh - h) // 2 + h))


def fetch(u): return Image.open(io.BytesIO(httpx.get(u, timeout=60).content)).convert("RGB")


W, H, ROOM_H = 1080, 1920, 1040
card = Image.new("RGB", (W, H), B.BG)
card.paste(cover(Image.open(AFTER).convert("RGB"), W, ROOM_H), (0, 0))
d = ImageDraw.Draw(card)
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
    card.paste(th, (x, chip_top))
    # no store name on marketing assets — price only
    d.text((x, chip_top + cw + 16), lei(p["price_minor"]), font=B.font("bold", 26), fill=B.ACCENT)
fy = chip_top + cw + 16 + 64
d.line([(54, fy), (W - 54, fy)], fill=B.HAIRLINE, width=1)
d.text((54, fy + 24), f"{len(prods)} produse · {total:,.0f}".replace(",", ".") + " lei",
       font=B.font("bold", 30), fill=B.HEADING)
d.text((54, fy + 66), "din magazine disponibile în România", font=B.font("sans", 26), fill=B.TEXT_MUTED)
cta = "vyka.ro"
d.text((W - 54 - d.textlength(cta, font=B.font("sans", 30)), fy + 30), cta, font=B.font("sans", 30), fill=B.ACCENT)
card.save(OUT / "ee_shop_9x16.png", quality=92)
print("wrote ee_shop_9x16.png", card.size)
