-- Writes the hair layer of every tagged frame in m_head_hair.aseprite / f_head_hair.aseprite back to
-- ../<sex>_hair_<tag>.png (200x200, transparent), and the head layer of frame 1 to ../<sex>_head_skin.png.
local dir = app.fs.filePath(debug.getinfo(1, "S").source:sub(2))
local src = app.fs.joinPath(dir, "..")
for _, sex in ipairs({"m", "f"}) do
  local f = app.fs.joinPath(dir, sex .. "_head_hair.aseprite")
  if app.fs.isFile(f) then
    local spr = app.open(f)
    local function layer(name) for _, l in ipairs(spr.layers) do if l.name == name then return l end end end
    local function full(cel)
      local img = Image(spr.width, spr.height, ColorMode.RGB)
      if cel then img:drawImage(cel.image, cel.position) end
      return img
    end
    full(layer("head"):cel(1)):saveAs(app.fs.joinPath(src, sex .. "_head_skin.png"))
    for _, tag in ipairs(spr.tags) do
      full(layer("hair"):cel(tag.fromFrame.frameNumber)):saveAs(app.fs.joinPath(src, sex .. "_hair_" .. tag.name .. ".png"))
    end
    spr:close()
  end
end
