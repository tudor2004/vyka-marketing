# src/gc01 — campaign source for "Garsonieră Comunistă → Glow-up"

Drop three files here, then run the `gc` scripts (see
`docs/campaigns/garsoniera-comunista.md`). This folder is intentionally empty of
binaries until a real transformation is supplied — these are NOT placeholders to
ship; use a genuine bloc-apartment before/after.

| File | What it is |
|------|-----------|
| `before.jpg` | The real *garsonieră / apartament de bloc* photo (the dated room) |
| `after.png` | The vyka.ro AI redesign of that exact room (export from the result page) |
| `products.json` | The shopping list behind that design (export / mirror the schema below) |

`products.json` schema — same as `src/ee0fa358/products.json`:

```json
[
  {
    "kind": "essentials | decoration",
    "name": "Product name",
    "category": "Paturi",
    "store": "IKEA",
    "price_minor": 169900,           // price in bani (RON * 100)
    "currency": "RON",
    "primary_image_url": "https://…"  // used for the shoppable card thumbnails
  }
]
```

Notes:
- The scripts feature the 4 priciest items (with photos) on the shoppable card and
  show the full count + total — **price only, no store names** (marketing rule).
- More rooms? Use `src/gc02/`, `src/gc03/…` and pass the id:
  `python scripts/make_gc_elements.py gc02`.
