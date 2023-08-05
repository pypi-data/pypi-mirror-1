#!/usr/bin/env python
import random

class WordSource(object):
    # Empty for now.
    pass

class TestSource(WordSource):
    def __init__(self, sentence):
        super(TestSource, self).__init__()
        self.sentence = sentence

    def __call__(self):
        return self.sentence

class LinedFileSource(WordSource):
    def __init__(self, fn, max_chars=20):
        self.lines = []
        fp = file(fn, "r")
        try:
            for line in fp:
                if len(line) <= max_chars and line not in self.lines:
                    self.lines.append(line.rstrip("\r\n"))
        finally:
            fp.close()

    def __call__(self):
        return random.choice(self.lines)
