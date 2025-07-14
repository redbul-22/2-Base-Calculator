import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

kivy.require('2.0.0')


class BinaryInput(TextInput):
    '''0/1 以外の文字を自動で除去するTextInput'''
    def insert_text(self, substring, from_undo=False):
        filtered = ''.join(c for c in substring if c in '01')
        return super().insert_text(filtered, from_undo=from_undo)


class BinaryCalculatorApp(App):
    def build(self):
        self.title = "Binary Calculator"

        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 入力欄
        self.entry1 = BinaryInput(
            hint_text='1 (binary)', multiline=False, font_size=24
        )
        self.entry2 = BinaryInput(
            hint_text='2 (binary)', multiline=False, font_size=24
        )

        # 結果表示ラベル
        self.result_label = Label(text='= ', font_size=28, size_hint=(1, 0.4))

        # ボタン配置(GridLayout4列)
        ops_layout = GridLayout(cols=4, spacing=5, size_hint=(1, 0.6))
        buttons = [
            ('add', 'add'),
            ('subtract', 'subtract'),
            ('multiply', 'multiply'),
            ('divide', 'divide'),
            ('AND', 'and'),
            ('OR', 'or'),
            ('XOR', 'xor'),
            ('Clear', 'clear'),
        ]
        for label, op in buttons:
            btn = Button(text=label, font_size=20)
            btn.bind(on_press=lambda inst, operation=op: self.on_button(operation))
            ops_layout.add_widget(btn)

        # ウィジェットを配置
        root.add_widget(self.entry1)
        root.add_widget(self.entry2)
        root.add_widget(ops_layout)
        root.add_widget(self.result_label)

        return root

    def on_button(self, operation):
        if operation == 'clear':
            self.entry1.text = ''
            self.entry2.text = ''
            self.result_label.text = '= '
            return

        a_text = self.entry1.text.strip()
        b_text = self.entry2.text.strip()

        # 空欄チェック
        if not a_text or not b_text:
            return self.show_error("0or1")

        try:
            a = int(a_text, 2)
            b = int(b_text, 2)

            if operation == 'add':
                res = a + b
            elif operation == 'subtract':
                res = a - b
            elif operation == 'multiply':
                res = a * b
            elif operation == 'divide':
                if b == 0:
                    raise ZeroDivisionError
                res = a // b
            elif operation == 'and':
                res = a & b
            elif operation == 'or':
                res = a | b
            elif operation == 'xor':
                res = a ^ b

            # 負数対応: '-' を付与してから2進文字列化
            sign = '-' if res < 0 else ''
            bin_str = bin(abs(res))[2:]
            self.result_label.text = f"= {sign}{bin_str}"

        except ZeroDivisionError:
            self.show_error("Error.2")
        except ValueError:
            # int(..,2) の失敗もキャッチ
            self.show_error("Error.1")

    def show_error(self, message):
        popup = Popup(
            title='Error.3',
            content=Label(text=message),
            size_hint=(0.6, 0.4)
        )
        popup.open()


if __name__ == '__main__':
    BinaryCalculatorApp().run()