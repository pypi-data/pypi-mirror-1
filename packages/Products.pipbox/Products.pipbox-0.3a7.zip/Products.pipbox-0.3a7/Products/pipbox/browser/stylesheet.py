#!/usr/bin/env python
# encoding: utf-8
"""
stylesheet.py

Created by Stephen McMahon on 2009-01-31.
"""

import os
from Globals import DTMLFile

from Products.Five.browser import BrowserView

this_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(this_dir, 'templates')

mystylesheet_dtml = DTMLFile('pipbox.css', templates_dir)


class PIPStylesheet(BrowserView):

    def __call__(self, *args, **kw):
        """Render DTML stylesheet"""

        context = self.context

        template = mystylesheet_dtml.__of__(context)
        return template(context=context)
