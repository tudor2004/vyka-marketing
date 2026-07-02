"""Single source of truth for Vyka asset styling — mirrors vyka.ro's Quiet
Gallery tokens EXACTLY (packages/ui/src/tokens/colors.ts + typography.ts).
Every marketing image/video imports from here so styling never drifts."""
import pathlib
from PIL import ImageFont

F = pathlib.Path(__file__).resolve().parent.parent / "fonts"
SERIF = str(F / "Fraunces-300.ttf")
SANS = str(F / "Inter-500.ttf")
SANS_B = str(F / "Inter-600.ttf")

CREAM_50 = (251, 247, 240)   # #FBF7F0 background
CREAM_100 = (245, 239, 227)  # #F5EFE3 cards
CREAM_200 = (236, 227, 208)  # #ECE3D0 borders
INK_700 = (21, 17, 13)       # #15110D headings
INK_500 = (51, 44, 36)       # #332C24 body
TEXT_MUTED = (107, 97, 85)   # #6B6155 kicker
ACCENT = (194, 94, 55)       # #C25E37 terracotta primary
OLIVE = (115, 120, 72)       # #737848 secondary
HAIRLINE = (214, 208, 200)
BG, HEADING, BODY, KICKER = CREAM_50, INK_700, INK_500, TEXT_MUTED
WHITE = (250, 248, 244)


def font(which, size):
    return ImageFont.truetype({"serif": SERIF, "sans": SANS, "bold": SANS_B}[which], size)


def kicker(d, xy, text="VYKA", size=24, fill=KICKER):
    d.text(xy, " ".join(list(text.upper())), font=font("sans", size), fill=fill)


def store_badge(d, xy, store, size=18):
    f = font("bold", size)
    x, y = xy
    tw = d.textlength(store, font=f)
    pad_x, h = 12, size + 14
    d.rectangle([x, y, x + tw + pad_x * 2, y + h], fill=INK_700)
    d.text((x + pad_x, y + 7), store, font=f, fill=CREAM_50)
    return tw + pad_x * 2
