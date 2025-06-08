from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.label import Label
from kivy.uix.button import Button


class RoninsDashboard(TabbedPanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_default_tab = False

        # Tab 1: Hello World
        tab1 = TabbedPanelItem(text='Welcome')
        tab1.add_widget(Label(text='Hello World from RoninsPiKivyDashboard!', font_size=24))
        self.add_widget(tab1)

        # Tab 2: Button test
        tab2 = TabbedPanelItem(text='Touch')
        btn = Button(text='Touch Me', font_size=20)
        btn.bind(on_press=self.on_button_press)
        tab2.add_widget(btn)
        self.add_widget(tab2)

    def on_button_press(self, instance):
        instance.text = "Touched!"


class RoninsApp(App):
    def build(self):
        return RoninsDashboard()


if __name__ == '__main__':
    RoninsApp().run()
