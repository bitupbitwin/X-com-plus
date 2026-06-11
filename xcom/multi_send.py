"""多条发送：按标签分组，每标签 20 条命令（左右两列），"+"号加标签，右键管理，持久化。"""

from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QCheckBox,
    QLineEdit, QPushButton, QLabel, QSpinBox, QTabWidget,
    QInputDialog, QMessageBox, QMenu,
)

ENTRIES_PER_PAGE = 20
ROWS_PER_COLUMN = 10
CONFIG_PATH = Path(__file__).resolve().parent.parent / "xcom_multisend.json"


class TagPage(QWidget):
    """单个标签页：20 条命令，左右两列各 10 条。"""

    def __init__(self, send_entry_func, on_changed, parent=None):
        super().__init__(parent)
        self.entries = []  # [(hex_chk, line_edit), ...] 共 20 条

        grid = QGridLayout(self)
        grid.setContentsMargins(4, 4, 4, 2)
        grid.setVerticalSpacing(2)
        for col in range(2):
            base_col = col * 4
            grid.addWidget(QLabel("HEX"), 0, base_col, alignment=Qt.AlignCenter)
            grid.addWidget(QLabel("内容"), 0, base_col + 1)
            grid.setColumnStretch(base_col + 1, 1)
            for row in range(ROWS_PER_COLUMN):
                idx = col * ROWS_PER_COLUMN + row
                hex_chk = QCheckBox()
                hex_chk.toggled.connect(on_changed)
                edit = QLineEdit()
                edit.editingFinished.connect(on_changed)
                btn = QPushButton(str(idx + 1))
                btn.setFixedWidth(40)
                btn.clicked.connect(lambda _=False, i=idx: send_entry_func(i))
                grid.addWidget(hex_chk, row + 1, base_col, alignment=Qt.AlignCenter)
                grid.addWidget(edit, row + 1, base_col + 1)
                grid.addWidget(btn, row + 1, base_col + 2)
                self.entries.append((hex_chk, edit))
            if col == 0:
                grid.setColumnMinimumWidth(3, 16)  # 两列之间留间隔
        grid.setRowStretch(ROWS_PER_COLUMN + 1, 1)  # 内容顶部对齐

    def to_list(self):
        return [{"hex": chk.isChecked(), "text": edit.text()}
                for chk, edit in self.entries]

    def load_list(self, items):
        if not isinstance(items, list):
            items = []
        for (chk, edit), item in zip(self.entries, items):
            if not isinstance(item, dict):
                item = {}
            chk.setChecked(bool(item.get("hex")))
            edit.setText(str(item.get("text", "")))


class MultiSendPage(QWidget):
    """send_func(text: str, is_hex: bool) 由主窗口提供，负责实际发送。

    标签栏最后固定一个 "+" 页签用于添加标签；右键页签弹出重命名/删除菜单。
    """

    def __init__(self, send_func, parent=None):
        super().__init__(parent)
        self._send_func = send_func
        self._cycle_index = 0
        self._prev_index = 0

        self.tag_tabs = QTabWidget()
        self.tag_tabs.tabBarClicked.connect(self._on_tab_clicked)
        self.tag_tabs.currentChanged.connect(self._on_current_changed)
        bar = self.tag_tabs.tabBar()
        bar.setContextMenuPolicy(Qt.CustomContextMenu)
        bar.customContextMenuRequested.connect(self._tab_context_menu)

        self.cycle_chk = QCheckBox("循环发送(当前标签)")
        self.cycle_chk.toggled.connect(self._toggle_cycle)
        self.period_spin = QSpinBox()
        self.period_spin.setRange(1, 600000)
        self.period_spin.setValue(1000)
        self.period_spin.setSuffix(" ms")

        bottom = QHBoxLayout()
        bottom.addWidget(self.cycle_chk)
        bottom.addWidget(QLabel("周期:"))
        bottom.addWidget(self.period_spin)
        bottom.addStretch()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 2)
        layout.setSpacing(3)
        layout.addWidget(self.tag_tabs)
        layout.addLayout(bottom)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._cycle_tick)

        self._loading = True
        self._load()
        self._loading = False

    # ---------- 标签管理 ----------

    def _plus_index(self) -> int:
        return self.tag_tabs.count() - 1

    def _is_plus(self, idx: int) -> bool:
        return idx == self._plus_index()

    def _on_tab_clicked(self, idx: int):
        if self._is_plus(idx):
            self.add_tag()

    def _on_current_changed(self, idx: int):
        # "+" 页签不可停留，弹回原页；原页已删除则弹回最后一个真实标签
        if self._is_plus(idx) and self.tag_tabs.count() > 1:
            target = self._prev_index
            if not 0 <= target < self._plus_index():
                target = self._plus_index() - 1
            self.tag_tabs.setCurrentIndex(target)
            return
        self._prev_index = idx
        self.stop_cycle()

    def _tab_context_menu(self, pos):
        bar = self.tag_tabs.tabBar()
        idx = bar.tabAt(pos)
        if idx < 0 or self._is_plus(idx):
            return
        menu = QMenu(self)
        rename_act = menu.addAction("重命名")
        delete_act = menu.addAction("删除标签")
        act = menu.exec(bar.mapToGlobal(pos))
        if act is rename_act:
            self.rename_tag(idx)
        elif act is delete_act:
            self.delete_tag(idx)

    def _unique_name(self, name: str, skip_idx: int = -1) -> bool:
        for i in range(self._plus_index()):
            if i != skip_idx and self.tag_tabs.tabText(i) == name:
                QMessageBox.warning(self, "提示", f"标签 {name} 已存在")
                return False
        return True

    def add_tag(self, name: str | None = None):
        if not name:
            name, ok = QInputDialog.getText(self, "添加标签", "标签名称:")
            if not ok or not name.strip():
                return
            name = name.strip()
        if not self._unique_name(name):
            return
        page = TagPage(self._send_entry, self.save)
        idx = self.tag_tabs.insertTab(self._plus_index(), page, name)
        self.tag_tabs.setCurrentIndex(idx)
        self.save()

    def rename_tag(self, idx: int):
        old = self.tag_tabs.tabText(idx)
        name, ok = QInputDialog.getText(self, "重命名标签", "标签名称:", text=old)
        if not ok or not name.strip() or name.strip() == old:
            return
        name = name.strip()
        if not self._unique_name(name, skip_idx=idx):
            return
        self.tag_tabs.setTabText(idx, name)
        self.save()

    def delete_tag(self, idx: int):
        if self.tag_tabs.count() <= 2:  # 一个标签 + "+"
            QMessageBox.warning(self, "提示", "至少保留一个标签")
            return
        name = self.tag_tabs.tabText(idx)
        if QMessageBox.question(self, "删除标签",
                                f"确认删除标签 {name} 及其全部命令？") != \
                QMessageBox.Yes:
            return
        self.tag_tabs.removeTab(idx)
        self.save()

    def _current_page(self) -> TagPage | None:
        w = self.tag_tabs.currentWidget()
        return w if isinstance(w, TagPage) else None

    # ---------- 持久化 ----------

    def _load(self):
        data = {}
        if CONFIG_PATH.exists():
            try:
                data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                data = {}
        if not data:
            data = {"默认": []}
        for name, items in data.items():
            page = TagPage(self._send_entry, self.save)
            page.load_list(items)
            self.tag_tabs.addTab(page, name)
        self.tag_tabs.addTab(QWidget(), "+")  # 固定在末尾的添加入口
        self.tag_tabs.setCurrentIndex(0)

    def save(self):
        if self._loading:
            return
        data = {self.tag_tabs.tabText(i): self.tag_tabs.widget(i).to_list()
                for i in range(self._plus_index())}
        try:
            CONFIG_PATH.write_text(
                json.dumps(data, ensure_ascii=False, indent=1),
                encoding="utf-8")
        except OSError:
            pass

    # ---------- 发送 ----------

    def _send_entry(self, idx) -> bool:
        page = self._current_page()
        if page is None:
            return False
        hex_chk, edit = page.entries[idx]
        text = edit.text()
        if not text:
            return False
        return self._send_func(text, hex_chk.isChecked())

    def _toggle_cycle(self, on: bool):
        if on:
            self._cycle_index = 0
            self._timer.start(self.period_spin.value())
        else:
            self._timer.stop()

    def _cycle_tick(self):
        self._timer.setInterval(self.period_spin.value())
        page = self._current_page()
        if page is None:
            self.cycle_chk.setChecked(False)
            return
        # 从当前位置往后找第一条非空条目发送
        for _ in range(ENTRIES_PER_PAGE):
            idx = self._cycle_index
            self._cycle_index = (self._cycle_index + 1) % ENTRIES_PER_PAGE
            if page.entries[idx][1].text():
                if not self._send_entry(idx):
                    self.cycle_chk.setChecked(False)
                return
        self.cycle_chk.setChecked(False)  # 全空则停止

    def stop_cycle(self):
        self.cycle_chk.setChecked(False)
