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

### Option 1: FreeCAD Addon Manager from GitHub URL

1. Open `Tools -> Addon manager` in FreeCAD.
2. Use the install-from-URL option (Git repository URL).
3. Paste `https://github.com/larsnygard/SnartScrews`.
4. Install and restart FreeCAD.
5. Open the `SnartScrews` workbench and run `Create Screw`.

### Option 2: Manual install

1. Download this repository as ZIP and extract to your FreeCAD `Mod` folder as `SnartScrews`.
2. Restart FreeCAD.
3. Open the `SnartScrews` workbench and run `Create Screw`.

## Notes

- The generated thread is a geometric helical thread built from a swept triangular profile.
- Presets are editable after selection.

## Addon Manager Notes

- This repo is prepared for direct installation from your own GitHub URL.
- It does not need inclusion in the public `FreeCAD/FreeCAD-addons` catalog for personal use.
