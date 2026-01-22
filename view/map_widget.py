from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QBrush, QColor, QPen, QMouseEvent, QPixmap
from PyQt6.QtCore import Qt, QRect


# --- MapWidget: 実際にマップを描画するカスタムウィジェット ---
class MapWidget(QWidget):
    def __init__(self, map_data, controller):
        super().__init__()
        self.map_data = map_data
        self.controller = controller
        self._pixmap_cache: dict[tuple[str, int], QPixmap] = {}

        self.update_dimensions()
        self.setMouseTracking(True)  # マウス移動をトラッキング
        self.dragging = False  # ドラッグ状態の初期化

    def update_dimensions(self):
        """現在のマップサイズに合わせてウィジェットの大きさを再設定"""
        self.setFixedSize(
            self.map_data.width * self.map_data.tile_size,
            self.map_data.height * self.map_data.tile_size,
        )
        self.updateGeometry()
        self._pixmap_cache.clear()

    def paintEvent(self, event):
        """描画処理。表示領域のタイルのみを描画（最適化）"""
        painter = QPainter(self)
        ts = self.map_data.tile_size

        # 描画が必要な領域を取得
        update_rect = event.rect()

        # 描画が必要なタイルの範囲を計算
        start_x = max(0, update_rect.left() // ts)
        start_y = max(0, update_rect.top() // ts)
        end_x = min(self.map_data.width, (update_rect.right() // ts) + 1)
        end_y = min(self.map_data.height, (update_rect.bottom() // ts) + 1)

        # グリッド線用のペン
        grid_pen = QPen(QColor(100, 100, 100), 1)

        # 表示領域内のタイルのみを描画
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
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
                        painter.setPen(grid_pen)
                        painter.drawRect(rect)
                else:
                    color_value = tile_def["color"] if tile_def else "#000000"
                    painter.setBrush(QBrush(QColor(color_value)))
                    painter.setPen(grid_pen)
                    painter.drawRect(rect)

                # グリッド線の描画
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(grid_pen)
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
        ts = self.map_data.tile_size
        x = int(event.position().x() // ts)
        y = int(event.position().y() // ts)

        if 0 <= x < self.map_data.width and 0 <= y < self.map_data.height:
            self.map_data.set_tile_id(x, y, self.map_data.current_tile_id)
            # 変更されたタイルのみ再描画
            self.update(QRect(x * ts, y * ts, ts, ts))
