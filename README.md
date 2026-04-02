# SnartScrews FreeCAD Addon

This addon adds a `SnartScrews` workbench with a dialog for creating screws.

## Features

- Head type: `Hex`, `Phillips`, `Unbraco (Socket Cap)`, `Pan`, `Flat`
- Head width and head length
- Screw length and diameter
- Thread type: `Metric ISO`, `Unified`, `Custom`
- Thread depth, angle, pitch, tolerance
- Presets dropdown with `Custom`, `M2`, `M3`, `M4`

## Install

1. Zip this folder or keep it as an addon directory.
2. Install it via FreeCAD Addon Manager or place it in your Mod folder.
3. Restart FreeCAD.
4. Open the `SnartScrews` workbench and run `Create Screw`.

## Notes

- The generated thread is a geometric helical thread built from a swept triangular profile.
- Presets are editable after selection.

## Addon Manager Listing

If you copied this folder manually into `Mod`, it installs locally but does not appear as a searchable entry in Addon Manager. That is expected.

To make `SnartScrews` appear in Addon Manager:

1. Publish this addon in a public repository (GitHub/GitLab/Codeberg).
2. Update `package.xml` with your real repository URL and maintainer info.
3. Open an issue in `FreeCAD/FreeCAD-addons` using their addon submission template.
4. Submit a PR to `FreeCAD/FreeCAD-addons` that adds:
	- an entry for your repo in `AddonCatalog.json` (FreeCAD 1.0+)
	- a `.gitmodules` entry (legacy compatibility)

Reference: `https://github.com/FreeCAD/FreeCAD-addons/blob/master/Documentation/Submission.md`
