import base64
import json
import re
from pathlib import Path

from kivy.config import Config
from kivy.properties import ObjectProperty

Config.set("graphics", "resizable", "0")
Config.set("graphics", "width", "640")
Config.set("graphics", "height", "480")
Config.set("graphics", "fullsscreen", "0")
Config.write()


from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from plyer import filechooser


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
    exit_manager = ObjectProperty()
    select_path = ObjectProperty()
    dialog = None

    def _close_dialog(self, obj) -> None:
        self.dialog.dismiss()
        del self.dialog

    def show_alert_dialog(self, text: str):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Alert",
                buttons=[MDFillRoundFlatButton(text="OK", on_release=self._close_dialog), ],
                text=text,
            )
        self.dialog.open()

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
            "method": method,
        }
        return converted_data

    def run_json_converter(self) -> None:
        if not self.input_field.text_is_valid():
            self.output_field.text = "Invalid input"
            self.output_field.error = True
            return

        converted_data = self.convert_to_dict(self.input_field.text)
        self.output_field.set_text(self.output_field, json.dumps(converted_data, indent=4))
        self.save_to_file_button.disabled = False

    def save_json_to_file(self):
        try:
            path = filechooser.choose_dir(title="Save JSON", multiple=False)
            if path:
                file_name = "server_info.json"
                file_path = Path(path[0]).joinpath(file_name)
                with open(file_path, "w") as file:
                    file.write(self.output_field.text)
                message = "Saved to %s" % file_path
            else:
                message = "No path selected! (Make sure that Cyrillic characters are not present in the path.)"
        except UnicodeDecodeError:
            message = "Error saving (Make sure that Cyrillic characters are not present in the path.)"
        except Exception as e:
            message = "Unknown error (%s)" % e

        self.show_alert_dialog(message)


class MainApp(MDApp):
    title = "Outline Key Converter"
    theme_cls = ThemeManager()
    theme_cls.primary_palette = "Teal"

    def build(self):
        return Container()


if __name__ == "__main__":
    MainApp().run()
