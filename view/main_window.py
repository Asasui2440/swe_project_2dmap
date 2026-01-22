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
    QSizePolicy,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
)
from PyQt6.QtGui import QAction, QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize

from .map_widget import MapWidget


class TilesetSplitDialog(QDialog):
    """タイルセット分割設定ダイアログ"""
    def __init__(self, parent=None, image_width=100, image_height=100):
        super().__init__(parent)
        self.setWindowTitle("Split Tileset")
        self.image_width = image_width
        self.image_height = image_height
        
        layout = QVBoxLayout(self)
        
        info_label = QLabel(f"Image Size: {image_width} x {image_height} px")
        layout.addWidget(info_label)
        
        form_layout = QFormLayout()
        
        self.h_spin = QSpinBox()
        self.h_spin.setRange(1, 10000)
        self.h_spin.setValue(10) # Default
        self.h_spin.valueChanged.connect(self._update_preview)
        
        self.v_spin = QSpinBox()
        self.v_spin.setRange(1, 10000)
        self.v_spin.setValue(10) # Default
        self.v_spin.valueChanged.connect(self._update_preview)

        form_layout.addRow("Horizontal Div (Cols):", self.h_spin)
        form_layout.addRow("Vertical Div (Rows):", self.v_spin)
        
        layout.addLayout(form_layout)
        
        self.preview_label = QLabel("")
        layout.addWidget(self.preview_label)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self._update_preview()
        
    def _update_preview(self):
        h = self.h_spin.value()
        v = self.v_spin.value()
        tile_w = self.image_width // h
        tile_h = self.image_height // v
        self.preview_label.setText(f"Tile Size: {tile_w} x {tile_h} px")
        
    def get_values(self):
        return self.h_spin.value(), self.v_spin.value()


# --- MainWindow: アプリケーションのメインフレーム ---
class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.setWindowTitle("Simple RPG Map Editor (PyQt6 Demo)")
        self.controller = controller
        self.setMinimumSize(600, 400)  # ウィンドウの最小サイズを設定

        # メインコンテナウィジェット
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # レイアウト
        main_layout = QGridLayout(main_widget)

        # 1. マップ表示エリア（スクロール可能）
        self.map_scroll_area = QScrollArea()
        self.map_scroll_area.setWidgetResizable(False)
        self.map_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.map_scroll_area.setMinimumSize(200, 200)
        self.map_widget = MapWidget(self.controller.map_data, self.controller)
        self.map_scroll_area.setWidget(self.map_widget)
        main_layout.addWidget(self.map_scroll_area, 0, 0, 1, 1)

        # 2. タイルセット選択エリア
        control_panel = QWidget()
        control_panel.setMinimumWidth(200)  # 最小幅を設定
        control_panel.setMaximumWidth(300)  # 最大幅を制限
        control_panel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
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
        self.width_spin.setRange(5, 1000)
        size_layout.addWidget(QLabel("幅"))
        size_layout.addWidget(self.width_spin)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(5, 1000)
        size_layout.addWidget(QLabel("高さ"))
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

        # レイアウトのストレッチ設定 (マップエリアを優先的に広げる)
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 0)
        main_layout.setRowStretch(0, 1)  # 行方向もストレッチ

        self._create_actions()
        self._create_menus()
        self._initialize_controls()
        self.load_tile_button = QPushButton("Load Tile")
        self.load_tile_button.clicked.connect(self.controller.load_external_tile)
        control_layout.addWidget(self.load_tile_button)

        self.load_tileset_button = QPushButton("Load Tileset")
        self.load_tileset_button.clicked.connect(self.controller.load_external_tileset)
        control_layout.addWidget(self.load_tileset_button)

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

            # ★ここから分岐：画像タイルかどうか
            if tile.get("image"):
                button.setText("")  # 画像がある場合はテキストを非表示
                button.setToolTip(tile["name"])  # ツールチップで名前を表示
                pix = QPixmap(tile["image"])
                if not pix.isNull():
                    button.setIcon(QIcon(pix))
                    button.setIconSize(QSize(32, 32))
                # 画像のときは背景色指定しない（してもいいけど崩れやすい）
                button.setStyleSheet("border: 2px solid #444;")
            else:
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
