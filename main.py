import os
import sys
import requests
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock

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
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=0.1)
        self.progress_bar.opacity = 0  # initial versteckt
        box = BoxLayout(orientation="vertical")
        box.add_widget(self.message_label)
        box.add_widget(self.progress_bar)
        self.tab1.add_widget(box)
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

    def update_status(self, text=None, progress=None):
        def update(dt):
            if text:
                self.message_label.text += f"\n{text}"
            if progress is not None:
                self.progress_bar.opacity = 1 if progress < 100 else 0
                self.progress_bar.value = progress

        Clock.schedule_once(update)

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

        def on_download(instance):
            popup.dismiss()
            download_and_apply_update(url, status_callback=self.update_status)

        def on_skip(instance):
            popup.dismiss()

        btn_download.bind(on_press=on_download)
        btn_skip.bind(on_press=on_skip)

        popup.open()


class RoninsApp(App):
    def build(self):
        return RoninsDashboard()


if __name__ == "__main__":
    RoninsApp().run()
