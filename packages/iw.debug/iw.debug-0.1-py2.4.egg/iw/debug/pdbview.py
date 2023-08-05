# -*- coding: utf-8 -*-
# Copyright (C)2007 Ingeniweb

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Contains the PDB view. It will start the python debugger or the ipython python
debugger if available.
It will only start if the zope instance is in debug mode.
"""

from Products.Five import BrowserView
from App.config import getConfiguration

class PdbView(BrowserView):
    def pdb(self):
        context = self.context
        portal = context.portal_url.getPortalObject()
        cfg = getConfiguration()
        if cfg.debug_mode:
            try:
                import ipdb
                ipdb.set_trace()
            except:
                import pdb
                pdb.set_trace()
