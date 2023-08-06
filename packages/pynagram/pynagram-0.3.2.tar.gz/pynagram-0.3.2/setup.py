#! /usr/bin/python
# 
#     setup.py
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
from distutils.core import setup
import glob
r = setup(name= "pynagram",
        version= "0.3.2",
        description= "Pynagram - Unjumble the letters and get addicted!",
        author= "Umang",
        author_email= "umang.me@gmail.com",
        url= "https://launchpad.net/pynagram",
        packages= ["Pynagram", "Pynagram.gui", "Pynagram.backend"],
        scripts= ["pynagram"],
        data_files= [("share/pynagram/", glob.glob("wordlist/*"))],
        license="GPLv3",
        long_description="Pynagram = (Anagramarama - bugs) + simplicity. \n" + \
        "Pynagram is an easy to play anagram game!"
        )
