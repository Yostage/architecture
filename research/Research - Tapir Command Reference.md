# Research - Tapir Command Reference

Full inventory of JSON commands registered by the Tapir Archicad add-on. Pulled from [`AddOnMain.cpp`](https://github.com/ENZYME-APD/tapir-archicad-automation/blob/main/archicad-addon/Sources/AddOnMain.cpp) on 2026-05-18. These sit in the **`TapirCommand`** namespace and stack *on top of* Archicad's small official JSON API. Both community MCP servers ([[Research - Archicad MCPs]]) wrap these.

**~134 Tapir commands across 14 groups.** Version column = the Tapir release that added the command — useful for spotting recently-added stuff.

## Topo pilot — commands likely to matter
The 3D-topo-from-survey pilot ([[Synthesis - Automation Opportunities]]) probably only needs a handful:
- **`CreateMeshes`** — the actual mesh-element creator. Core of the pilot.
- **`GetElementsByType`** / **`GetSelectedElements`** — find the imported 2D polylines.
- **`GetDetailsOfElements`** — read polyline geometry / Z values.
- **`DeleteElements`** — clean up the source 2D lines after mesh is built.
- **`HighlightElements`** — visual feedback while debugging.
- **`CreateLayers`** / **`GetAttributesByType`** — manage the mesh's layer.
- **`FitInWindow`** — center the view on the new mesh for the user.

Reading the source DWG happens *outside* Archicad (Python + ezdxf). Tapir's surface starts after polylines exist inside the project.

---

## Application Commands (5)
| Command | Ver | Description |
|---|---|---|
| `GetAddOnVersion` | 0.1.0 | Tapir add-on version |
| `GetArchicadLocation` | 0.1.0 | Path to running Archicad executable |
| `QuitArchicad` | 0.1.0 | Quit Archicad |
| `GetCurrentWindowType` | 1.0.7 | Type of active window (Plan / 3D / Section / etc.) |
| `ChangeWindow` | 1.3.1 | Switch active window |

## Project Commands (15)
| Command | Ver | Description |
|---|---|---|
| `GetProjectInfo` | 0.1.0 | Project file/path info |
| `GetProjectInfoFields` | 0.1.2 | All project info field names + values |
| `SetProjectInfoField` | 0.1.2 | Set a project info field |
| `GetStories` | 1.1.5 | Story (floor) structure |
| `SetStories` | 1.1.5 | Replace story structure |
| `GetHotlinks` | 0.1.0 | Hotlink module paths (tree-structured) |
| `OpenProject` | 1.0.7 | Open a project file |
| `CloseProject` | 1.3.1 | Close current project |
| `SaveProject` | 1.3.1 | Save current project |
| `GetCalculationUnits` | 1.4.0 | Project's calculation units |
| `GetGeoLocation` | 1.1.6 | Project geolocation |
| `SetGeoLocation` | 1.2.9 | Set project geolocation |
| `IFCFileOperation` | 1.2.6 | Execute an IFC import/export op |
| `PrintView` | 1.3.1 | Print current view |
| `RebuildView` | 1.4.1 | Rebuild current view |

## Element Commands (49)

### Selection & query
| Command | Ver | Description |
|---|---|---|
| `GetSelectedElements` | 0.1.0 | Currently selected elements |
| `GetElementsByType` | 1.0.7 | All elements of a given type (with optional filter) |
| `GetAllElements` | 1.0.7 | All elements (with optional filter) |
| `ChangeSelectionOfElements` | 1.0.7 | Add/remove elements from selection |
| `FilterElements` | 1.0.7 | Test elements against criteria |
| `HighlightElements` | 1.0.3 | Highlight elements (empty array = clear) |

### Read element details
| Command | Ver | Description |
|---|---|---|
| `GetDetailsOfElements` | 1.0.7 | Geometry + parameters |
| `Get3DBoundingBoxes` | 1.1.2 | 3D bounding boxes |
| `GetSubelementsOfHierarchicalElements` | 1.0.6 | Children of hierarchical elements |
| `GetConnectedElements` | 1.1.4 | Connected elements |
| `GetZoneBoundaries` | 1.2.3 | Zone connections / neighbour zones |
| `GetCollisions` | 1.2.2 | Collisions between two element groups |
| `GetElementPreviewImage` | 1.2.7 | Element preview image |
| `GetRoomImage` | 1.2.7 | Zone (room) image |

### Modify / move / delete
| Command | Ver | Description |
|---|---|---|
| `SetDetailsOfElements` | 1.0.7 | Set floor / layer / order / etc. |
| `MoveElements` | 1.0.2 | Translate by vector |
| `DeleteElements` | 1.2.1 | Delete elements |

### Create — primary geometry
| Command | Ver | Description |
|---|---|---|
| `CreateWalls` | 1.4.0 | Wall elements |
| `CreateBeams` | 1.4.0 | Beam elements |
| `CreateColumns` | 1.0.3 | Column elements |
| `CreateSlabs` | 1.0.3 | Slab elements |
| `CreateRoofs` | 1.4.0 | Multi-plane roofs (footprint + profile) |
| `CreateMorphs` | 1.4.0 | Morph elements from box definitions |
| `CreateMeshes` | 1.1.9 | **Mesh elements (topo)** |
| `CreateZones` | 1.1.8 | Zone elements |
| `CreatePolylines` | 1.1.5 | Polyline elements |
| `CreateObjects` | 1.0.3 | Library Object elements |
| `CreateLamps` | 1.4.1 | Lamp elements |

### Create — openings & labels
| Command | Ver | Description |
|---|---|---|
| `CreateWindows` | 1.4.0 | Windows in host walls |
| `CreateDoors` | 1.4.0 | Doors in host walls |
| `CreateOpenings` | 1.4.0 | Openings in host elements |
| `CreateLabels` | 1.2.5 | Label elements |

### Create — dimensions
| Command | Ver | Description |
|---|---|---|
| `CreateAssociativeDimensions` | 1.4.0 | Linear dims from witness-point refs |
| `CreateAssociativeDimensionsOnSection` | 1.4.0 | Dims on sections using element presets |
| `CreateWallThicknessDimensions` | 1.4.0 | Wall thickness dims |

### Modify (per-type)
`ModifyWalls`, `ModifyBeams`, `ModifySlabs`, `ModifyColumns`, `ModifyWindows`, `ModifyDoors`, `ModifyMorphs`, `ModifyRoofs` — all 1.4.0, all "modify based on given parameters."

### GDL parameters
| Command | Ver | Description |
|---|---|---|
| `GetGDLParametersOfElements` | 1.0.8 | Read GDL params (name, type, value) |
| `SetGDLParametersOfElements` | 1.0.8 | Write GDL params |

### Classifications
| Command | Ver | Description |
|---|---|---|
| `GetClassificationsOfElements` | 1.0.7 | Element classifications (works on subelements) |
| `SetClassificationsOfElements` | 1.0.7 | Set classifications (omit `classificationItemId` → unclassified) |

### Notifications
| Command | Ver | Description |
|---|---|---|
| `AddElementNotificationClient` | 1.2.8 | Subscribe to element events |
| `RemoveElementNotificationClient` | 1.2.8 | Unsubscribe |

## Element Grouping Commands (1)
| Command | Ver | Description |
|---|---|---|
| `CreateGroups` | 1.4.0 | Group passed elements |

## Favorites Commands (6)
| Command | Ver | Description |
|---|---|---|
| `GetFavoritesByType` | 1.2.2 | List favorite names for an element type |
| `GetFavoritePreviewImage` | 1.2.7 | Preview image of a favorite |
| `ApplyFavoritesToElementDefaults` | 1.1.2 | Apply favorites to element defaults |
| `CreateFavoritesFromElements` | 1.1.2 | Create favorites from selection |
| `ImportFavorites` | 1.4.1 | Import from `.prefs` file/folder |
| `ExportFavorites` | 1.4.1 | Export to `.prefs` file/folder |

## Property Commands (9)
| Command | Ver | Description |
|---|---|---|
| `GetAllProperties` | 1.1.3 | All user-defined + built-in properties |
| `GetPropertyValuesOfElements` | 1.0.6 | Read property values |
| `SetPropertyValuesOfElements` | 1.0.6 | Write property values |
| `GetPropertyValuesOfAttributes` | 1.1.8 | Read property values of attributes |
| `SetPropertyValuesOfAttributes` | 1.1.8 | Write property values of attributes |
| `CreatePropertyGroups` | 1.0.7 | Create property groups |
| `DeletePropertyGroups` | 1.0.9 | Delete property groups |
| `CreatePropertyDefinitions` | 1.0.9 | Create custom property defs |
| `DeletePropertyDefinitions` | 1.0.9 | Delete custom property defs |

## Attribute Commands (8)
| Command | Ver | Description |
|---|---|---|
| `GetAttributesByType` | 1.1.3 | All attributes of a type |
| `CreateLayers` | 1.0.3 | Create/overwrite layers |
| `CreateLayerCombinations` | 1.2.4 | Create/overwrite layer combinations |
| `CreateBuildingMaterials` | 1.0.1 | Create/overwrite building materials |
| `CreateComposites` | 1.0.2 | Create/overwrite composites |
| `CreateSurfaces` | 1.2.2 | Create/overwrite surfaces |
| `GetBuildingMaterialPhysicalProperties` | 0.1.3 | Physical props of building materials |
| `GetLayerCombinations` | 1.2.4 | Layer combination details |

## Library Commands (4)
| Command | Ver | Description |
|---|---|---|
| `GetLibraries` | 1.0.1 | Loaded libraries |
| `ReloadLibraries` | 1.0.0 | Reload libraries |
| `AddFilesToEmbeddedLibrary` | 1.2.2 | Add files into the embedded library |
| `GetAvailableLibraryParts` | 1.4.1 | List library parts (filter by typeId: Door/Window/Object/Lamp) |

## Teamwork Commands (4)
| Command | Ver | Description |
|---|---|---|
| `TeamworkSend` | 0.1.0 | Send changes |
| `TeamworkReceive` | 0.1.0 | Receive changes |
| `ReserveElements` | 1.1.4 | Reserve in Teamwork |
| `ReleaseElements` | 1.1.4 | Release in Teamwork |

## Navigator Commands (14)
| Command | Ver | Description |
|---|---|---|
| `PublishPublisherSet` | 0.1.0 | Publish a publisher set |
| `UpdateDrawings` | 1.1.4 | Update given drawings |
| `GetDatabaseIdFromNavigatorItemId` | 1.1.4 | Resolve navigator item → database ID |
| `CreateDetails` | 1.4.0 | Independent Detail databases |
| `CreateWorksheets` | 1.4.0 | Independent Worksheet databases |
| `CreateLayouts` | 1.4.0 | Layouts + backing master layouts |
| `CreateSubsets` | 1.4.0 | Layout Book subsets |
| `CreateDrawings` | 1.4.0 | Drawing elements on a layout from navigator items |
| `GetModelViewOptions` | 1.1.4 | All model view options |
| `GetViewSettings` | 1.1.4 | View settings of navigator items |
| `SetViewSettings` | 1.1.4 | Set view settings |
| `GetView2DTransformations` | 1.1.7 | Zoom + rotation of 2D views |
| `Set3DCutPlanes` | 1.3.1 | Set 3D cut planes |
| `FitInWindow` | 1.3.1 | Zoom to elements / fit all |

## Issue Management Commands (10)
| Command | Ver | Description |
|---|---|---|
| `CreateIssue` | 1.0.2 | New issue |
| `DeleteIssue` | 1.0.2 | Delete issue |
| `GetIssues` | 1.0.2 | List issues |
| `AddCommentToIssue` | 1.0.6 | Comment on issue |
| `GetCommentsFromIssue` | 1.0.6 | Issue comments |
| `AttachElementsToIssue` | 1.0.6 | Attach elements |
| `DetachElementsFromIssue` | 1.0.6 | Detach elements |
| `GetElementsAttachedToIssue` | 1.0.6 | Attached elements (filtered by attachment type) |
| `ExportIssuesToBCF` | 1.0.6 | Export to BCF |
| `ImportIssuesFromBCF` | 1.0.6 | Import from BCF |

## Revision Management Commands (5)
| Command | Ver | Description |
|---|---|---|
| `GetRevisionIssues` | 1.1.9 | All revision issues |
| `GetRevisionChanges` | 1.1.9 | All revision changes |
| `GetDocumentRevisions` | 1.1.9 | All document revisions |
| `GetCurrentRevisionChangesOfLayouts` | 1.1.9 | Last-revision changes of given layouts |
| `GetRevisionChangesOfElements` | 1.1.9 | Changes attached to given elements |

## Design Options Commands (3) *(Archicad 29+)*
| Command | Ver | Description |
|---|---|---|
| `GetDesignOptions` | 1.2.9 | Existing design options |
| `GetDesignOptionSets` | 1.2.9 | Existing design option sets |
| `GetDesignOptionCombinations` | 1.2.9 | Existing design option combinations |

## Developer Commands (1)
| Command | Ver | Description |
|---|---|---|
| `GenerateDocumentation` | 1.0.7 | Generate docs (Tapir devs only) |

---

## Observations

- **Tapir 1.4.0 was a big bang** — most `Create*` and all `Modify*` element commands landed in one release. The add-on grew from "read + tweak" into "create geometry from scratch."
- **Coverage is asymmetric.** Reading is broad (geometry, properties, classifications, GDL params, attachments). Writing is targeted to specific element types — there's no generic "create element from spec." For meshes specifically, `CreateMeshes` exists and is what the topo pilot needs.
- **No DWG/PDF import command.** Bringing the 2D survey lines *into* Archicad still has to happen the manual way (or via Archicad's own File > Open / Merge), unless we use `IFCFileOperation` and a DWG→IFC pre-step. Probably easiest: pre-convert DWG outside Archicad → emit polylines directly via `CreateMeshes` parameters.
- **`CreateMeshes` is the load-bearing command for the pilot.** Schema verified 2026-05-19 — see below.

## CreateMeshes — input schema (read from source 2026-05-19)

```json
{
  "meshesData": [
    {
      "polygonCoordinates": [{"x":..,"y":..,"z":..}, ...],  // REQUIRED — the mesh outline polygon (3D)
      "polygonArcs":        [...],                          // optional — curved segments of the outline
      "holes":              [...],                          // optional — cutouts
      "sublines": [                                          // optional — leveling lines INSIDE the polygon
        {"coordinates": [{"x":..,"y":..,"z":..}, ...]},
        ...
      ],
      "level":      <number>,                                // optional — Z reference
      "skirtType":  "SurfaceOnlyWithoutSkirt" | "WithSkirt" | "SolidBodyWithSkirt",
      "skirtLevel": <number>,
      "floorIndex": <integer>
    }
  ]
}
```

**Why this is the perfect shape for the topo pilot:**
- The contour polylines from the DWG map **directly** to `sublines` — each contour becomes one subline, with each vertex carrying the contour's Z.
- The mesh perimeter (the YouTube tutorial's "don't flatten the edge" footgun) is **separately specified** as `polygonCoordinates` — Tapir's API enforces the distinction the manual workflow has to police by hand.
- One JSON, one call, one mesh. No state machine, no per-node elevation loop.

**Pilot architecture (one-shot):**
1. Parse DWG → list of `(polyline_xy_points, elevation)` from CONT-HGH + CONT-NML.
2. Compute or accept a perimeter polygon (open question — see [[Source - Lot 44 Survey DWG]]).
3. Emit one `CreateMeshes` call with sublines = contours, polygonCoordinates = perimeter.

## Sources
- [Tapir add-on docs landing page](https://enzyme-apd.github.io/tapir-archicad-automation/archicad-addon/) *(intro only; live command list comes from source)*
- [`AddOnMain.cpp` — canonical command registration](https://github.com/ENZYME-APD/tapir-archicad-automation/blob/main/archicad-addon/Sources/AddOnMain.cpp)
- [tapir-archicad-automation repo](https://github.com/ENZYME-APD/tapir-archicad-automation)
