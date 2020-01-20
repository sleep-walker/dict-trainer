# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

import dict_trainer

EN_COLOR = "#03fca9"
CZ_COLOR = "#dd42eb"
WRONG_DELAY = 4


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
        self.textbox.text = ""
        self.generate_question()
        Clock.schedule_once(self.set_focus_to_textinput, 0.1)

    def dismiss_popup(self):
        self._popup.dismiss()

    def redraw(self):
        self.g_label.text = '[color=#00ff00]Správně:[/color] %d' % self.dt.good
        self.b_label.text = '[color=#ff0000]Špatně:[/color] %d' % self.dt.bad
        self.r_label.text = '[color=#0000ff]Zbývá:[/color] %d' % len(self.dt.remaining)
        if self.dt.in_progress:
            if self.dt.direction == "left":
                self.q_label.text = "[color=%s]%s[/color]" % (
                    EN_COLOR, self.dt.question)
            else:
                self.q_label.text = "[color=%s]%s[/color]" % (
                    CZ_COLOR, self.dt.question)
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
            self.log_activity()
        self.redraw()

    def set_focus_to_textinput(self, _):
        self.textbox.focus = True

    def show_correct(self):
        self.c_label.text = ("Správná odpověď:\n"
                             "[color=#ff0000]%s[/color]") % self.dt.answer
        Clock.schedule_once(self.hide_correct, WRONG_DELAY)

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

    def log_activity(self):
        with open("finished.log", "a") as f:
            f.write("----Finished run----\n"
                    "filenames: %s\n"
                    "direction: %s\n"
                    "good: %s\n"
                    "bad: %s\n"
            ) % (self.dt.filenames, self.dt.directions, self.dt.good, self.dt.bad)


class DictTrainer(App):
    pass


Factory.register('Root', cls=Root)
Factory.register('LoadDialog', cls=LoadDialog)


if __name__ == '__main__':
    DictTrainer().run()