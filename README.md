# Pixel Mod Tools App

> [!NOTE]
**v0.2.0-alpha.1** is in the final stages of refactoring - user interface, as well as some of the tools code, has been completely rewritten. Once complete and ready for release the old tool will be completely retired as the license conditions for the previous interface framework have changed and no longer allow free hobbyist use. The new app will fall under LGPL license, which will be reflected on this repository on update.
> 




This repository contains a collection of tools and utilities for Stardew Valley mod authors. Written primarily in Python, most will include a graphical user interface and a packaged executable (currently supporting Windows only).

## Sub-projects

*   [Recolor Tool](RecolorTool/README.md): A tool for recoloring PNG images and, optionally, creating color mappings using image inputs.
*   WIP: Alernative Textures <-> Content Patcher code and texture converter
*   WIP: Custom tile / texture size index map generator: creates a map of index numbers that can be overlayed on textures or tilesheets to simplify tile index checks
*   WIP: Sprite stitch/split based on custom attributes (e.g. stitch individual textures based on sorting orders, sub-attributes, etc)

## Recolor Tool | Roadmap

**Current Release (v0.1.0-alpha.1):**

*   Core image recoloring functionality.
*   Optional image based color mapping generation.
*   Output backup to prevent unintended overwrites.
*   Basic UI.
*   Basic input validation.
*   Tool user guide and example outputs.

**Next Release (v0.2.0 - Target: End of Jan25):**

*   Rework gui into PySide6 Framework for no installation executable package if possible
*   Color map input image structure validation and warnings
*   Color map input dynamic size selection (e.g. 1px by 1px vs 4px by 4px, etc)
*   Configuration for all-in-one image structure (choose number of columns/rows)
*   Video user guide
*   UI enhancements for clarify and readability
*   [stretch goal] include image to image color map generation (providing two identical images to scrape color mappings)

**Future Enhancements:**

*   Batch image recolors (for example for AT or FF individual textures - currently only single file selection is supported)
*  Ready-made vanilla recolor palettes for one-click use
*  Framework / Opt-in for recolor authors to provide color palettes to allow creators to quickly create compatible versions of their content (terrain tilesheets, interiors, furniture, other asset, etc) 
*  Persistent color palette naming and retention for simpler re-use across projects
*  Visual validation of inputs and outputs (display sample extracts from input files to confirm correct selection)
*  Live preview of individual color adjustments in the application gui
*  MAC OS / Linux / Web application options
