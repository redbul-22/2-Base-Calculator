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
        self.setFixedSize(1280, 815)

        self.reset_state()
        self.current_theme = "dark"   # dark / light
        self.current_lang  = "EN"     # EN / JP

        self._init_ui()
        self.apply_theme()
        self.apply_language()

    def reset_state(self, keep_result=False):
        if keep_result:
            self.current_value = self.last_result
            self.expression = self.last_result
        else:
            self.current_value = ""
            self.expression = ""
        self.operator = None
        self.waiting_for_operand = False
        self.last_result = ""

    def _init_ui(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(40, 40, 40, 40)
        vbox.setSpacing(20)

        # header: theme & lang toggles
        header = QHBoxLayout()
        header.setSpacing(20)
        self.btn_theme = QPushButton("🌙")
        self.btn_lang  = QPushButton("EN")
        for btn in (self.btn_theme, self.btn_lang):
            btn.setFont(QFont("Helvetica Neue", 24, QFont.Bold))
            btn.setFixedSize(80, 80)
        self.btn_theme.clicked.connect(self.toggle_theme)
        self.btn_lang.clicked.connect(self.toggle_language)
        header.addWidget(self.btn_theme)
        header.addWidget(self.btn_lang)
        header.addStretch()
        vbox.addLayout(header)

        # expression display (shows full expression)
        self.expression_display = QLabel("")
        self.expression_display.setFont(QFont("Helvetica Neue", 26, QFont.Medium))
        self.expression_display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.expression_display.setFixedHeight(55)
        self.expression_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        vbox.addWidget(self.expression_display)

        # main display (shows current input/result)
        self.display = QLabel("0")
        self.display.setFont(QFont("Helvetica Neue", 76, QFont.Bold))
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setFixedHeight(170)
        self.display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        vbox.addWidget(self.display)

        # buttons grid
        grid = QGridLayout()
        grid.setHorizontalSpacing(15)
        grid.setVerticalSpacing(60)

        keys = [
            ("and",   "AND"), ("or","OR"), ("xor","XOR"), ("back","⌫"),
            ("add",   "+"),   ("subtract","-"), ("multiply","×"),("divide","÷"),
            ("0","0"), ("1","1"), ("equal","="), ("clear","C"),
        ]
        self.buttons = {}
        for idx, (key, _) in enumerate(keys):
            btn = QPushButton()
            btn.setFont(QFont("Helvetica Neue", 36, QFont.Bold))
            btn.setFixedSize(200, 120)
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

    # theme
    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme=="dark" else "dark"
        self.apply_theme()

    def apply_theme(self):
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        pal = QPalette()

        if self.current_theme == "dark":
            # ダークテーマの最適化
            bg_color = "#0D1117"        # GitHub風の深い背景
            text_color = "#F0F6FC"      # より鮮明な白
            self.btn_theme.setText("☀️")
            
            # 元の色設定を維持
            digit_bg = "#2D2D2D"
            func_bg  = "#374955"
            eq_bg    = "#004C69"
            clr_bg   = "#484264"
            
            # ディスプレイ背景の最適化
            disp_bg = "#161B22"
            expr_bg = "#0D1117"
            
        else:
            # ライトテーマの最適化
            bg_color = "#FFFFFF"
            text_color = "#1F2328"      # より読みやすい濃い色
            self.btn_theme.setText("🌙")
            
            # 元の色設定を維持
            digit_bg = "#E0E0E0"
            func_bg  = "#D2E5F4"
            eq_bg    = "#C2E8FF"
            clr_bg   = "#E5DEFF"
            
            # ディスプレイ背景の最適化
            disp_bg = "#F6F8FA"
            expr_bg = "#FFFFFF"

        pal.setColor(QPalette.Window,      QColor(bg_color))
        pal.setColor(QPalette.WindowText,  QColor(text_color))
        pal.setColor(QPalette.Base,        QColor(bg_color))
        pal.setColor(QPalette.Text,        QColor(text_color))
        QApplication.setPalette(pal)

        # ヘッダーボタンのスタイリング改善
        for header_btn in (self.btn_theme, self.btn_lang):
            header_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {func_bg};
                    color: {text_color};
                    border-radius: 40px;
                    border: 2px solid {"#30363D" if self.current_theme == "dark" else "#D8DEE4"};
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {"#30363D" if self.current_theme == "dark" else "#C7CED6"};
                    border: 2px solid {"#58A6FF" if self.current_theme == "dark" else "#0969DA"};
                    transform: scale(1.05);
                }}
                QPushButton:pressed {{
                    transform: scale(0.95);
                    background-color: {"#21262D" if self.current_theme == "dark" else "#B1B9C1"};
                }}
            """)

        # メインディスプレイのスタイリング改善
        self.display.setStyleSheet(f"""
            QLabel {{
                background: {disp_bg};
                color: {text_color};
                border-radius: 25px;
                padding-right: 35px;
                border: 3px solid {"#30363D" if self.current_theme == "dark" else "#D8DEE4"};
                font-weight: bold;
            }}
        """)

        # 式表示のスタイリング改善
        expr_color = "#8B949E" if self.current_theme == "dark" else "#656D76"
        self.expression_display.setStyleSheet(f"""
            QLabel {{
                background: {expr_bg};
                color: {expr_color};
                border-radius: 15px;
                padding-right: 25px;
                border: 2px solid {"#21262D" if self.current_theme == "dark" else "#E1E7ED"};
                font-weight: 500;
            }}
        """)

        # 元のボタン色設定を維持したスタイリング
        for key, btn in self.buttons.items():
            if key == "equal":
                bg = eq_bg
            elif key == "clear":
                bg = clr_bg
            elif btn.property("type") == "digit":
                bg = digit_bg
            else:
                bg = func_bg

            # ホバーとプレス効果を追加
            hover_opacity = "CC" if self.current_theme == "dark" else "DD"
            pressed_opacity = "AA" if self.current_theme == "dark" else "BB"

            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: {text_color};
                    border-radius: 60px;
                    border: 2px solid {"#30363D" if self.current_theme == "dark" else "#D8DEE4"};
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {bg}{hover_opacity};
                    border: 2px solid {"#58A6FF" if self.current_theme == "dark" else "#0969DA"};
                    transform: scale(1.02);
                }}
                QPushButton:pressed {{
                    background-color: {bg}{pressed_opacity};
                    transform: scale(0.98);
                    border: 2px solid {"#F0F6FC" if self.current_theme == "dark" else "#1F2328"};
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
            self.expression_display.setText("")
            return

        if key == "back":
            if self.waiting_for_operand:
                # Remove last operator from expression
                if self.expression and self.expression.split():
                    parts = self.expression.split()
                    if len(parts) >= 2:
                        self.expression = " ".join(parts[:-1])
                        self.expression_display.setText(self.expression)
                    self.operator = None
                    self.waiting_for_operand = False
            else:
                # Remove last digit from current input
                current_text = self.display.text()
                if current_text and current_text != "0":
                    new_text = current_text[:-1]
                    if not new_text:
                        new_text = "0"
                    self.display.setText(new_text)
                    self.current_value = new_text if new_text != "0" else ""
            return

        if key == "equal":
            self.calculate_final()
            return

        if key in ("add","subtract","multiply","divide","and","or","xor"):
            if self.waiting_for_operand:
                # Replace the last operator
                if self.expression and self.expression.split():
                    parts = self.expression.split()
                    if len(parts) >= 2:
                        parts[-1] = self.op_symbol(key)
                        self.expression = " ".join(parts)
                        self.expression_display.setText(self.expression)
                self.operator = key
                return
            
            # If we have a current value, calculate intermediate result
            if self.operator and self.current_value and self.expression:
                self.calculate_intermediate()
            
            # Add current value to expression if not already there
            if self.current_value:
                if self.expression:
                    self.expression += f" {self.op_symbol(key)}"
                else:
                    self.expression = f"{self.current_value} {self.op_symbol(key)}"
            elif self.last_result:
                # Use last result if no current value
                self.expression = f"{self.last_result} {self.op_symbol(key)}"
                self.current_value = self.last_result
            else:
                return
            
            self.operator = key
            self.waiting_for_operand = True
            self.expression_display.setText(self.expression)
            return

        if key in ("0","1"):
            if self.waiting_for_operand:
                # Start new operand
                self.current_value = key
                self.waiting_for_operand = False
            else:
                # Continue building current operand
                if self.current_value == "0" or not self.current_value:
                    self.current_value = key
                else:
                    self.current_value += key
            
            self.display.setText(self.current_value)

    def calculate_intermediate(self):
        """Calculate intermediate result for continuous operations"""
        if not (self.operator and self.current_value and self.expression):
            return
        
        try:
            # Extract the last operand from expression
            parts = self.expression.split()
            if len(parts) >= 1:
                operand1 = parts[0]
                x = int(operand1, 2)
                y = int(self.current_value, 2)
                
                result = self.perform_operation(x, y, self.operator)
                result_str = self.format_result(result)
                
                # Update expression with the intermediate result
                self.expression = result_str
                self.current_value = result_str
                self.display.setText(result_str)
                
        except (ValueError, ZeroDivisionError):
            pass  # Skip intermediate calculation on error

    def calculate_final(self):
        """Calculate final result and display it"""
        if not self.expression:
            return
        
        try:
            # If we're waiting for operand, remove the trailing operator
            if self.waiting_for_operand:
                parts = self.expression.split()
                if len(parts) >= 2:
                    self.expression = parts[0]
                    self.current_value = parts[0]
            elif self.operator and self.current_value:
                # Add the current operand to complete the expression
                self.expression += f" {self.current_value}"
            
            # Parse and calculate the full expression
            result_str = self.evaluate_expression(self.expression)
            
            self.display.setText(result_str)
            self.expression_display.setText(f"{self.expression} =")
            self.last_result = result_str
            self.reset_state(keep_result=True)
            
        except (ValueError, ZeroDivisionError) as e:
            self.show_error(str(e))

    def evaluate_expression(self, expression):
        """Evaluate a binary expression string"""
        parts = expression.split()
        if len(parts) == 1:
            return parts[0]
        
        # Process left to right (no operator precedence for simplicity)
        result = int(parts[0], 2)
        
        i = 1
        while i < len(parts) - 1:
            operator = parts[i]
            operand = int(parts[i + 1], 2)
            
            if operator in ("+", "＋"):
                result = result + operand
            elif operator in ("-", "－"):
                result = result - operand
            elif operator == "×":
                result = result * operand
            elif operator == "÷":
                if operand == 0:
                    raise ZeroDivisionError
                result = result // operand
            elif operator == "AND":
                result = result & operand
            elif operator == "OR":
                result = result | operand
            elif operator == "XOR":
                result = result ^ operand
            
            i += 2
        
        return self.format_result(result)

    def perform_operation(self, x, y, operator):
        """Perform a single operation"""
        if operator == "add":
            return x + y
        elif operator == "subtract":
            return x - y
        elif operator == "multiply":
            return x * y
        elif operator == "divide":
            if y == 0:
                raise ZeroDivisionError
            return x // y
        elif operator == "and":
            return x & y
        elif operator == "or":
            return x | y
        elif operator == "xor":
            return x ^ y

    def format_result(self, result):
        """Format integer result as binary string"""
        sign = "-" if result < 0 else ""
        return sign + bin(abs(result))[2:]

    def op_symbol(self, operator=None):
        """Get display symbol for operator"""
        op = operator or self.operator
        symbols = {
            "add": "+" if self.current_lang == "EN" else "＋",
            "subtract": "-" if self.current_lang == "EN" else "－",
            "multiply": "×",
            "divide": "÷",
            "and": "AND",
            "or": "OR",
            "xor": "XOR"
        }
        return symbols.get(op, "")

    def show_error(self, error_type):
        """Show error message"""
        if "ZeroDivisionError" in error_type:
            msg = {
                "EN": "Cannot divide by zero.",
                "JP": "ゼロで割ることはできません。"
            }[self.current_lang]
        else:
            msg = {
                "EN": "Invalid input.",
                "JP": "無効な入力です。"
            }[self.current_lang]
        
        QMessageBox.critical(self, "Error", msg, QMessageBox.Close)
        self.reset_state()
        self.display.setText("0")
        self.expression_display.setText("")

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