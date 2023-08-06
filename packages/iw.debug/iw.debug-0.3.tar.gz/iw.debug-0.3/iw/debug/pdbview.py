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

import zope.component
import zope.interface

from ipdb import set_trace

try:
    from Products.Five import BrowserView
    from App.config import getConfiguration
    debug_mode = getConfiguration().debug_mode
except:
    from zope.publisher.browser import BrowserView
    debug_mode = True

valid_keys = ('v', 'view')

class PdbView(BrowserView):

    def pdb(self):
        context = self.context
        request = self.request
        try:
            portal = context.portal_url.getPortalObject()
        except AttributeError:
            portal = None

        def getView(name):
            return zope.component.queryMultiAdapter(
                    (context, request), name=name)

        view_name = None
        kwargs = self.request.form
        for k in valid_keys:
            if k in kwargs:
                view_name = kwargs.get(k, None)
                del kwargs[k]

        if view_name:
            view = getView(view_name)
        else:
            view = None

        if view_name and view is None:
            meth = getattr(context, view_name, None)
        else:
            meth = None

        if debug_mode:
            ll = locals().copy()
            for k in ('getView', 'kwargs', 'ipdb', 'self', 'view_name', 'k'):
                try:
                    del ll[k]
                except KeyError:
                    pass

            if callable(view):
                fn = view
            elif callable(meth):
                fn = meth
            else:
                fn = None

            if callable(fn):
                if kwargs:
                    set_trace()
                    fn(**kwargs)
                else:
                    set_trace()
                    fn()
            else:
                set_trace()

