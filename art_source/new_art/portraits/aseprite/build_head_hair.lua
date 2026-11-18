-- Expedition: Brave Unknown - head + hair touch-up file.
-- Builds <sex>_head_hair.aseprite from the PNG layers in the folder above (art_source/new_art/portraits/).
-- One FRAME per hairstyle (each frame is tagged with the style name). Layers, back to front:
--   head  (the base head, same in every frame - linked cel)
--   hair  (that frame's hairstyle)
-- Both are grayscale value maps: the game tints them, so keep the hair gray and use the full range
-- (black = deepest shadow, white = highlight). Edit, then run export_head_hair.lua to write the PNGs back.
-- Run:  Aseprite > File > Scripts > Open Scripts Folder, copy this folder in, run "build_head_hair".
--   or: "<path to>\Aseprite.exe" -b --script build_head_hair.lua

local dir = app.fs.filePath(debug.getinfo(1, "S").source:sub(2))
local src = app.fs.joinPath(dir, "..")
local STYLES = {
  m = {"messy","sidepart","spiky","crewcut","slicked","shaggy","ponytail","long",
       "topknot","braided_mohawk","wild_mane","knight_cut"},
  f = {"long","ponytail","bob","braids","wavy","pixie","bun","crown_braid",
       "side_braid","twin_buns","curly_mane","warrior_halfup"},
}
for _, sex in ipairs({"m", "f"}) do
  local headPath = app.fs.joinPath(src, sex .. "_head_skin.png")
  if app.fs.isFile(headPath) then
    local spr = Sprite(200, 200, ColorMode.RGB)
    spr.layers[1].name = "head"
    local hairLayer = spr:newLayer(); hairLayer.name = "hair"
    local head = Image{ fromFile = headPath }
    local n = 0
    for i, style in ipairs(STYLES[sex]) do
      local p = app.fs.joinPath(src, sex .. "_hair_" .. style .. ".png")
      if app.fs.isFile(p) then
        n = n + 1
        if n > 1 then spr:newEmptyFrame() end
        spr:newCel(spr.layers[1], n, head, Point(0, 0))
        spr:newCel(hairLayer, n, Image{ fromFile = p }, Point(0, 0))
        local tag = spr:newTag(n, n); tag.name = style
      end
    end
    spr:saveAs(app.fs.joinPath(dir, sex .. "_head_hair.aseprite"))
  end
end
