-- Shared settings for build_portrait_parts.lua and export_portrait_parts.lua.
-- PNG layers live in the folder above this one (art_source/new_art/portraits/), all 200x200.
local M = {}

function M.here()
  local src = debug.getinfo(1, "S").source
  if src:sub(1, 1) == "@" then src = src:sub(2) end
  local d = app.fs.filePath(src)
  if d == nil or d == "" then d = app.fs.currentPath end
  return d
end

M.DIR = M.here()
-- PNG folder: one folder up (when run from the repo), or the path written in portraits_path.txt next to the
-- scripts (when the scripts were copied into Aseprite's scripts folder).
M.SRC = app.fs.joinPath(M.DIR, "..")
if not app.fs.isFile(app.fs.joinPath(M.SRC, "m_head_skin.png")) then
  local f = io.open(app.fs.joinPath(M.DIR, "portraits_path.txt"), "r")
  if f then
    local p = f:read("*l"); f:close()
    if p then M.SRC = p:gsub("^%s+", ""):gsub("[%s\\/]+$", "") end
  end
end
if not app.fs.isFile(app.fs.joinPath(M.SRC, "m_head_skin.png")) then
  error("Portrait PNGs not found. Put the full path of art_source/new_art/portraits in portraits_path.txt next to this script.")
end
-- .aseprite files are kept with the PNGs, in an "aseprite" subfolder
M.DIR = app.fs.joinPath(M.SRC, "aseprite")
M.SEXES = { "m", "f" }
M.CLASSES = { "soldier", "archer", "cleric", "mage", "warrior", "rogue" }   -- cleric = Acolyte

-- Every part file: one .aseprite per sex and part, one frame per style (tagged with the style name).
-- layers: bottom to top. "ref" layers are locked references and are never exported.
-- file(sex, style, layer) gives the PNG name for an editable layer (nil = not exported).
M.PARTS = {
  hair = {
    pattern = "^(%a)_hair_(.+)%.png$",
    layers = { "head", "hair" },
    ref = {},                                   -- head is editable here (the only place it is exported)
    file = function(sex, style, layer)
      if layer == "hair" then return sex .. "_hair_" .. style .. ".png" end
      if layer == "head" then return sex .. "_head_skin.png" end
    end,
  },
  eyes = {
    pattern = "^(%a)_eyes_(.+)_fixed%.png$",
    layers = { "head", "eyes", "iris" },
    ref = { head = true },
    file = function(sex, style, layer)
      if layer == "eyes" then return sex .. "_eyes_" .. style .. "_fixed.png" end
      if layer == "iris" then return sex .. "_eyes_" .. style .. "_iris.png" end
    end,
  },
  bodies = {
    pattern = "^(%a)_body_(.+)_fixed%.png$",
    layers = { "head", "body_skin", "body" },
    ref = { head = true },
    file = function(sex, style, layer)
      if layer == "body" then return sex .. "_body_" .. style .. "_fixed.png" end
      if layer == "body_skin" then return sex .. "_body_" .. style .. "_skin.png" end
    end,
  },
}
M.ORDER = { "hair", "eyes", "bodies" }

-- styles of one part for one sex, found from the PNG files (bodies keep the class order)
function M.styles(part, sex)
  local list, seen = {}, {}
  for _, name in ipairs(app.fs.listFiles(M.SRC)) do
    local s, style = name:match(M.PARTS[part].pattern)
    if s == sex and not seen[style] then seen[style] = true; table.insert(list, style) end
  end
  if part == "bodies" then
    local ordered = {}
    for _, c in ipairs(M.CLASSES) do if seen[c] then table.insert(ordered, c) end end
    return ordered
  end
  table.sort(list)
  return list
end

function M.aseFile(part, sex)
  return app.fs.joinPath(M.DIR, sex .. "_" .. part .. ".aseprite")
end

return M
