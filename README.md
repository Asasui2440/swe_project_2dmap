# 2D Map Editor (PyQt6)

A lightweight tile-based map editor built with PyQt6. Choose from multiple tilesets, paint tiles onto a customizable grid, and save/load your creations as JSON.

## Features

- Multiple tilesets (field and dungeon) with color-coded tiles.
- Click a tile button to select it, then click the map grid to paint.
- Adjustable grid dimensions (width × height) with live resizing.
- JSON save/load that preserves grid dimensions and available tiles.

## Requirements

- Python 3.12+
- PyQt6 (install via `pip install PyQt6`)

## Running the editor

```bash
cd /Users/sui/Desktop/2025/後期/ソフトウェア工学/2dmap
conda activate pyqt6_env
python3 main.py
```

## Usage tips

1. Pick a tileset from the dropdown on the right.
2. Click a tile button to make it the active brush.
3. Click anywhere on the grid to place the selected tile.
4. Adjust the width/height spinboxes and press **サイズ変更** to resize the grid.
5. Use **File → Save Map** / **Load Map** to persist or restore your maps (JSON files).

Happy mapping!
