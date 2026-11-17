-- Expedition: Brave Unknown - weapon layers for battle sprites.
-- Builds two Aseprite files next to this script and exports PNGs into export\.
-- Run:  "<path to>\Aseprite.exe" -b --script build_weapons.lua
-- (or in Aseprite: File > Scripts > Open Scripts Folder, copy this folder in, then run it from the menu)

local dir = app.fs.filePath(debug.getinfo(1, "S").source:sub(2))
local function P(...) return app.fs.joinPath(dir, ...) end
app.fs.makeDirectory(P("export"))

local PALETTE = {
  {34,30,38},
  {78,84,98},
  {128,136,150},
  {180,188,200},
  {234,238,244},
  {70,42,26},
  {108,68,38},
  {148,98,56},
  {54,32,24},
  {100,56,34},
  {150,104,32},
  {216,172,66},
  {28,46,108},
  {46,80,166},
  {90,128,212}
}
local function setPalette(spr)
  local p = Palette(#PALETTE + 1)
  p:setColor(0, Color{r=0, g=0, b=0, a=0})
  for i, c in ipairs(PALETTE) do p:setColor(i, Color{r=c[1], g=c[2], b=c[3], a=255}) end
  spr:setPalette(p)
end

------------------------------------------------------------------ 1. weapons.aseprite
-- One layer per weapon, lying flat with the point to the right. Each weapon has a slice
-- "<name>_grip" whose pivot is the hand position (and "<name>_grip2" for the second hand).
local WEAPONS = {
  {name="sword", w=68, h=13, y=2, grip={12,6}},
  {name="shield", w=28, h=38, y=21, grip={14,18}},
  {name="greataxe", w=120, h=36, y=65, grip={18,5}, grip2={9,5}},
  {name="longspear", w=242, h=11, y=107, grip={181,5}, grip2={19,5}}
}
local W, H = 0, 0
for _, w in ipairs(WEAPONS) do W = math.max(W, w.w + 4); H = w.y + w.h + 2 end
local spr = Sprite(W, H, ColorMode.RGB)
setPalette(spr)
spr.layers[1].name = "_delete"
for _, w in ipairs(WEAPONS) do
  local layer = spr:newLayer()
  layer.name = w.name
  local img = Image{ fromFile = P("layers", "w_" .. w.name .. ".png") }
  spr:newCel(layer, 1, img, Point(2, w.y))
  for k, key in ipairs({"grip", "grip2"}) do
    local g = w[key]
    if g then
      local s = spr:newSlice(Rectangle(2, w.y, w.w, w.h))
      s.name = w.name .. "_" .. key
      s.pivot = Point(g[1], g[2])
      s.color = (k == 1) and Color{r=255, g=80, b=80} or Color{r=80, g=120, b=255}
    end
  end
end
spr:deleteLayer("_delete")
spr:saveAs(P("weapons.aseprite"))
for _, layer in ipairs(spr.layers) do                       -- one PNG per weapon
  layer:cel(1).image:saveAs(P("export", "weapon_" .. layer.name .. ".png"))
end
-- left open so you can look at it

------------------------------------------------------------------ 2. merge_examples.aseprite
-- One frame per test (tagged). Layers, back to front: squares, weapon_back, body, weapon_front, fists.
-- The body stands in the middle square; long weapons may cross into the next square.
local TESTS = {
  "soldier_m_1h_sword_shield",
  "soldier_f_1h_sword_shield",
  "soldier_m_1h_sword",
  "soldier_f_1h_sword",
  "soldier_m_2h_greataxe",
  "soldier_f_2h_greataxe",
  "brawler_m_2h_greataxe",
  "brawler_f_2h_greataxe",
  "soldier_m_reach_longspear",
  "soldier_f_reach_longspear",
  "acolyte_m_reach_longspear",
  "acolyte_f_reach_longspear"
}
local CW, CH = 399, 270
local m = Sprite(CW, CH, ColorMode.RGB)
local order = { "squares", "weapon_back", "body", "weapon_front", "fists" }
local layers = {}
m.layers[1].name = "squares"; layers.squares = m.layers[1]
for i = 2, #order do local l = m:newLayer(); l.name = order[i]; layers[order[i]] = l end
for i, name in ipairs(TESTS) do
  if i > 1 then m:newEmptyFrame() end
  local idx = string.format("t%02d_", i - 1)
  m:newCel(layers.squares, i, Image{ fromFile = P("layers", "squares.png") }, Point(0, 0))
  for j = 2, #order do
    m:newCel(layers[order[j]], i, Image{ fromFile = P("layers", idx .. order[j] .. ".png") }, Point(0, 0))
  end
  local t = m:newTag(i, i); t.name = name
  m.frames[i].duration = 1.0
end
m:saveAs(P("merge_examples.aseprite"))
m:saveCopyAs(P("export", "merge_.png"))   -- numbered PNG per frame
-- left open so you can look at it
print("done: weapons.aseprite, merge_examples.aseprite, export\\*.png")
