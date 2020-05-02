import copy
import os
import random
import re
from enum import Enum

class NoQuestionsLeft(Exception):
    pass


class NoQuestionsLoaded(Exception):
    pass


class CorruptedFile(Exception):
    pass


re_enter = re.compile(r" \([^)]+\)")


def filter_answer_part(s):
    s = re_enter.sub("", s)
    return s


def filter_question_part(s):
    return s.replace("|", r"\n")


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
        if hasattr(one, "decode"):
            one = one.decode("utf-8")
            two = two.decode("utf-8")
        if "left" in directions:
            self.dictionary.append((one, two, "left"))
        if "right" in directions:
            self.dictionary.append((two, one, "right"))


    def process_line_v1(self, line, directions):
        translation = line.split("|", 1)
        self.add_translation(translation[0], translation[1], directions)

    def process_direction(self, question, answer, direction):
        self.dictionary.append((filter_question_part(question),
                                filter_answer_part(answer),
                                direction))

    def process_line(self, line, directions):
        if "||" not in line:
            return self.process_line_v1(line, directions)

        native, foreign = line.split("||", 1)
        native = native.strip()
        foreign = foreign.strip()
        if "left" in directions:
            for n in native.split("|"):
                n = n.strip()
                self.dictionary.append((n, foreign, "left"))

        if "right" in directions:
            for n in foreign.split("|"):
                n = n.strip()
                self.dictionary.append((n, native, "left"))


    def load(self, path, filenames, directions):
        self.dictionary = []
        self.filenames = filenames
        self.directions = directions
        for fname in filenames:
            with open(os.path.join(path, os.path.basename(fname)), "r") as f:
                lines = f.read().splitlines()
                for n, line in enumerate(lines):
                    try:
                        self.process_line(line, directions)
                    except Exception as e:
                        m = (
                            "Corruption detected: %s on line %s: %s" %
                            (fname, n + 1, e))
                        raise CorruptedFile(m)
        self.reset()

    def check_answer(self, ans):
        if ans:
            possible_answers = [filter_answer_part(s).strip() for s in self.answer.split("|")]
            if ans.strip() in possible_answers:
                self.good += 1
                self.remaining.remove(self.selection)
                return True
            else:
                self.bad += 1
                return False

    def get_correct_answer(self):
        return self.answer.replace("|", ", ")

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
