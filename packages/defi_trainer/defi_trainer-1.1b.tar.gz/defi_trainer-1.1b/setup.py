"""
Copyright 2008,2009 Steven Mohr

This file is part of DefiTrainer.

    DefiTrainer is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    DefiTrainer is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with DefiTrainer.  If not, see <http://www.gnu.org/licenses/>.
 
"""

from setuptools import setup, find_packages
setup(
    name = "defi_trainer",
    version = "1.1b",
    packages = find_packages(),
    install_requires = ['docutils>=0.3'],
    author = "Steven Mohr",
    author_email = "steven@stevenmohr.de",
    description = "DefiTrainer is a light-weight definition and fact trainer",
    license = "GPL v3",
    keywords = "learning studies school trainer",
    url = "http://blog.stevenmohr.de/projects/defitrainer/",
    long_description = "DefiTrainer is a light-weight definition trainer."\
    " I created it to learn definitions and facts for university. "\
    "DefiTrainer parses RestructuredText and asks for definition based"\
    "on definiitons and low-level section elements.\n"\
    "My intention was to reuse my notes which I usually write in RST."\
    "  I didn't want to create a second file which can be used by a "\
    "training program.", 
    entry_points = {
        'gui_scripts': [
            'defi_trainer = defi_trainer:start',
        ]
    }

)

