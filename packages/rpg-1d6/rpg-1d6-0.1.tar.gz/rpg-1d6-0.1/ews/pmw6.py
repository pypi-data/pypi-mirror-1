#!/bin/env python
# This Python file uses the following encoding=utf-8

# Schlachtfeld - Großkämpfe im EWS System
#   http://rpg-tools-1d6.sf.net
# Copyright © 2007 - 2007 Achim Zien

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
# MA 02110-1301 USA

"""Do tests/checks (skills, etc.) according to the ±W6 rules => Throw a die."""


#### IMPORTS ####
from random import randint as rnd
#### IMPORTS ####


#### FUNCTIONS ####

def pmw6():
    """Throw the ±W6/±D6 die."""
    tmp = rnd(0,5)
    count = 1
    if tmp in [0,5]:
            while tmp == rnd(0,5):
                    count += 1
    wurf = count*ews[tmp]
    return wurf

def check(skill, MW):
    """Check if the throw reaches a target number (MW)."""
    if skill + pmw6() >= MW:
        return True
    else:
        return False
                
def open_check(skill, MW):
    """Check by how far we manage to beat the target number, or by how far we lose to it."""
    return skill - MW + pmw6()
    
def open_check_with_result(skill,  MW):
    """Check, by how far we beat (or get beaten by) a target number and also return, which absolute value we reach."""
    res = skill + pmw6()
    return res - MW,  res

#### FUNCTIONS ####


#### GAME PARS ####
ews = [-5, -3, -1, 2, 4, 6]
#### GAME PARS ####


#### SELF CHECK ####
if __name__ == '__main__':
        store = []
        for i in range(100000):
                store.append(pmw6())
        print 'min max'
        print min(store), max(store)
#### SELF CHECK ####
