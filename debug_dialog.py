import sys
from PyQt6.QtWidgets import QApplication
from view import TilesetSplitDialog

app = QApplication(sys.argv)
dialog = TilesetSplitDialog(None, 800, 600)
result = dialog.exec()
print(f"Result: {result}")
h, v = dialog.get_values()
print(f"Values: H={h}, V={v}")
