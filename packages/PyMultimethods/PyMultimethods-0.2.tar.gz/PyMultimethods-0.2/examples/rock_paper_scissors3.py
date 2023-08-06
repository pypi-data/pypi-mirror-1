# Copyright 2007, 2008 Nathan Davis

# Rock, Paper, Scissors, Part III
# See http://pymultimethods.wiki.sourceforge.net/Rock+Paper+Scissors3 for details

# This file is part of PyMultimethods
#
# PyMultimethods is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyMultimethods is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PyMultimethods.  If not, see <http://www.gnu.org/licenses/>.

from rock_paper_scissors2 import *

class BombTech(object): pass

@rock_paper_scissors.extend(BombTech, Dynamite)
def rock_paper_scissors(player1, player2):
    print "Player1 successfully disarms the bomb"
    print "Player1 wins"

@rock_paper_scissors.extend(Dynamite, BombTech)
def rock_paper_scissors(player1, player2):
    print "Player2 successfully disarms the bomb"
    print "Player2 wins"

@rock_paper_scissors.extend(BombTech, anything)
@rock_paper_scissors.extend(anything, BombTech)
def rock_paper_scissors(player1, player2):
    print "The bomb tech is mysteriously murdered."
    print "Both players are accused with murder and go bankrupt attempting to clear themselves."

@rock_paper_scissors.extend(BombTech, BombTech)
def rock_paper_scissors_game(player1, player2):
    print "Player1 and Player2 die of old age attempting to locate the explosive device"

if __name__ == "__main__":
    rock_paper_scissors(BombTech(), Dynamite())
    rock_paper_scissors(BombTech(), Scissors())
    rock_paper_scissors(Rock(), BombTech())
    rock_paper_scissors_game(BombTech(), BombTech())
    rock_paper_scissors_game(Dynamite(), BombTech())
    rock_paper_scissors(BombTech(), BombTech())
