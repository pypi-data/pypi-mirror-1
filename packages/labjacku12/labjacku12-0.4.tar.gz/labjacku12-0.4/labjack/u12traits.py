#!/usr/bin/python
#
# Labjack U12 GUI
# (c) 2008 Robert Jordens <jordens@phys.ethz.ch> 
# 
# This driver is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This driver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this driver; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

from u12 import LabjackU12

from enthought.traits.api import HasTraits
from enthought.traits.api import Str, List as TList, Instance, Bool
from enthought.traits.api import (Str, Float, Int,
        File, List, Instance, Tuple, Property)
from enthought.traits.ui.api import View, Item, Group

class LabjackU12g(LabjackU12, HasTraits):
    pass

def main():
    for l in LabjackU12g.find_all():
        l.configure_traits()

if __name__ == "__main__":
    main()
