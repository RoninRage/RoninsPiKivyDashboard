import os
import sys
import shutil
import tarfile
import tempfile
import requests

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout

from update_check import is_update_available
from updater import download_and_apply_update


class RoninsDashboard(TabbedPanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_default_tab = False

        # Welcome Tab
        self.tab1 = TabbedPanelItem(text="Welcome")
        self.message_label = Label(
            text="Hello World from RoninsPiKivyDashboard!", font_size=20
        )
        self.tab1.add_widget(self.message_label)
        self.add_widget(self.tab1)

        # Touch Tab
        tab2 = TabbedPanelItem(text="Touch")
        btn = Button(text="Touch Me", font_size=20)
        btn.bind(on_press=self.on_button_press)
        tab2.add_widget(btn)
        self.add_widget(tab2)

        # Update check on start
        self.check_for_updates()

    def on_button_press(self, instance):
        instance.text = "Touched!"

    def check_for_updates(self):
        update_available, new_version, url = is_update_available()
        if update_available:
            self.message_label.text += f"\n\n🔔 Update available: v{new_version}"
            self.show_update_popup(new_version, url)

    def show_update_popup(self, version, url):
        box = BoxLayout(orientation="vertical", spacing=10, padding=10)
        info = Label(
            text=f"Version {version} is available.\nDo you want to download and restart?",
            font_size=16,
        )
        btn_download = Button(text="Download & Restart", size_hint_y=None, height=40)
        btn_skip = Button(text="Skip", size_hint_y=None, height=40)

        box.add_widget(info)
        box.add_widget(btn_download)
        box.add_widget(btn_skip)

        popup = Popup(title="Update Available", content=box, size_hint=(0.8, 0.5))

        def update_status(self, message):
            self.message_label.text += f"\n{message}"

        def on_download(instance):
            popup.dismiss()
            download_and_apply_update(url, status_callback=self.update_status)

        def on_skip(instance):
            popup.dismiss()

        btn_download.bind(on_press=on_download)
        btn_skip.bind(on_press=on_skip)

        popup.open()

    def download_and_apply_update(self, url):
        try:
            self.message_label.text += "\n\n⬇ Downloading update..."
            temp_dir = tempfile.mkdtemp()
            archive_path = os.path.join(temp_dir, "update.tar.gz")

            with requests.get(url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(archive_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(temp_dir)

            extracted_root = os.path.join(temp_dir, os.listdir(temp_dir)[0])
            current_dir = os.path.dirname(os.path.abspath(__file__))

            for item in os.listdir(extracted_root):
                src = os.path.join(extracted_root, item)
                dst = os.path.join(current_dir, item)
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)

            self.message_label.text += "\n✅ Update applied. Restarting..."
            App.get_running_app().stop()
            os.execv(sys.executable, [sys.executable] + sys.argv)

        except Exception as e:
            self.message_label.text += f"\n❌ Update failed: {e}"


class RoninsApp(App):
    def build(self):
        return RoninsDashboard()


if __name__ == "__main__":
    RoninsApp().run()
