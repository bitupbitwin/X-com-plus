"""毛玻璃深色主题：深色渐变底 + 橙色光晕背景，半透明圆角玻璃面板，苹果系统橙点缀。"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPalette, QRadialGradient
from PySide6.QtWidgets import QApplication, QWidget

ACCENT = "#FF9500"  # Apple 经典系统橙


class Backdrop(QWidget):
    """主界面背景：深色底上叠两团柔和光晕，透过半透明面板形成玻璃质感。"""

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        p.fillRect(self.rect(), QColor("#15171D"))

        glow = QRadialGradient(w * 0.88, h * 0.08, max(w, h) * 0.65)
        glow.setColorAt(0.0, QColor(255, 149, 0, 64))
        glow.setColorAt(1.0, QColor(255, 149, 0, 0))
        p.fillRect(self.rect(), glow)

        cool = QRadialGradient(w * 0.06, h * 0.95, max(w, h) * 0.55)
        cool.setColorAt(0.0, QColor(86, 110, 180, 46))
        cool.setColorAt(1.0, QColor(86, 110, 180, 0))
        p.fillRect(self.rect(), cool)


def _palette() -> QPalette:
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor("#15171D"))
    pal.setColor(QPalette.WindowText, QColor("#F2F2F5"))
    pal.setColor(QPalette.Base, QColor("#1D2027"))
    pal.setColor(QPalette.Text, QColor("#E9E9EE"))
    pal.setColor(QPalette.Button, QColor("#2A2D36"))
    pal.setColor(QPalette.ButtonText, QColor("#F2F2F5"))
    pal.setColor(QPalette.Highlight, QColor(ACCENT))
    pal.setColor(QPalette.HighlightedText, QColor("#1A1208"))
    pal.setColor(QPalette.ToolTipBase, QColor("#23262E"))
    pal.setColor(QPalette.ToolTipText, QColor("#F2F2F5"))
    pal.setColor(QPalette.PlaceholderText, QColor(255, 255, 255, 90))
    return pal


QSS = """
QMainWindow, QDialog, QMessageBox, QInputDialog { background: #15171D; }
QLabel { color: #D8D8DE; background: transparent; }

QGroupBox {
    background: rgba(255,255,255,16);
    border: 1px solid rgba(255,255,255,30);
    border-radius: 14px;
    margin-top: 20px;
    padding: 8px 6px 6px 6px;
    color: #D8D8DE;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px; top: 1px;
    color: #FFB04D;
    font-weight: 600;
}

QPlainTextEdit {
    background: rgba(8,10,14,170);
    border: 1px solid rgba(255,255,255,26);
    border-radius: 12px;
    color: #E9E9EE;
    selection-background-color: #FF9500;
    selection-color: #141414;
    padding: 6px;
    font-family: Consolas, Menlo, "Courier New", monospace;
}

QLineEdit, QComboBox, QSpinBox {
    background: rgba(255,255,255,20);
    border: 1px solid rgba(255,255,255,34);
    border-radius: 8px;
    padding: 3px 8px;
    color: #F0F0F4;
    selection-background-color: #FF9500;
    selection-color: #141414;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border: 1px solid #FF9500; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background: #23262E;
    border: 1px solid rgba(255,255,255,40);
    border-radius: 8px;
    color: #F0F0F4;
    selection-background-color: rgba(255,149,0,90);
    outline: none;
}

QPushButton {
    background: rgba(255,255,255,26);
    border: 1px solid rgba(255,255,255,40);
    border-radius: 9px;
    padding: 5px 14px;
    color: #F2F2F5;
}
QPushButton:hover { background: rgba(255,255,255,44); }
QPushButton:pressed { background: rgba(255,255,255,16); }
QPushButton:disabled { color: rgba(255,255,255,70); background: rgba(255,255,255,10); }
QPushButton#primary {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFAA33, stop:1 #FF8A00);
    border: 1px solid rgba(255,200,120,150);
    color: #221302;
    font-weight: 700;
}
QPushButton#primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFB54D, stop:1 #FF9500);
}
QPushButton#primary:pressed { background: #E07F00; }

QCheckBox { color: #D8D8DE; spacing: 6px; background: transparent; }
QCheckBox::indicator {
    width: 15px; height: 15px;
    border-radius: 5px;
    background: rgba(255,255,255,22);
    border: 1px solid rgba(255,255,255,55);
}
QCheckBox::indicator:hover { border: 1px solid rgba(255,170,60,160); }
QCheckBox::indicator:checked { background: #FF9500; border: 1px solid #FFAD42; }

QTabWidget::pane {
    background: rgba(255,255,255,12);
    border: 1px solid rgba(255,255,255,26);
    border-radius: 12px;
    top: -1px;
}
QTabBar::tab {
    background: transparent;
    color: #A8A8B0;
    padding: 5px 16px;
    margin: 2px;
    border-radius: 8px;
}
QTabBar::tab:selected {
    background: rgba(255,149,0,46);
    color: #FFB04D;
    font-weight: 600;
}
QTabBar::tab:hover:!selected { background: rgba(255,255,255,24); color: #E8E8EC; }

QStatusBar { background: transparent; color: #9A9AA2; }
QStatusBar QLabel { color: #9A9AA2; }
QStatusBar::item { border: none; }

QSplitter::handle:vertical {
    background: rgba(255,255,255,22);
    height: 5px;
    margin: 2px 10px;
    border-radius: 2px;
}
QSplitter::handle:vertical:hover { background: rgba(255,149,0,120); }

QMenu {
    background: #23262E;
    border: 1px solid rgba(255,255,255,40);
    border-radius: 10px;
    padding: 4px;
    color: #F0F0F4;
}
QMenu::item { padding: 5px 22px; border-radius: 6px; }
QMenu::item:selected { background: rgba(255,149,0,90); color: #FFFFFF; }

QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
QScrollBar::handle:vertical {
    background: rgba(255,255,255,50);
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: rgba(255,149,0,140); }
QScrollBar:horizontal { background: transparent; height: 10px; margin: 2px; }
QScrollBar::handle:horizontal {
    background: rgba(255,255,255,50);
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: rgba(255,149,0,140); }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; width: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }
"""


def apply_theme(window):
    app = QApplication.instance()
    app.setStyle("Fusion")
    app.setPalette(_palette())
    window.setStyleSheet(QSS)
