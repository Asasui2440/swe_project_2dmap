import sys

from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox

# ↑ QAction はここからインポート
# 自身の作成したモジュールをインポート
from model import MapData
from view import MainWindow


# Controller的な役割を担うクラス
class MapEditorController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        # Modelのインスタンス化
        self.map_data = MapData(width=20, height=15, tile_size=32)
        # Viewのインスタンス化
        self.main_window = MainWindow(self)

        # アクションとロジックの接続
        self.main_window.save_action.triggered.connect(self.save_map)
        self.main_window.load_action.triggered.connect(self.load_map)

    def set_current_tile(self, tile_id):
        """Modelの現在のタイルIDを設定"""
        if self.map_data.set_current_tile(tile_id):
            print(f"Current tile set to ID: {tile_id}")

    def set_current_tileset(self, name):
        if self.map_data.set_current_tileset(name):
            self.main_window.update_map_widget()
            return True
        return False

    def place_tile(self, x, y):
        """指定されたグリッド座標に現在のタイルを配置 (Modelを操作)"""
        if self.map_data.set_tile_id(x, y, self.map_data.current_tile_id):
            print(f"Placed tile ID {self.map_data.current_tile_id} at ({x}, {y})")

    def resize_map(self, width, height):
        self.map_data.resize(width, height)
        self.main_window.update_map_widget()

    def save_map(self):
        """保存処理ロジック (Controller)"""
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window, "Save Map", "", "Map Files (*.json)"
        )
        if file_path:
            try:
                self.map_data.save_map(file_path)
                QMessageBox.information(
                    self.main_window, "Success", "Map saved successfully."
                )
            except Exception as e:
                QMessageBox.critical(
                    self.main_window, "Error", f"Failed to save map: {e}"
                )

    def load_map(self):
        """読み込み処理ロジック (Controller)"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window, "Load Map", "", "Map Files (*.json)"
        )
        if file_path:
            try:
                # 読み込み処理 (Modelを操作)
                self.map_data.load_map(file_path)

                # Viewの更新 (Modelの内容が変わったことをViewに伝える)
                self.main_window.refresh_from_model()

                QMessageBox.information(
                    self.main_window, "Success", "Map loaded successfully."
                )
            except Exception as e:
                QMessageBox.critical(
                    self.main_window, "Error", f"Failed to load map: {e}"
                )

    def run(self):
        self.main_window.show()
        sys.exit(self.app.exec())


if __name__ == "__main__":
    editor = MapEditorController()
    editor.run()
