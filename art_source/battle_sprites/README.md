# Battle sprites (in progress)

> **LEGACY — reference only (2026-11-18).** All Canva-made bodies, grip bodies, poses and sprites here are Legacy and were not put into the game. Scripts and the grip JSON format are still usable. See [`../LEGACY.md`](../LEGACY.md).

Full-body sprites that match the hero portraits. Same idea as the portraits: a hero is assembled
from layers (body, weapon, shield, later hair and skin tint) driven by the same `HeroAppearance`.

**Status:** Soldier bodies confirmed by the user. Bodies for the other five classes were drawn on
2026-11-17 (Archer, Acolyte, Mage, Brawler, Rogue) and are **awaiting review**. Weapons are not drawn yet.
Review sheet: `all_class_bodies_sheet.png`.

## Confirmed decisions

- **Style:** `style_reference/chosen_style_MAHbDbX73BU.png`. Taller, natural anime proportions
  (about 6–7 heads), not the chunky big-head version. Characters face right (the party is on the left).
- **Bodies have no weapons.** Hands are empty gripping fists. Weapons and shields are separate layers
  placed at each body's hand points, with the body's own fist drawn over the handle.
- **Three stances per body:**
  - **One-handed** (`*_1h`): back fist raised, front fist forward. Weapon alone goes in the front hand.
    Weapon with a shield: shield on the front arm, weapon in the back hand.
  - **Two-handed** (`*_2h`): both fists together, held forward. Greatsword (and future 2H axes or hammers).
  - **Reach** (`*_reach`): hands spread along the shaft, front fist forward, back fist at the rear hip.
    Spear, glaive, halberd.
  - Archers will use a bow/crossbow shooting pose instead of the melee two-handed stance (not drawn yet).
- **Female bodies are clearly feminine** at sprite size: smaller frame, narrow shoulders, curved waist
  and hips, visible chest under the armor, slimmer limbs, smaller pauldrons. Same armor style as the male.

## Stances per class

Each class gets the stances its weapon list (design doc, class table) needs. Male and female each.

| Class | Stances | Why |
|---|---|---|
| Soldier | 1h, 2h, reach | Martial and reach weapons, shield |
| Archer | 1h, bow | Light secondary weapon (or two daggers); `bow` is the bow/crossbow shooting pose |
| Acolyte | 1h, 2h, reach | Simple weapons include the quarterstaff (2h) and spears (reach); shield on 1h |
| Mage | 1h | Light simple weapons only; wand or staff held in the front hand (assumption) |
| Brawler | 1h, 2h, reach | Simple and martial weapons; unarmed pairs use the 1h body, fists already wrapped |
| Rogue | 1h | One-handed weapons only; dual wield uses the 1h body (one weapon per fist) |

Assumptions to confirm: the Acolyte has no crossbow pose (crossbows are simple weapons in PF1e); the
Mage holds a staff in the 1h pose; dual wield and unarmed use the 1h pose.

## Outfits (shared with the portraits)

- Archer: green cloak with gold trim, hood down, brown laced jerkin, quiver on the back.
- Acolyte: white hooded mantle with gold trim, blue gem clasp, one gold cross, long white robe.
- Mage: deep violet robe with silver trim, high collar, crescent clasp, blue sash with book pouch.
- Brawler: crimson sleeveless tunic, studded leather vest, black sash, hand wraps, wrapped shins.
- Rogue: charcoal leather armor, plum short hooded cape (hood down) and scarf, belt daggers.

## Files

| Path | Contents |
|---|---|
| `<class>/bodies/` | `<m|f>_<stance>.png`, 133×200, white background, facing right |
| `all_class_bodies_sheet.png` | Every body on one sheet |
| `soldier/previews/` | Review sheets and weapon previews (greatsword, spear in each stance) |
| `style_reference/` | The design the style was chosen from |
| `first_layer_test/` | First attempt at cutting weapons into layers (superseded; kept for the scripts) |

Canva media ids. Soldier: male 1H `MAHbDda6aMk`, 2H `MAHbDT2gx3c`, reach `MAHbDaj44KI`;
female 1H `MAHbDWuOiaE`, 2H `MAHbDfkRYn0`, reach `MAHbDfxJVE8`. The other classes were made as outfit
edits of the Soldier body with the same stance and sex (bow poses from the Archer 1h body):

| Body | Male | Female |
|---|---|---|
| Archer 1h / bow | `MAHbLFV2fGA` / `MAHbLCZu3vg` | `MAHbLKDXDAc` / `MAHbLAWbzhI` |
| Acolyte 1h / 2h / reach | `MAHbLA6IyVw` / `MAHbLFXF_d4` / `MAHbLOWyfnA` | `MAHbLDP8XHg` / `MAHbLFooT34` / `MAHbLBYUNcA` |
| Mage 1h | `MAHbLNJbWUs` | `MAHbLCqcxr0` |
| Brawler 1h / 2h / reach | `MAHbLLgVeYw` / `MAHbLPcQ2lQ` / `MAHbLIoslTE` | `MAHbLIrIQbk` / `MAHbLBhGz0o` / `MAHbLEgswbA` |
| Rogue 1h | `MAHbLNgYPxw` | `MAHbLJNZQzM` |

Known flaws: the male Acolyte reach body has a warmer (orange) head than the others; the female
Acolyte reach body seems to have lost the gold cross. Fix by regenerating or in the layer pass.

## Notes for the next step

- The bodies differ slightly in scale (the reach bodies are smaller). Normalize them to one head
  size when cutting layers, so a hero does not change size when switching weapons.
- Cutting a weapon back out of an AI edit of the body leaves artifacts (ghost outlines, broken poles);
  see `first_layer_test/soldier_test_sheet.png`. Draw each weapon on its own at matching scale and place
  it by its grip point instead.
- The empty reach body holds the back fist lower than the spear preview, so a spear placed on it will
  angle up slightly toward the front.
