# QtWidgets からインポートするもの
from typing import cast

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QSpinBox,
    QHBoxLayout,
    QGroupBox,
    QButtonGroup,
    QScrollArea,
    QAbstractButton,
)

# QtGui から QAction をインポートするように修正！
from PyQt6.QtGui import QPainter, QBrush, QColor, QPen, QAction, QMouseEvent

# ↑ QAction はここからインポート
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


# --- MainWindow: アプリケーションのメインフレーム ---
class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.setWindowTitle("Simple RPG Map Editor (PyQt6 Demo)")
        self.controller = controller

        # メインコンテナウィジェット
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # レイアウト
        main_layout = QGridLayout(main_widget)

        # 1. マップ表示エリア
        self.map_widget = MapWidget(self.controller.map_data, self.controller)
        main_layout.addWidget(self.map_widget, 0, 0, 1, 1)  # (行, 列, 縦幅, 横幅)

        # 2. タイルセット選択エリア
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)

        # タイルセット切り替え
        tileset_label = QLabel("タイルセット")
        control_layout.addWidget(tileset_label)

        self.tileset_combo = QComboBox()
        self.tileset_combo.currentTextChanged.connect(self.on_tileset_changed)
        control_layout.addWidget(self.tileset_combo)

        # タイル一覧 (スクロール可能)
        self.tile_button_group = QButtonGroup(self)
        self.tile_button_group.setExclusive(True)
        self.tile_buttons_container = QWidget()
        self.tile_buttons_layout = QGridLayout(self.tile_buttons_container)
        self.tile_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.tile_buttons_layout.setSpacing(6)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.tile_buttons_container)
        control_layout.addWidget(scroll, 1)

        # グリッドサイズ設定
        size_group = QGroupBox("グリッドサイズ")
        size_layout = QHBoxLayout(size_group)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(5, 100)
        self.width_spin.setSuffix(" 幅")
        size_layout.addWidget(self.width_spin)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(5, 100)
        self.height_spin.setSuffix(" 高")
        size_layout.addWidget(self.height_spin)

        resize_button = QPushButton("サイズ変更")
        resize_button.clicked.connect(self.on_resize_requested)
        size_layout.addWidget(resize_button)

        control_layout.addWidget(size_group)

        # ファイル操作 (保存/読み込み)
        file_group = QGroupBox("ファイル操作")
        file_layout = QHBoxLayout(file_group)

        save_button = QPushButton("保存")
        save_button.clicked.connect(self.controller.save_map)
        file_layout.addWidget(save_button)

        load_button = QPushButton("読み込み")
        load_button.clicked.connect(self.controller.load_map)
        file_layout.addWidget(load_button)

        control_layout.addWidget(file_group)

        control_layout.addStretch()

        main_layout.addWidget(control_panel, 0, 1, 1, 1)

        self._create_actions()
        self._create_menus()
        self._initialize_controls()
        self.load_tile_button = QPushButton("Load Tile")
        control_layout.addWidget(self.load_tile_button)

    def _create_actions(self):
        # 保存アクション
        self.save_action = QAction("&Save Map", self)
        self.save_action.setShortcut("Ctrl+S")

        # 読み込みアクション
        self.load_action = QAction("&Load Map", self)
        self.load_action.setShortcut("Ctrl+O")

    def _create_menus(self):
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.load_action)

    def update_map_widget(self):
        """マップデータが読み込まれたときなどにMapWidgetを更新/再描画する"""
        # MapWidgetのサイズと内容をModelのデータに合わせて更新
        self.map_widget.update_dimensions()
        self.map_widget.update()  # 再描画を要求

        # レイアウトを更新してサイズ変更を反映
        self.centralWidget().layout().update()

        # スピンボックスの値も反映
        self._sync_dimension_controls()

    def _initialize_controls(self):
        self._populate_tileset_combo()
        self._sync_dimension_controls()

    def _populate_tileset_combo(self):
        names = self.controller.map_data.get_tileset_names()
        self.tileset_combo.blockSignals(True)
        self.tileset_combo.clear()
        self.tileset_combo.addItems(names)
        current = getattr(
            self.controller.map_data, "current_tileset", names[0] if names else ""
        )
        index = self.tileset_combo.findText(current)
        if index >= 0:
            self.tileset_combo.setCurrentIndex(index)
        self.tileset_combo.blockSignals(False)
        self._populate_tile_buttons(current)

    def _populate_tile_buttons(self, tileset_name):
        # 既存ボタンの削除
        while self.tile_buttons_layout.count():
            item = self.tile_buttons_layout.takeAt(0)
            if item is None:
                continue
            child = item.widget()
            if child is None:
                continue
            if child in self.tile_button_group.buttons():
                button = cast(QAbstractButton, child)
                self.tile_button_group.removeButton(button)
            child.deleteLater()

        tiles = self.controller.map_data.get_tiles_for_set(tileset_name)
        for idx, tile in enumerate(tiles):
            button = QPushButton(tile["name"])
            button.setCheckable(True)
            button.setMinimumHeight(40)
            button.setStyleSheet(
                f"background-color: {tile['color']}; border: 2px solid #444; color: white;"
            )
            button.clicked.connect(
                lambda checked, tile_id=tile["id"]: self.on_tile_selected(tile_id)
            )
            self.tile_button_group.addButton(button)
            row = idx // 2
            col = idx % 2
            self.tile_buttons_layout.addWidget(button, row, col)

            if tile["id"] == self.controller.map_data.current_tile_id:
                button.setChecked(True)

    def _sync_dimension_controls(self):
        self.width_spin.blockSignals(True)
        self.height_spin.blockSignals(True)
        self.width_spin.setValue(self.controller.map_data.width)
        self.height_spin.setValue(self.controller.map_data.height)
        self.width_spin.blockSignals(False)
        self.height_spin.blockSignals(False)

    def on_tileset_changed(self, name):
        if not name:
            return
        if self.controller.set_current_tileset(name):
            self._populate_tile_buttons(name)

    def on_tile_selected(self, tile_id):
        self.controller.set_current_tile(tile_id)

    def on_resize_requested(self):
        new_width = self.width_spin.value()
        new_height = self.height_spin.value()
        self.controller.resize_map(new_width, new_height)

    def refresh_from_model(self):
        """外部から呼び出してUI全体をModelに同期させる"""
        self._populate_tileset_combo()
        self.update_map_widget()
