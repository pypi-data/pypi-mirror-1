#!/usr/bin/env python
# encoding: utf-8
"""
jsinit.py

Created by Stephen McMahon on 2009-02-01.
"""

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

class PIPJSInit(BrowserView):
    
    def __call__(self, *args, **kw):
        """Render JS Initialization code"""

        response = self.request.response
        context = self.context
        
        response.setHeader('Content-Type', 'application/x-javascript')

        prop_tool = getToolByName(self, 'portal_properties')
        ps = prop_tool.pipbox_properties
        table = ps.selector_specs
        
        code = ''
        for line in table:
            code = "%s\npb.doSetup(%s);" % (code, line.strip())

        return code
