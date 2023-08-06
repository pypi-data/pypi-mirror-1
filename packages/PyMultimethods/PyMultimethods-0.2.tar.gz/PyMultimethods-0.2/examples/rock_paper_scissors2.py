# Copyright 2008 Nathan Davis

# Rock, Paper, Scissors, Part II
# See http://pymultimethods.wiki.sourceforge.net/Rock+Paper+Scissors2 for details

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

from multidispatch import anything
from rock_paper_scissors1 import *

class Dynamite: pass

@multimethod(Dynamite, anything)
def rock_paper_scissors(player1, player2):
    print "Dynamite blows up everything"
    print "Player1 wins"

@multimethod(anything, Dynamite)
def rock_paper_scissors(player1, player2):
    print "Dynamite blows up everything"
    print "Player2 wins"

@multimethod(Dynamite, Dynamite)
def rock_paper_scissors(player1, player2):
    print "Dynamite blows up everything"
    print "Mutual destruction"
    print "Both players lose"

if __name__ == "__main__":
    rock_paper_scissors(Rock(), Scissors()) # The old ones still work
    rock_paper_scissors(Dynamite(), Paper()) # Let's blow up some paper!
    rock_paper_scissors(Scissors(), Dynamite()) # Blowing something else up
    rock_paper_scissors(Dynamite(), Dynamite()) # Armagedon!
