-- Expedition: Brave Unknown - build the portrait part files for editing in Aseprite.
-- Makes, next to this script, for each sex (m, f):
--   <sex>_hair.aseprite    one frame per hairstyle      layers: head, hair
--   <sex>_eyes.aseprite    one frame per eye pair       layers: head (locked), eyes, iris
--   <sex>_bodies.aseprite  one frame per class outfit   layers: head (locked), body_skin, body
-- Each frame is tagged with its style name. Use the tags (timeline) to jump between styles.
--
-- Colours: head, hair, iris and body_skin are GRAYSCALE value maps - the game tints them (skin, hair and eye
-- colours). Keep them gray: black = deepest shadow, white = highlight. eyes and body are drawn in final colours.
-- WARNING: running this again overwrites the .aseprite files with the current PNGs (export first!).
--
-- Run in Aseprite: File > Scripts > Open Scripts Folder, copy this whole folder there, then File > Scripts >
-- build_portrait_parts. Or from a terminal: Aseprite -b --script build_portrait_parts.lua
local here = debug.getinfo(1, "S").source:gsub("^@", "")
local C = dofile(app.fs.joinPath(app.fs.filePath(here), "portrait_common.lua"))

local made = {}
for _, sex in ipairs(C.SEXES) do
  local headPath = app.fs.joinPath(C.SRC, sex .. "_head_skin.png")
  for _, part in ipairs(C.ORDER) do
    local P = C.PARTS[part]
    local styles = C.styles(part, sex)
    if #styles > 0 and app.fs.isFile(headPath) then
      local spr = Sprite(200, 200, ColorMode.RGB)
      local layers = {}
      for i, lname in ipairs(P.layers) do
        local l = (i == 1) and spr.layers[1] or spr:newLayer()
        l.name = lname
        layers[lname] = l
      end
      local head = Image { fromFile = headPath }
      for f, style in ipairs(styles) do
        if f > 1 then spr:newEmptyFrame() end
        for _, lname in ipairs(P.layers) do
          local img
          if lname == "head" then
            img = head
          else
            local p = app.fs.joinPath(C.SRC, P.file(sex, style, lname))
            if app.fs.isFile(p) then img = Image { fromFile = p } end
          end
          if img then spr:newCel(layers[lname], f, img, Point(0, 0)) end
        end
        local tag = spr:newTag(f, f)
        tag.name = style
      end
      for lname, _ in pairs(P.ref) do layers[lname].isEditable = false end
      local out = C.aseFile(part, sex)
      spr:saveAs(out)
      spr:close()
      table.insert(made, app.fs.fileName(out) .. " (" .. #styles .. ")")
    end
  end
end
if app.isUIAvailable then
  app.alert { title = "Portrait parts", text = { "Built:", table.concat(made, ", ") } }
else
  print("Built: " .. table.concat(made, ", "))
end
