from kivy.app import App
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

import dict_trainer
import time

EN_COLOR="#03fca9"
CZ_COLOR="#dd42eb"

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class Root(FloatLayout):
    loadfile = ObjectProperty(None)
    textbox = ObjectProperty(None)
    g_label = ObjectProperty(None)
    b_label = ObjectProperty(None)
    r_label = ObjectProperty(None)
    q_label = ObjectProperty(None)
    c_label = ObjectProperty(None)

    dt = dict_trainer.DictTrainer()

    direction = []

    def reset(self):
        self.dt.reset()
        self.generate_question()

    def dismiss_popup(self):
        self._popup.dismiss()

    def redraw(self):
        self.g_label.text = '[color=#00ff00]Správně:[/color] %d' % self.dt.good
        self.b_label.text = '[color=#ff0000]Špatně:[/color] %d' % self.dt.bad
        self.r_label.text = '[color=#0000ff]Zbývá:[/color] %d' % len(self.dt.remaining)
        if self.dt.in_progress:
            if self.dt.direction == "left":
                self.q_label.text = f"[color={EN_COLOR}]{self.dt.question}[/color]"
            else:
                self.q_label.text = f"[color={CZ_COLOR}]{self.dt.question}[/color]"
        else:
            self.q_label.text = self.dt.question

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Vybrat sadu...", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def set_direction(self, direction):
        self.direction = direction

    def load(self, path, filenames):
        self.dt.load(path, filenames, self.direction)
        self.dismiss_popup()
        self.reset()

    def generate_question(self):
        try:
            self.dt.generate_question()
        except dict_trainer.NoQuestionsLoaded:
            self.dt.question = "[color=#ffffff]Není nahrána žádná sada[/color]"
        except dict_trainer.NoQuestionsLeft:
            self.dt.question = "[color=#ffffff]Dokončil jsi sadu[/color]"
        self.redraw()

    def set_focus_to_textinput(self, _):
        self.textbox.focus = True

    def show_correct(self):
        self.c_label.text = f"Správná odpověď:\n[color=#ff0000]{self.dt.answer}[/color]"
        Clock.schedule_once(self.hide_correct, 2)

    def hide_correct(self, _):
        self.c_label.text = ""

    def check_answer(self):
        if not self.dt.in_progress:
            Clock.schedule_once(self.set_focus_to_textinput, 0.1)
            return
        if not self.dt.check_answer(self.textbox.text):
            self.show_correct()
        self.textbox.text = ""
        self.generate_question()
        Clock.schedule_once(self.set_focus_to_textinput, 0.1)


class DictTrainer(App):
    pass


Factory.register('Root', cls=Root)
Factory.register('LoadDialog', cls=LoadDialog)


if __name__ == '__main__':
    DictTrainer().run()
