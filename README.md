
# 2D Map Editor (PyQt6)

A lightweight tile-based map editor built with PyQt6. Choose from multiple tilesets, paint tiles onto a customizable grid, and save/load your creations as JSON.

## Features

- Multiple tilesets (field and dungeon) with color-coded tiles.
- Select a tile by clicking a tile button, then click or drag on the map grid to paint.
- Adjustable grid dimensions (width × height) with live resizing.
- JSON save/load that preserves grid dimensions and available tiles.
- Support for importing external tiles.

## Requirements

- Python 3.12+
- PyQt6

### Environment Setup

Run the following commands to set up the environment:

```bash
# 1. Python 3.12 で環境を作成
conda create -n pyqt6_env python=3.12 -y

# 2. 作成した環境を有効化
conda activate pyqt6_env

# 3. PyQt6 をインストール
pip install PyQt6
```
```bash
# Running the editor
conda activate pyqt6_env
python3 main.py
```

## Usage tips

1. Click a tile button to make it the active brush.
2. Click or drag anywhere on the grid to place the selected tile.
3. Adjust the width/height spinboxes and press **サイズ変更** to resize the grid.
4. Use **File → Save Map** / **Load Map** to persist or restore your maps (JSON files).
5. Click the **Load Tile** button to import a single image file (PNG, JPG, etc.) as a new tile. This tile will
     typically be added to a new tileset named "外部" (External).
6. Click the **Load Tileset** button to import a larger image file and split it into multiple individual tiles.
     A "タイルセット分割" (Tileset Split) dialog will appear, allowing you to specify how many horizontal and vertical
     divisions to make.  
   The application will then automatically save the split tiles and add them to a new tileset based on
     the original image's filename.
  
### Default Screen

<img width="600" height="300" alt="スクリーンショット 0008-01-29 10 56 11" src="https://github.com/user-attachments/assets/9a377961-ff4d-4187-b730-670ab6814573" />  

### How to use:Load tileset
1. Click the load tileset button and select the image.  
<img width="350" height="200" alt="スクリーンショット 0008-01-29 11 10 18" src="https://github.com/user-attachments/assets/e089fad1-bcea-4e39-a7c7-87eb6e1321e3" />  
  
2. A dialog will appear; set the split size.  
<img width="180" height="200" alt="スクリーンショット 0008-01-29 11 10 25" src="https://github.com/user-attachments/assets/97d63aa0-dc72-4d92-819d-fd05a81a6a07" />  
  
3. The tileset will be loaded with the image name.  
<img width="500" height="250" alt="スクリーンショット 0008-01-29 11 22 13" src="https://github.com/user-attachments/assets/12c915df-284b-4b4f-a381-62d9327143b3" />  
  

**Happy mapping!**


