-- Expedition: Brave Unknown - write edited portrait parts back to the PNG layers.
-- Reads <sex>_hair / _eyes / _bodies .aseprite next to this script and saves every editable layer of every tagged
-- frame as a 200x200 PNG in the folder above (overwriting the old PNG). Locked reference layers are skipped.
-- An empty layer in a frame deletes nothing: that PNG is simply left as it was.
-- Save your .aseprite files first, then run File > Scripts > export_portrait_parts
-- (or: Aseprite -b --script export_portrait_parts.lua). Then commit the changed PNGs.
local here = debug.getinfo(1, "S").source:gsub("^@", "")
local C = dofile(app.fs.joinPath(app.fs.filePath(here), "portrait_common.lua"))

local count, files = 0, {}
for _, sex in ipairs(C.SEXES) do
  for _, part in ipairs(C.ORDER) do
    local P = C.PARTS[part]
    local path = C.aseFile(part, sex)
    if app.fs.isFile(path) then
      local spr = app.open(path)
      local byName = {}
      for _, l in ipairs(spr.layers) do byName[l.name] = l end
      for _, tag in ipairs(spr.tags) do
        local frame = tag.fromFrame.frameNumber
        for _, lname in ipairs(P.layers) do
          local outName = P.file(sex, tag.name, lname)
          local layer = byName[lname]
          if outName and layer and not P.ref[lname] then
            -- the head is shared: export it once, from the first frame of the hair file
            if not (lname == "head" and frame ~= 1) then
              local cel = layer:cel(frame)
              if cel then
                local img = Image(spr.width, spr.height, ColorMode.RGB)
                img:drawImage(cel.image, cel.position)
                img:saveAs(app.fs.joinPath(C.SRC, outName))
                count = count + 1
              end
            end
          end
        end
      end
      spr:close()
      table.insert(files, app.fs.fileName(path))
    end
  end
end
local msg = "Exported " .. count .. " PNG layers from " .. table.concat(files, ", ")
if app.isUIAvailable then app.alert { title = "Portrait parts", text = msg } else print(msg) end
