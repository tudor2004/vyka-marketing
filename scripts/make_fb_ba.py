"""Facebook before/after promo creatives (RO campaigns + community groups).
Stacked ÎNAINTE / DUPĂ with a clean footer band: headline + proof subline + CTA.
Brand-styled via brand.py; NO store names (marketing rule). Outputs to out/.

Produces 3 creatives across the two real designs and FB's two best feed formats
(4:5 portrait, 1:1 square). Run from repo root."""
import json, pathlib
from PIL import Image, ImageDraw
import brand as B

R = pathlib.Path(__file__).resolve().parent.parent
OUT = R / "out"
WHITE = B.WHITE


def cover(path, w, h):
    im = Image.open(path).convert("RGB")
    s = max(w / im.width, h / im.height)
    nw, nh = round(im.width * s), round(im.height * s)
    im = im.resize((nw, nh), Image.LANCZOS)
    return im.crop(((nw - w) // 2, (nh - h) // 2, (nw - w) // 2 + w, (nh - h) // 2 + h))


def n_products(camp):
    return len(json.loads((R / "src" / camp / "products.json").read_text()))


def badge(d, x, y, text, size=26):
    f = B.font("bold", size)
    s = " ".join(list(text.upper()))
    tw = d.textlength(s, font=f)
    pad_x, h = 19, size + 26
    # soft shadow so the pill reads on any photo
    d.rectangle([x + 2, y + 2, x + tw + pad_x * 2 + 2, y + h + 2], fill=(0, 0, 0))
    d.rectangle([x, y, x + tw + pad_x * 2, y + h], fill=B.INK_700)
    d.text((x + pad_x, y + 13), s, font=f, fill=WHITE)


def footer(card, top, h, hook, sub, cta="vyka.ro"):
    W = card.width
    d = ImageDraw.Draw(card)
    d.rectangle([0, top, W, top + h], fill=B.BG)
    pad = 48
    B.kicker(d, (pad, top + int(h * 0.16)))
    hf = B.font("serif", 50 if W >= 1080 and h >= 180 else 44)
    d.text((pad, top + int(h * 0.30)), hook, font=hf, fill=B.HEADING)
    sf = B.font("sans", 27)
    d.text((pad, top + int(h * 0.74)), sub, font=sf, fill=B.TEXT_MUTED)
    cf = B.font("bold", 30)
    cw = d.textlength(cta + "  →", font=cf)
    d.text((W - pad - cw, top + int(h * 0.30)), cta + "  →", font=cf, fill=B.ACCENT)


def before_after(camp, W, H, band_h, hook, sub, out, cta="vyka.ro"):
    before = R / "src" / camp / "before.jpg"
    after = R / "src" / camp / "after.png"
    cell_h = (H - band_h) // 2
    card = Image.new("RGB", (W, H), B.BG)
    card.paste(cover(before, W, cell_h), (0, 0))
    card.paste(cover(after, W, cell_h), (0, cell_h))
    d = ImageDraw.Draw(card)
    d.line([(0, cell_h), (W, cell_h)], fill=B.BG, width=4)
    badge(d, 26, 26, "Înainte")
    badge(d, 26, cell_h + 26, "După")
    footer(card, 2 * cell_h, H - 2 * cell_h, hook, sub, cta)
    card.save(OUT / out, quality=92)
    print("wrote", out, card.size)


# 1) Scandinavian bedroom — 4:5 feed (transformation + affordability angle)
before_after("ee0fa358", 1080, 1350, 200,
             "Aceeași cameră. Reimaginată.",
             f"{n_products('ee0fa358')} piese reale, din magazine din România · prima e gratis",
             "fb_ba_ee_4x5.png")

# 2) Minimalist bedroom — 4:5 feed (real-products angle)
before_after("a3cdba11", 1080, 1350, 200,
             "Din învechit, în uimitor.",
             "Fiecare piesă se poate cumpăra · prima ta cameră, gratis",
             "fb_ba_a3_4x5.png")

# 3) Scandinavian bedroom — 1:1 square (groups / feed thumbnail, relatable hook)
before_after("ee0fa358", 1080, 1080, 180,
             "Camera ta merită asta.",
             "Încarcă o poză. Vezi-o transformată · gratis",
             "fb_ba_ee_1x1.png")
