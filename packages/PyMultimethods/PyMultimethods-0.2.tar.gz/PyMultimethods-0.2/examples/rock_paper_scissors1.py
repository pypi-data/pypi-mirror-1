# Copyright 2007, 2008 Nathan Davis

# Rock, Paper, Scissors, Part I
# See http://pymultimethods.wiki.sourceforge.net/Rock+Paper+Scissors1 for details

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

from multidispatch import multimethod

class Rock: pass
class Paper: pass
class Scissors: pass
 
@multimethod(Rock, Rock)
def rock_paper_scissors(player1, player2):
    print "Tie"
 
@multimethod(Rock, Paper)
def rock_paper_scissors(player1, player2):
    print "Paper covers Rock"
    print "Player2 wins"
 
@multimethod(Rock, Scissors)
def rock_paper_scissors(player1, player2):
    print "Rock crushes Scissors"
    print "Player1 wins"
 
@multimethod(Paper, Rock)
def rock_paper_scissors(player1, player2):
    print "Paper covers Rock"
    print "Player1 wins"
 
@multimethod(Paper, Paper)
def rock_paper_scissors(player1, player2):
    print "Tie"
 
@multimethod(Paper, Scissors)
def rock_paper_scissors(player1, player2):
    print "Scissors cuts Paper"
    print "Player2 wins"
 
@multimethod(Scissors, Rock)
def rock_paper_scissors(player1, player2):
    print "Rock crushes Scissors"
    print "Player2 wins"
 
@multimethod(Scissors, Paper)
def rock_paper_scissors(player1, player2):
    print "Scissors cuts paper"
    print "Player1 wins"
 
@multimethod(Scissors, Scissors)
def rock_paper_scissors(player1, player2):
    print "Tie"

if __name__ == "__main__":
    rock_paper_scissors(Rock(), Rock())
    rock_paper_scissors(Rock(), Paper())
    rock_paper_scissors(Rock(), Scissors())
    rock_paper_scissors(Paper(), Rock())
    rock_paper_scissors(Paper(), Paper())
    rock_paper_scissors(Paper(), Scissors())
    rock_paper_scissors(Scissors(), Rock())
    rock_paper_scissors(Scissors(), Paper())
    rock_paper_scissors(Scissors(), Scissors())
