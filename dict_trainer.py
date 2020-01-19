import os
import random
import copy


class NoQuestionsLeft(Exception):
    pass


class NoQuestionsLoaded(Exception):
    pass


class DictTrainer():
    dictionary = []
    remaining = []
    in_progress = False
    question = ""
    answer = None

    good = 0
    bad = 0

    def reset(self):
        self.good = 0
        self.bad = 0
        self.remaining = copy.copy(self.dictionary)
        self.in_progress = True

    def add_translation(self, one, two, directions):
        if "left" in directions:
            self.dictionary.append((one, two, "left"))
        if "right" in directions:
            self.dictionary.append((two, one, "right"))

    def load(self, path, filenames, directions):
        self.dictionary = []
        self.filenames = filenames
        self.directions = directions
        for fname in filenames:
            with open(os.path.join(path, os.path.basename(fname)), "r") as f:
                lines = f.read().splitlines()
                for line in lines:
                    translation = line.split("|", 1)
                    self.add_translation(translation[0], translation[1],
                                         directions)
        self.reset()

    def check_answer(self, ans):
        if ans:
            if ans == self.answer:
                self.good += 1
                self.remaining.remove(self.selection)
                return True
            else:
                self.bad += 1
                return False

    def generate_question(self):
        if not self.dictionary:
            self.in_progress = False
            raise NoQuestionsLoaded()

        if self.remaining:
            self.selection = random.choice(self.remaining)
            self.question = self.selection[0]
            self.answer = self.selection[1]
            self.direction = self.selection[2]
        else:
            self.in_progress = False
            raise NoQuestionsLeft()
