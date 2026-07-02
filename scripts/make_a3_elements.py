"""TikTok-style reel elements for design a3cdba11 (dormitor minimalist).
Hook card, rapid product montage cards, USP summary, CTA. Brand-styled, NO
store names (marketing rule)."""
import io, json, pathlib
import httpx
from PIL import Image, ImageDraw
import brand as B

R = pathlib.Path(__file__).resolve().parent.parent
OUT = R / "out"; WORK = R / "out/work"; WORK.mkdir(parents=True, exist_ok=True)
prods = json.loads((R / "src/a3cdba11/products.json").read_text())
total = sum(p["price_minor"] for p in prods) / 100
W, H = 1080, 1920
WHITE = (255, 255, 255)


def lei(m): return f"{m/100:,.0f}".replace(",", ".") + " lei"


def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    nw, nh = round(im.width * s), round(im.height * s)
    im = im.resize((nw, nh), Image.LANCZOS)
    return im.crop(((nw - w) // 2, (nh - h) // 2, (nw - w) // 2 + w, (nh - h) // 2 + h))


def contain(im, w, h):
    s = min(w / im.width, h / im.height)
    return im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)


def fetch(u): return Image.open(io.BytesIO(httpx.get(u, timeout=60).content)).convert("RGB")


def short(name):
    # turn "Cadru pat KONGSBERG 180x200 bej" -> "Pat KONGSBERG" etc.
    w = name.replace("Cadru pat", "Pat").replace("artificială", "").split()
    return " ".join(w[:2])


# 1) HOOK card — before room + punchy caption
def hook():
    card = cover(Image.open(R / "src/a3cdba11/before.jpg").convert("RGB"), W, H)
    sc = Image.new("L", (1, H), 0)
    for y in range(H):
        a = 150
        if y < H * 0.34: t = (H * 0.34 - y) / (H * 0.34)
        elif y > H * 0.66: t = (y - H * 0.66) / (H * 0.34)
        else: t = 0
        sc.putpixel((0, y), int(a * (t ** 1.3)))
    card = Image.composite(Image.new("RGB", (W, H), B.INK_700), card, sc.resize((W, H)))
    d = ImageDraw.Draw(card)
    B.kicker(d, (60, 120), "POV", fill=B.WHITE, size=30)
    d.text((60, 158), "Dormitorul tău arată", font=B.font("serif", 70), fill=B.WHITE)
    d.text((60, 238), "așa de banal?", font=B.font("serif", 70), fill=B.WHITE)
    d.text((60, H - 180), "Stai să vezi.", font=B.font("sans", 40), fill=B.WHITE)
    card.save(WORK / "a3_hook.png"); print("hook")


def not_blank(im):
    """Reject near-blank product photos (>92% near-white pixels)."""
    g = im.convert("L").resize((64, 64))
    px = list(g.get_flattened_data() if hasattr(g, "get_flattened_data") else g.getdata())
    white = sum(1 for v in px if v > 246)
    return white / len(px) < 0.95


# 2) PRODUCT montage cards — curated to recognizable furniture with solid photos
def product_cards():
    priority = ["Fotoliu", "Cadru pat", "MALM", "LINDBYN", "MATT Covor", "OLIVE", "COLERAINE"]
    ordered = []
    for key in priority:
        for r in prods:
            if r["name"].startswith(key) and r not in ordered:
                ordered.append(r); break
    # backfill with any remaining products by price desc
    for r in sorted(prods, key=lambda x: -x["price_minor"]):
        if r not in ordered:
            ordered.append(r)
    pick, i = [], 0
    for p in ordered:
        if len(pick) == 6:
            break
        try:
            im = fetch(p["primary_image_url"])
            if not not_blank(im):
                print("skip blank:", p["name"][:30]); continue
        except Exception:
            continue
        i += 1
        card = Image.new("RGB", (W, H), B.BG)
        top_h = 1200
        card.paste(Image.new("RGB", (W, top_h), WHITE), (0, 0))
        ci = contain(im, W - 160, top_h - 130)
        card.paste(ci, ((W - ci.width) // 2, (top_h - ci.height) // 2))
        d = ImageDraw.Draw(card)
        by = top_h + 80
        B.kicker(d, (60, by), "PRODUS REAL", size=26)
        d.text((60, by + 42), short(p["name"]), font=B.font("serif", 66), fill=B.HEADING)
        d.text((60, by + 138), lei(p["price_minor"]), font=B.font("bold", 64), fill=B.ACCENT)
        card.save(WORK / f"a3_p{i}.png")
        pick.append(p)
    print("product cards:", len(pick))
    return len(pick)


# 3) USP summary (9:16)
def usp():
    card = Image.new("RGB", (W, H), B.BG)
    card.paste(cover(Image.open(R / "src/a3cdba11/after.png").convert("RGB"), W, 1180), (0, 0))
    d = ImageDraw.Draw(card)
    y = 1180 + 70
    B.kicker(d, (60, y))
    d.text((60, y + 40), "Un dormitor întreg.", font=B.font("serif", 72), fill=B.HEADING)
    d.text((60, y + 132), "Și fiecare piesă e reală.", font=B.font("serif", 60), fill=B.ACCENT)
    d.text((60, y + 240), f"{len(prods)} produse · {total:,.0f}".replace(",", ".") + " lei",
           font=B.font("bold", 40), fill=B.HEADING)
    d.text((60, y + 296), "din magazine disponibile în România", font=B.font("sans", 32), fill=B.TEXT_MUTED)
    card.save(OUT / "a3_shop_9x16.png"); print("usp")


# 4) CTA (9:16) — after full-bleed
def cta():
    card = cover(Image.open(R / "src/a3cdba11/after.png").convert("RGB"), W, H)
    sc = Image.new("L", (1, H), 0)
    for yy in range(H):
        t = max(0.0, (yy - H * 0.5) / (H * 0.5)); sc.putpixel((0, yy), int(195 * (t ** 1.35)))
    card = Image.composite(Image.new("RGB", (W, H), B.INK_700), card, sc.resize((W, H)))
    d = ImageDraw.Draw(card); pad = 72
    B.kicker(d, (pad, H - pad - 250), fill=B.WHITE, size=30)
    d.line([(pad, H - pad - 204), (pad + 74, H - pad - 204)], fill=B.WHITE, width=3)
    d.text((pad, H - pad - 174), "Încarcă o poză.", font=B.font("serif", 82), fill=B.WHITE)
    d.text((pad, H - pad - 86), "Prima ta cameră e gratis · vyka.ro", font=B.font("sans", 33), fill=B.WHITE)
    card.save(WORK / "a3_cta.png"); print("cta")


hook(); n = product_cards(); usp(); cta()
print("N_PRODUCTS", n)
