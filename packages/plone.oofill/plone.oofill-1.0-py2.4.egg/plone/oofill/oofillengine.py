# -*- coding: utf-8 -*-
#
# File: plone.oofill.oofillengine
#
# Copyright (c) 2007 atReal
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

"""
$Id$
"""

__author__ = """Jean-Nicolas Bès <contact@atreal.net>"""
__docformat__ = 'plaintext'
__licence__ = 'GPL'


from zope.component import getMultiAdapter
from zope.interface import implements

from plone.oofill.interfaces import IOOFillEngine

from oofill.parser import OOFill

import StringIO

def renderMacro(context, view, viewname, macro):
    options = dict(template="here/@@"+viewname,
                   macro=macro)
    extra_context=dict(options = options,
                       view = view,
                       template = view.index)
    def wrapper():
        text = context.macro_renderer.pt_render( extra_context=extra_context)
        return text
    return wrapper

class OOFillPTWrapper(object):
    pass


class OOFillEngine(object):
    """An odt filling engine.
    """

    implements(IOOFillEngine)

    def fillFromView(self, odtfile, context, viewname, outfile=None):
        view = getMultiAdapter((context, context.REQUEST), name=viewname)
        obj = OOFillPTWrapper()
        for macro in view.index.macros.keys():
            setattr(obj, macro, renderMacro(context, view, viewname, macro))
        return self.fillFromObject(odtfile, obj, outfile)
    
    def fillFromObject(self, odtfile, obj, outfile=None):
        ofilinst = OOFill(odtfile)
        if outfile == None:
            outfile = StringIO.StringIO()
        ofilinst.render(obj, outfile)
        return outfile
