#!/usr/bin/env python
#
#     gui.py
#
#     Copyright (c) 2009 Umang <umang.me@gmail.com>. All rights reserved.
#
#     This file is part of Pynagram
#
#     Pynagram is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Pynagram is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Pynagram. If not, see <http://www.gnu.org/licenses/>.
#

from PyQt4 import QtCore, QtGui
from qt_struct import Ui_MainWindow
from qt_about import Ui_About

import random
import time


from Pynagram.backend import anagram

class About(QtGui.QDialog):
    """This class is the About Dialog"""
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_About()
        self.ui.setupUi(self)
    def start(self):
        self.show()

class App(QtGui.QMainWindow):
    """This class handles the GUI."""

    def __init__(self, parent=None):
        """Initializes the code for the GUI"""
        # @type self.pynagram Anagram
        self.pynagram = anagram.Anagram()
        self.typed = []
        self.available_letters = []
        self.widgets = {}
        self.last_word = ""
        self.last_word_color = "000"
        self.solved = False
        self.time_started = 0
        self.time_elapsed = 0
        self.timer = QtCore.QTimer()
        #
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #
        QtCore.QObject.connect(self.ui.actionSolve, QtCore.SIGNAL("activated()"), self.actionSolve_activate)
        QtCore.QObject.connect(self.ui.actionNew, QtCore.SIGNAL("activated()"), self.actionNew_activate)
        QtCore.QObject.connect(self.ui.actionAbout, QtCore.SIGNAL("activated()"), self.actionAbout_activate)
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.__update_status_bar)
        self.timer.start(1000)

    def init_game(self):
        """Initializes a game."""
        self.pynagram.start_new()
        self.available_letters = self.pynagram.letters[:]
        self.last_word = ""
        self.typed = []
        self.show()
        self.time_started = time.time()
        self.__reflect_letters()
        self.__update_words()

    def __reflect_letters(self):
        """Updates the labels in the GUI

        to reflect the state of the variables in this class."""
        self.ui.l_avail.setText(" ".join(self.available_letters))
        self.ui.l_typed.setText(" ".join(self.typed))
        self.ui.l_last.setText(("Last word: <b><font color=\"#%s\">" + \
        "%s</font></b>") % (self.last_word_color, self.last_word))

    def __update_words(self):
        """Updates the list of words in the Pynagram window"""
        a_words = self.pynagram.words.keys()
        a_words.sort()
        a_words.sort(lambda x, y: len(x) - len(y))
        if not False in self.pynagram.words.values():
            self.solved = True
        per_column = len(a_words)/5 + 1
        for x in xrange(0, 5):
            words = [((self.pynagram.words[word] or self.solved) and  word) \
                or "_ " * len(word) for word in \
                        a_words[x*per_column:(x+1)*per_column]]
            getattr(self.ui, "l_solved_" + str(x+1)).setText(\
                "<br>".join([(word in self.pynagram.words and \
                self.pynagram.words[word] and self.solved and \
                (" <b>%s</b>"%word)) or word for \
                word in words]))
        self.__update_status_bar()

    def __update_status_bar(self):
        s_time = ""
        if not (self.solved or self.pynagram.solved_all):
            self.time_elapsed = int(time.time() - self.time_started)
        if self.time_elapsed >= 300 and not self.solved:
            self.solved = True
            self.actionSolve_activate()
        s_time = "Time: %s" % (time.strftime("%M:%S", \
                            time.gmtime(300 - self.time_elapsed)))
        s_score = "Score: %d" % self.pynagram.score
        self.ui.statusbar.showMessage(s_score + "\t" + s_time)
        self.resize(self.sizeHint())

    def actionNew_activate(self):
        self.solved = False
        if not self.pynagram.qualified:
            self.pynagram.clear_all()
        self.init_game()

    def actionAbout_activate(self):
        w_about = About()
        w_about.exec_()

    def actionSolve_activate(self):
        self.available_letters.extend(self.typed)
        self.typed = []
        self.__update_status_bar()
        self.solved = True
        self.__reflect_letters()
        self.__update_words()
        
    
    def keyPressEvent(self, event):
        if not self.solved:
            key = int(event.key())
            if 64 < key < 123 and chr(key).lower() in self.available_letters:
                # If an available letter has been typed
                letter = chr(key).lower()
                self.typed.append(letter)
                self.available_letters.remove(letter)
            elif key == 16777216:
                # Escape
                self.available_letters.extend(self.typed)
                self.typed = []
            elif key == 16777219 and len(self.typed) > 0:
                # Backspace
                self.available_letters.append(self.typed.pop())
            elif key == 32:
                # Spacebar
                random.shuffle(self.available_letters)
            elif key == 16777221 or key == 16777220:
                # Enter
                word = "".join(self.typed)
                result, already_typed = self.pynagram.guess(word)
                if already_typed:
                    self.last_word_color = "ff0"
                elif (not already_typed) and result:
                    self.last_word_color = "0f0"
                else:
                    self.last_word_color = "f00"
                self.last_word = word
                self.available_letters.extend(self.typed)
                self.typed = []
                self.__update_words()
            self.__reflect_letters()
