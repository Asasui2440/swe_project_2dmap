import json
from .tileset import get_default_tile_sets


class MapData:
    """マップデータとその入出力ロジックを管理するクラス (Model)"""

    def __init__(self, width=20, height=15, tile_size=32, tile_sets=None):
        self.width = width
        self.height = height
        self.tile_size = tile_size

        # タイルセット定義
        self.tile_sets = tile_sets or get_default_tile_sets()
        self._rebuild_tile_lookup()
        self.current_tileset = next(iter(self.tile_sets))
        self.current_tile_id = self.tile_sets[self.current_tileset][0]["id"]

        # タイルデータを初期化
        default_tile_id = self.tile_sets[self.current_tileset][0]["id"]
        self.data = [[default_tile_id for _ in range(width)] for _ in range(height)]

    def get_tile_id(self, x, y):
        """指定座標のタイルIDを取得"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[y][x]
        return 0

    def set_tile_id(self, x, y, tile_id):
        """指定座標のタイルIDを設定"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.data[y][x] = tile_id
            return True
        return False

    def resize(self, width, height, fill_tile_id=None):
        """マップサイズを変更。既存データを保ちながら拡張/縮小する"""
        fill_id = fill_tile_id
        if fill_id is None:
            fill_id = self.tile_sets[self.current_tileset][0]["id"]

        new_data = [[fill_id for _ in range(width)] for _ in range(height)]
        for y in range(min(self.height, height)):
            for x in range(min(self.width, width)):
                new_data[y][x] = self.data[y][x]

        self.width = width
        self.height = height
        self.data = new_data

    def get_tileset_names(self):
        return list(self.tile_sets.keys())

    def get_tiles_for_set(self, name):
        return self.tile_sets.get(name, [])

    def set_current_tileset(self, name):
        if name in self.tile_sets:
            self.current_tileset = name
            # タイルセットを切り替えた際、存在しないタイルIDだったらデフォルトに戻す
            tile_ids = [tile["id"] for tile in self.tile_sets[name]]
            if self.current_tile_id not in tile_ids:
                self.current_tile_id = tile_ids[0]
            return True
        return False

    def set_current_tile(self, tile_id):
        if tile_id in self.tile_lookup:
            self.current_tile_id = tile_id
            return True
        return False

    def get_tile_definition(self, tile_id):
        return self.tile_lookup.get(tile_id)

    def save_map(self, file_path):
        """マップデータをJSONファイルに保存"""
        map_info = {
            "width": self.width,
            "height": self.height,
            "tile_size": self.tile_size,
            "tile_sets": self.tile_sets,
            "current_tileset": self.current_tileset,
            "current_tile_id": self.current_tile_id,
            # 二次元リストを一次元に平坦化して保存
            "data": [tile for row in self.data for tile in row],
        }
        with open(file_path, "w") as f:
            json.dump(map_info, f, indent=4)

    def load_map(self, file_path):
        """マップデータをJSONファイルから読み込み、自身のプロパティを更新"""
        with open(file_path, "r") as f:
            map_info = json.load(f)

        self.width = map_info["width"]
        self.height = map_info["height"]
        self.tile_size = map_info["tile_size"]

        if "tile_sets" in map_info:
            self.tile_sets = map_info["tile_sets"]
        else:
            # 互換性確保: 旧データの場合はデフォルト設定
            self.tile_sets = get_default_tile_sets()
        self._rebuild_tile_lookup()

        self.current_tileset = map_info.get(
            "current_tileset", next(iter(self.tile_sets))
        )
        if self.current_tileset not in self.tile_sets:
            self.current_tileset = next(iter(self.tile_sets))

        self.current_tile_id = map_info.get(
            "current_tile_id", self.tile_sets[self.current_tileset][0]["id"]
        )
        if self.current_tile_id not in self.tile_lookup:
            self.current_tile_id = self.tile_sets[self.current_tileset][0]["id"]

        # 読み込んだ一次元データを二次元リストに戻す
        flat_data = map_info["data"]
        new_data = []
        for i in range(self.height):
            new_data.append(flat_data[i * self.width : (i + 1) * self.width])

        self.data = new_data

        # 成功時に True を返す (Controllerで利用)
        return True

    def _rebuild_tile_lookup(self):
        self.tile_lookup = {}
        for tiles in self.tile_sets.values():
            for tile in tiles:
                self.tile_lookup[tile["id"]] = tile
