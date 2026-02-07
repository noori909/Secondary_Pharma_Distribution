import sys
from PySide6.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)

label = QLabel("Pharma Distribution System")
label.resize(400, 200)
label.show()

sys.exit(app.exec())
