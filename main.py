import sys
import os

# PyQt6のパスを設定（Anaconda環境での競合を回避）
_pyqt6_path = os.path.join(
    os.path.dirname(sys.executable),
    '..', 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}',
    'site-packages', 'PyQt6', 'Qt6'
)
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(_pyqt6_path, 'plugins', 'platforms')
os.environ['QT_PLUGIN_PATH'] = os.path.join(_pyqt6_path, 'plugins')
os.environ['DYLD_FRAMEWORK_PATH'] = os.path.join(_pyqt6_path, 'lib')

from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt6.QtGui import QImage

# ↑ QAction はここからインポート
# 自身の作成したモジュールをインポート
from model import MapData
from view import MainWindow
from view.main_window import TilesetSplitDialog


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

    def load_external_tile(self):
        """外部画像を選んで、タイルとして追加する"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Load Tile Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if not file_path:
            return

        try:
            new_id = self.map_data.add_external_tile(file_path, tileset_name="外部")
            # 追加したタイルセットへ切替＆選択
            self.map_data.set_current_tileset("外部")
            self.map_data.set_current_tile(new_id)
            self.main_window.refresh_from_model()
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to load tile: {e}")

    def load_external_tileset(self):
        """外部画像を読み込み、ユーザーが指定した分割数で分割して一括追加する"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Load Tileset Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if not file_path:
            return

        try:
            # 画像を読み込む
            image = QImage(file_path)
            if image.isNull():
                raise Exception("Failed to load image.")

            width = image.width()
            height = image.height()

            # 分割数を選択するダイアログを表示
            dialog = TilesetSplitDialog(self.main_window, width, height)
            if dialog.exec() != dialog.DialogCode.Accepted:
                return  # キャンセルされた場合

            h_div, v_div = dialog.get_values()
            tile_width = width // h_div
            tile_height = height // v_div

            # 保存先ディレクトリ
            save_dir = "tiles"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            base_name = os.path.splitext(os.path.basename(file_path))[0]
            tileset_name = base_name  # ファイル名をタイルセット名にする

            # タイル分割処理
            new_tile_id = -1
            count = 0

            for row in range(v_div):
                for col in range(h_div):
                    x = col * tile_width
                    y = row * tile_height

                    # 切り出し
                    tile_image = image.copy(x, y, tile_width, tile_height)

                    # 保存
                    tile_filename = f"{base_name}_{row}_{col}.png"
                    tile_path = os.path.join(save_dir, tile_filename)
                    tile_image.save(tile_path)

                    # モデルに追加
                    new_id = self.map_data.add_external_tile(
                        os.path.abspath(tile_path),
                        name=f"{base_name}_{count}",
                        tileset_name=tileset_name
                    )
                    if new_tile_id == -1:
                        new_tile_id = new_id
                    count += 1

            if count > 0:
                self.map_data.set_current_tileset(tileset_name)
                if new_tile_id != -1:
                    self.map_data.set_current_tile(new_tile_id)
                self.main_window.refresh_from_model()
                QMessageBox.information(
                    self.main_window,
                    "Success",
                    f"Successfully loaded {count} tiles ({h_div}x{v_div}) from {tileset_name}."
                )
            else:
                QMessageBox.warning(self.main_window, "Warning", "No tiles were generated.")

        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to load tileset: {e}")

if __name__ == "__main__":
    editor = MapEditorController()
    editor.run()
