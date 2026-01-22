from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtGui import QPainter, QBrush, QColor, QPen, QMouseEvent, QPixmap, QResizeEvent
from PyQt6.QtCore import Qt, QRect


# --- MapWidget: 実際にマップを描画するカスタムウィジェット ---
class MapWidget(QWidget):
    def __init__(self, map_data, controller):
        super().__init__()
        self.map_data = map_data
        self.controller = controller
        self._pixmap_cache: dict[tuple[str, int], QPixmap] = {}
        self._current_tile_size = self.map_data.tile_size  # 動的なタイルサイズ

        self.setMouseTracking(True)  # マウス移動をトラッキング
        self.dragging = False  # ドラッグ状態の初期化

        # サイズポリシーを設定（ウィンドウに合わせて拡大縮小）
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(100, 100)

    def update_dimensions(self):
        """現在のマップサイズに合わせてタイルサイズを再計算"""
        self._calculate_tile_size()
        self.update()

    def _calculate_tile_size(self):
        """ウィジェットのサイズからタイルサイズを計算"""
        if self.map_data.width > 0 and self.map_data.height > 0:
            # ウィジェットのサイズに収まるようにタイルサイズを計算
            tile_width = self.width() // self.map_data.width
            tile_height = self.height() // self.map_data.height
            # 正方形のタイルを維持するため、小さい方を使用
            self._current_tile_size = max(8, min(tile_width, tile_height))  # 最小8px

    def resizeEvent(self, event: QResizeEvent):
        """ウィジェットのリサイズ時にタイルサイズを再計算"""
        self._calculate_tile_size()
        # キャッシュをクリア（サイズが変わったため）
        self._pixmap_cache.clear()
        super().resizeEvent(event)

    def paintEvent(self, event):
        """描画処理。Modelのデータに基づいてタイルとグリッドを描画"""
        painter = QPainter(self)
        ts = self._current_tile_size

        # グリッド線用のペン
        painter.setPen(QPen(QColor(100, 100, 100), 1))

        for y in range(self.map_data.height):
            for x in range(self.map_data.width):
                tile_id = self.map_data.get_tile_id(x, y)
                rect = QRect(x * ts, y * ts, ts, ts)

                # タイルの描画
                tile_def = self.map_data.get_tile_definition(tile_id)
                if tile_def and tile_def.get("image"):
                    path = tile_def["image"]
                    key = (path, ts)
                    pix = self._pixmap_cache.get(key)
                    if pix is None:
                        original = QPixmap(path)
                        if not original.isNull():
                            pix = original.scaled(ts, ts, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        else:
                            pix = QPixmap()
                        self._pixmap_cache[key] = pix

                    if not pix.isNull():
                        painter.drawPixmap(rect, pix)
                    else:
                        painter.setBrush(QBrush(QColor("#000000")))
                        painter.drawRect(rect)
                else:
                    color_value = tile_def["color"] if tile_def else "#000000"
                    painter.setBrush(QBrush(QColor(color_value)))
                    painter.drawRect(rect)

                # グリッド線の描画 (タイルの四隅を描くことで実現)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRect(rect)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True  # ドラッグ開始
            self._update_tile(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:  # ドラッグ中のみ処理
            self._update_tile(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False  # ドラッグ終了

    def _update_tile(self, event: QMouseEvent):
        """マウスイベントからタイルを更新"""
        ts = self._current_tile_size
        if ts <= 0:
            return
        x = int(event.position().x() // ts)
        y = int(event.position().y() // ts)

        if 0 <= x < self.map_data.width and 0 <= y < self.map_data.height:
            self.map_data.set_tile_id(x, y, self.map_data.current_tile_id)
            self.update()  # 再描画
