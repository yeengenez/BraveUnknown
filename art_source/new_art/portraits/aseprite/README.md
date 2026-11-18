# Editing portrait parts in Aseprite

1. `git pull` the `art-source` branch.
2. In Aseprite: **File > Scripts > Open Scripts Folder**. Copy the three `.lua` files from this folder into it.
   In that scripts folder, create a text file `portraits_path.txt` with one line: the full path of your
   `art_source/new_art/portraits` folder, e.g. `C:\Users\you\BraveUnknown\art_source\new_art\portraits`.
   Then **File > Scripts > Rescan Scripts Folder**. (Running from the repo with `Aseprite -b --script` needs no path file.)
3. Run **build_portrait_parts**. It creates, in `art_source/new_art/portraits/aseprite/`:

   | File | Frames (tags) | Layers (bottom to top) |
   |---|---|---|
   | `m_hair.aseprite`, `f_hair.aseprite` | one per hairstyle | head, hair |
   | `m_eyes.aseprite`, `f_eyes.aseprite` | one per eye pair | head (locked), eyes, iris |
   | `m_bodies.aseprite`, `f_bodies.aseprite` | one per class | head (locked), body_skin, body |

4. Edit. **head, hair, iris and body_skin are gray value maps** (the game tints them with skin / hair / eye colours):
   keep them gray, black = deepest shadow, white = highlight. **eyes** and **body** are final colours.
   The head is only editable in the hair file (it is exported from there).
5. Save the .aseprite files, run **export_portrait_parts**. Every editable layer of every tagged frame is written
   back to its PNG (`m_hair_spiky.png`, `f_eyes_doe_iris.png`, `m_body_warrior_skin.png`, ...).
6. Commit and push the changed PNGs (the .aseprite files are working files; commit them too if you want to keep them).

Running build again overwrites the .aseprite files from the PNGs, so export first.
New styles: add a PNG with the right name (e.g. `m_hair_mohawk.png`) and run build; it is picked up automatically.
