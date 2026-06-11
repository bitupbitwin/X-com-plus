import sys
import traceback
from pathlib import Path

MIN_PYTHON = (3, 8)
ERROR_LOG = Path(__file__).resolve().with_name("xcom_error.log")


def _excepthook(etype, value, tb):
    """未捕获异常写日志并弹窗，避免无声闪退。"""
    msg = "".join(traceback.format_exception(etype, value, tb))
    try:
        ERROR_LOG.write_text(msg, encoding="utf-8")
    except OSError:
        pass
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        if QApplication.instance() is not None:
            QMessageBox.critical(None, "程序异常",
                                 f"{msg}\n已写入 {ERROR_LOG}")
    except Exception:
        pass
    sys.__excepthook__(etype, value, tb)


def main():
    if sys.version_info < MIN_PYTHON:
        sys.exit(f"需要 Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} 及以上，"
                 f"当前为 {sys.version.split()[0]}")
    sys.excepthook = _excepthook

    from PySide6.QtWidgets import QApplication
    from xcom.main_window import MainWindow

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
