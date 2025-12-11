def get_default_tile_sets():
    """プリセットのタイルセット定義を返す"""
    return {
        "フィールド": [
            {"id": 0, "name": "Grass", "color": "#64b464"},
            {"id": 1, "name": "Road", "color": "#cda673"},
            {"id": 2, "name": "Water", "color": "#4fa3d1"},
            {"id": 3, "name": "Mountain", "color": "#8e8b7b"},
        ],
        "ダンジョン": [
            {"id": 4, "name": "Floor", "color": "#b0b0b0"},
            {"id": 5, "name": "Wall", "color": "#5c5c5c"},
            {"id": 6, "name": "Water Pit", "color": "#1f4c68"},
            {"id": 7, "name": "Lava", "color": "#d35400"},
        ],
    }
