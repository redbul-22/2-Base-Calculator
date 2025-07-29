import sys
from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QMessageBox, QStyleFactory, QSizePolicy
)

class BinaryCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Binary Calculator")
        self.setFixedSize(360, 600)

        self.reset_state()
        self.current_theme = "dark"   # dark / light
        self.current_lang  = "EN"     # EN / JP

        self._init_ui()
        self.apply_theme()
        self.apply_language()

    def reset_state(self, keep_result=False):
        if keep_result:
            self.operand1 = self.last_result
        else:
            self.operand1 = ""
        self.operand2 = ""
        self.operator = None
        self.editing_second = False

    def _init_ui(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(12, 12, 12, 12)
        vbox.setSpacing(8)

        # header: theme & lang toggles
        header = QHBoxLayout()
        header.setSpacing(12)
        self.btn_theme = QPushButton("🌙")
        self.btn_lang  = QPushButton("EN")
        for btn in (self.btn_theme, self.btn_lang):
            btn.setFont(QFont("Helvetica Neue", 16))
            btn.setFixedSize(48, 48)
        self.btn_theme.clicked.connect(self.toggle_theme)
        self.btn_lang.clicked.connect(self.toggle_language)
        header.addWidget(self.btn_theme)
        header.addWidget(self.btn_lang)
        header.addStretch()
        vbox.addLayout(header)

        # display
        self.display = QLabel("0")
        self.display.setFont(QFont("Helvetica Neue", 40, QFont.Bold))
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setFixedHeight(100)
        self.display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        vbox.addWidget(self.display)

        # buttons grid
        grid = QGridLayout()
        grid.setSpacing(8)

        keys = [
            ("and",   "AND"), ("or","OR"), ("xor","XOR"), ("back","⌫"),
            ("add",   "+"),   ("subtract","-"), ("multiply","×"),("divide","÷"),
            ("0","0"), ("1","1"), ("equal","="), ("clear","C"),
        ]
        self.buttons = {}
        for idx, (key, _) in enumerate(keys):
            btn = QPushButton()
            btn.setFont(QFont("Helvetica Neue", 24))
            btn.setFixedSize(72, 72)
            btn.clicked.connect(partial(self.on_button, key))
            if key in ("0","1"):
                btn.setProperty("type", "digit")
            elif key in ("clear","back"):
                btn.setProperty("type", "func")
            else:
                btn.setProperty("type", "op")
            r, c = divmod(idx, 4)
            grid.addWidget(btn, r, c)
            self.buttons[key] = btn

        vbox.addLayout(grid)

        self.last_result = ""

    # theme
    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme=="dark" else "dark"
        self.apply_theme()

    def apply_theme(self):
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        pal = QPalette()

        if self.current_theme == "dark":
            bg_color = "#121212"
            text_color = "white"
            self.btn_theme.setText("☀")
            digit_bg = "#2D2D2D"
            func_bg  = "#374955"
            eq_bg    = "#004C69"
            clr_bg   = "#484264"
        else:
            bg_color = "#FFFFFF"
            text_color = "black"
            self.btn_theme.setText("🌙")
            digit_bg = "#E0E0E0"
            func_bg  = "#D2E5F4"
            eq_bg    = "#C2E8FF"
            clr_bg   = "#E5DEFF"

        pal.setColor(QPalette.Window,      QColor(bg_color))
        pal.setColor(QPalette.WindowText,  QColor(text_color))
        pal.setColor(QPalette.Base,        QColor(bg_color))
        pal.setColor(QPalette.Text,        QColor(text_color))
        QApplication.setPalette(pal)

        # display styling
        disp_bg = "#1F1F1F" if self.current_theme=="dark" else "#FFFFFF"
        self.display.setStyleSheet(f"""
            QLabel {{
                background: {disp_bg};
                color: {text_color};
                border-radius: 12px;
                padding-right: 16px;
            }}
        """)

        # button styling
        for key, btn in self.buttons.items():
            if key == "equal":
                bg = eq_bg
            elif key == "clear":
                bg = clr_bg
            elif btn.property("type") == "digit":
                bg = digit_bg
            else:
                bg = func_bg

            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: {text_color};
                    border-radius: 36px;
                }}
                QPushButton:pressed {{
                    background-color: {bg}CC;
                }}
            """)

    # language
    def toggle_language(self):
        self.current_lang = "JP" if self.current_lang=="EN" else "EN"
        self.apply_language()

    def apply_language(self):
        self.btn_lang.setText(self.current_lang)
        labels = {
            "EN": {"and":"AND","or":"OR","xor":"XOR","clear":"C",
                   "add":"+","subtract":"-","multiply":"×","divide":"÷",
                   "0":"0","1":"1","equal":"=","back":"⌫"},
            "JP": {"and":"AND","or":"OR","xor":"XOR","clear":"C",
                   "add":"＋","subtract":"－","multiply":"×","divide":"÷",
                   "0":"0","1":"1","equal":"＝","back":"⌫"},
        }
        for k, btn in self.buttons.items():
            btn.setText(labels[self.current_lang][k])

    # input / calc
    def on_button(self, key):
        if key == "clear":
            self.reset_state()
            self.display.setText("0")
            self.last_result = ""
            return

        if key == "back":
            tgt = "operand2" if self.editing_second else "operand1"
            s = getattr(self, tgt)[:-1]
            setattr(self, tgt, s)
            self.update_display()
            return

        if key == "equal":
            self.calculate()
            return

        if key in ("add","subtract","multiply","divide","and","or","xor"):
            if not self.operand1:
                if self.last_result:
                    self.operand1 = self.last_result
                else:
                    return
            # chaining: if result just shown, allow new operator for continued input
            if not self.editing_second and self.operator is None and self.last_result:
                self.operand1 = self.last_result
            self.operator = key
            self.editing_second = True
            self.operand2 = ""
            self.update_display()
            return

        if key in ("0","1"):
            # chaining: if previous result just shown and inputting digit, start new calculation
            if self.last_result and not self.editing_second and not self.operator and not self.operand1:
                self.reset_state()
                self.display.setText("0")
            if not self.editing_second:
                self.operand1 += key
            else:
                self.operand2 += key
            self.update_display()

    def update_display(self):
        if not self.operator:
            txt = self.operand1 or "0"
        else:
            sym = self.op_symbol()
            txt = f"{self.operand1} {sym} {self.operand2 or ''}"
        self.display.setText(txt)

    def op_symbol(self):
        return {
            "add":"+","subtract":"-","multiply":"×","divide":"÷",
            "and":"AND","or":"OR","xor":"XOR"
        }[self.operator]

    def calculate(self):
        if not (self.operand1 and self.operator and self.operand2):
            return
        try:
            x, y = int(self.operand1, 2), int(self.operand2, 2)
            if   self.operator == "add":      r = x + y
            elif self.operator == "subtract": r = x - y
            elif self.operator == "multiply": r = x * y
            elif self.operator == "divide":
                if y == 0:
                    raise ZeroDivisionError
                r = x // y
            elif self.operator == "and":      r = x & y
            elif self.operator == "or":       r = x | y
            elif self.operator == "xor":      r = x ^ y

            sign = "-" if r < 0 else ""
            res = bin(abs(r))[2:]
            result_str = sign + res
            self.display.setText(result_str)
            self.last_result = result_str
            self.reset_state(keep_result=True)

        except ZeroDivisionError:
            msg = {
                "EN": "Cannot divide by zero.",
                "JP": "ゼロで割ることはできません。"
            }[self.current_lang]
            QMessageBox.critical(self, "Error", msg, QMessageBox.Close)
            self.last_result = ""
            self.reset_state()

        except ValueError:
            msg = {
                "EN": "Invalid input.",
                "JP": "無効な入力です。"
            }[self.current_lang]
            QMessageBox.critical(self, "Error", msg, QMessageBox.Close)
            self.last_result = ""
            self.reset_state()

    def keyPressEvent(self, event):
        # Optional: keyboard shortcuts
        keymap = {
            Qt.Key_0: "0", Qt.Key_1: "1",
            Qt.Key_Plus: "add", Qt.Key_Minus: "subtract",
            Qt.Key_Asterisk: "multiply", Qt.Key_Slash: "divide",
            Qt.Key_Equal: "equal", Qt.Key_Return: "equal", Qt.Key_Enter: "equal",
            Qt.Key_Backspace: "back", Qt.Key_Delete: "clear",
        }
        if event.key() in keymap:
            self.on_button(keymap[event.key()])
        else:
            super().keyPressEvent(event)

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Helvetica Neue", 14))
    win = BinaryCalculator()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()