#!/usr/bin/env python

import curses
import time

class UI(object):
    letter_correct = 1
    letter_incorrect = 2
    letter_outside = 3

    @classmethod
    def correct(cls, sentence, input_):
        r = []
        for i, c in enumerate(input_):
            s = cls.letter_correct
            if i > len(sentence) - 1:
                s = cls.letter_outside
            elif sentence[i] != c:
                s = cls.letter_incorrect
            r.append((c, s))
        return r

    get_time = time.time

class TerminalUI(UI):
    cpm_win_width = 20
    cpm_win_height = 5

    color_default = 0
    color_wrong = 1
    color_outside = 2
    color_letter_map = {UI.letter_correct: color_default,
        UI.letter_incorrect: color_wrong, UI.letter_outside: color_outside}

    def __init__(self):
        self.screen = self._init_screen()
        self.cpm_win = curses.newwin(self.cpm_win_height,
            self.cpm_win_width, 0,
            curses.COLS - self.cpm_win_width)
        self.sentence_display_win = curses.newwin(2,
            curses.COLS - self.cpm_win_width - 2, 0, 0)
        self.display_stats()

    def _display_sentence(self, sentence, refresh=False):
        self.sentence_display_win.clear()
        self.sentence_display_win.addstr(0, 0, sentence.encode("utf-8"))
        self.screen.move(1, 0)
        if refresh:
            self.sentence_display_win.refresh()

    def get_sentence(self, sentence):
        cinp = u""
        errors = 0
        start = last = None
        self._display_sentence(sentence, True)
        while True:
            c = chr(self.screen.getch())
            if c == "\n":
                # Wouldn't be very fair if you could type one letter and hit
                # Enter, now, would it?
                if cinp == sentence:
                    break
            elif c == "\x7f":
                cinp = cinp[:-1]
            else:
                # Only really start when we add to the input.
                if start is None:
                    start = self.get_time()
                last = self.get_time()
                while True:
                    try:
                        c = c.decode("utf-8")
                    except UnicodeDecodeError:
                        c += chr(self.screen.getch())
                    else:
                        break
                cinp += c
            self._display_sentence(sentence)
            i = 0
            for (letter, status) in self.correct(sentence, cinp):
                letter = letter.encode("utf-8")
                self.sentence_display_win.addstr(1, i, letter,
                        curses.color_pair(self.color_letter_map[status]))
                i += len(letter)
            if status != UI.letter_correct and letter.decode("utf-8") == c:
                errors += 1
            self.screen.move(1, len(cinp))
            self.sentence_display_win.refresh()
        return start, last, errors, cinp

    def display_stats(self, avg_cpm=0.0, tot_errors=0, last_cpm=0.0,
            last_errors=0):
        self.cpm_win.clear()
        self.cpm_win.addstr(0, 0, "| %.2f avg. CPM" % (avg_cpm,))
        self.cpm_win.addstr(1, 0, "| %.2f last CPM" % (last_cpm,))
        self.cpm_win.addstr(2, 0, "| %d total errors" % (tot_errors,))
        self.cpm_win.addstr(3, 0, "| %d last errors" % (last_errors,))
        self.cpm_win.addstr(4, 0, "+" + "-" * (self.cpm_win_width - 2))
        self.cpm_win.refresh()

    def _init_screen(self):
        s = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.init_pair(self.color_wrong,
            curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(self.color_outside,
            curses.COLOR_YELLOW, curses.COLOR_BLACK)
        s.clear()
        s.refresh()
        return s

    def _deinit_screen(self):
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    end = _deinit_screen
