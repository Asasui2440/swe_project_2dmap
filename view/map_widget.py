from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QBrush, QColor, QPen, QMouseEvent
from PyQt6.QtCore import Qt, QRect


# --- MapWidget: 実際にマップを描画するカスタムウィジェット ---
class MapWidget(QWidget):
    def __init__(self, map_data, controller):
        super().__init__()
        self.map_data = map_data
        self.controller = controller

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

    def paintEvent(self, event):
        """描画処理。Modelのデータに基づいてタイルとグリッドを描画"""
        painter = QPainter(self)
        ts = self.map_data.tile_size

        # グリッド線用のペン
        painter.setPen(QPen(QColor(100, 100, 100), 1))

        for y in range(self.map_data.height):
            for x in range(self.map_data.width):
                tile_id = self.map_data.get_tile_id(x, y)
                rect = QRect(x * ts, y * ts, ts, ts)

                # タイルの描画
                tile_def = self.map_data.get_tile_definition(tile_id)
                color_value = tile_def["color"] if tile_def else "#000000"
                color = QColor(color_value)
                painter.setBrush(QBrush(color))
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
        x = event.position().x() // self.map_data.tile_size
        y = event.position().y() // self.map_data.tile_size

        if 0 <= x < self.map_data.width and 0 <= y < self.map_data.height:
            self.map_data.set_tile_id(int(x), int(y), self.map_data.current_tile_id)
            self.update()  # 再描画
