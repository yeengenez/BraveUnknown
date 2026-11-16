# Battle sprites (in progress, on hold)

Full-body sprites that match the hero portraits. Same idea as the portraits: a hero is assembled
from layers (body, weapon, shield, later hair and skin tint) driven by the same `HeroAppearance`.

**Status:** Soldier bodies confirmed. Paused until the class equipment lists are defined. Next step
after that: draw the example weapons as separate layers and fit them to these bodies.

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

## Files

| Path | Contents |
|---|---|
| `soldier/bodies/` | The six confirmed Soldier bodies, 133×200, white background |
| `soldier/previews/` | Review sheets and weapon previews (greatsword, spear in each stance) |
| `style_reference/` | The design the style was chosen from |
| `first_layer_test/` | First attempt at cutting weapons into layers (superseded; kept for the scripts) |

Canva media ids of the confirmed bodies: male 1H `MAHbDda6aMk`, 2H `MAHbDT2gx3c`, reach `MAHbDaj44KI`;
female 1H `MAHbDWuOiaE`, 2H `MAHbDfkRYn0`, reach `MAHbDfxJVE8`.

## Notes for the next step

- The six bodies differ slightly in scale (the reach bodies are smaller). Normalize them to one head
  size when cutting layers, so a hero does not change size when switching weapons.
- Cutting a weapon back out of an AI edit of the body leaves artifacts (ghost outlines, broken poles);
  see `first_layer_test/soldier_test_sheet.png`. Draw each weapon on its own at matching scale and place
  it by its grip point instead.
- The empty reach body holds the back fist lower than the spear preview, so a spear placed on it will
  angle up slightly toward the front.
