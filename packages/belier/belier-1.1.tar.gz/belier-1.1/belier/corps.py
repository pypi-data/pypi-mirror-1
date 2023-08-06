# -*- coding: utf-8 -*-
# Copyright © 2008 Carl Chenet <chaica@ohmytux.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#Deroulement principal de belier
"""Déroulement principal de bélier"""

from belier.terminal import Terminal
from belier.options import Options

class Corps:
    """Classe principale de bélier"""

    def __init__(self):
        opts = Options()
        Terminal(opts) 
