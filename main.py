import base64
import re
from turtledemo.penrose import start
import json

from kivy.properties import ObjectProperty
from kivy.config import Config


Config.set('graphics', 'resizable', "0")
Config.set('graphics', 'width', '640')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'fullsscreen', '0')
Config.write()


from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.theming import ThemeManager


class CustomTextField(MDTextField):
    key_pattern = re.compile(r"ss://[\w=]+@((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}:\d{4,5}[\w\/#\?=%.]+")

    def set_text(self, instance_text_field, text: str) -> None:
        super().set_text(instance_text_field, text)
        if not self.key_pattern.match(text):
            self.error = True

    def text_is_valid(self) -> bool:
        if not self.key_pattern.match(self.text):
            self.error = True
        return not self.error


class Container(MDScreen):
    input_field = ObjectProperty()
    output_field = ObjectProperty()
    save_to_file_button = ObjectProperty()

    @staticmethod
    def convert_to_dict(key: str) -> dict:
        base64code, server_info = key.split("@")
        base64code = base64code.replace("ss://", "")
        server_info = re.search(r"((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}:\d{4,5}", server_info).group()
        decoded = base64.b64decode(base64code).decode("utf-8")
        method, password = decoded.split(":")
        server_ip, server_port = server_info.split(":")
        converted_data = {
            "server": server_ip,
            "server_port": int(server_port),
            "local_port": 1080,
            "password": password,
            "method": method
        }
        return converted_data

    def run_json_converter(self) -> None:
        if not self.input_field.text_is_valid():
            self.output_field.text = "Invalid input"
            self.output_field.error = True
            return
        print(self.input_field.text)
        converted_data = self.convert_to_dict(self.input_field.text)
        self.output_field.set_text(self.output_field, json.dumps(converted_data, indent=4))
        self.save_to_file_button.disabled = False


    def save_json_to_file(self):
        print("Save to file: ", self.input_field.text.lower())


class MainApp(MDApp):
    title = 'Outline Key Converter'
    theme_cls = ThemeManager()
    theme_cls.primary_palette = "Teal"


    def build(self):
        return Container()


if __name__ == '__main__':
    MainApp().run()
