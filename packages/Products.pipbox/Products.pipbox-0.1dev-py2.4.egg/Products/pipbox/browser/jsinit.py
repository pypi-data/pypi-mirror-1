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
            try:
                selector, btype, search, replace, args = line.split('|')
                code = "%s\npb_init('%s','%s','%s','%s','%s');" % (code, selector, btype, search, replace, args)
            except ValueError:
                pass # XXX: log this

        return """jq(document).ready(function(){%s});""" % code
        
#         return """
# /* demonstration */
# jq(document).ready(function(){
#     // give all news item images a preview   
#   pb_init('.newsImageContainer a', '/image_view_fullscreen', '_preview', 'image', '');
#   // put all site actions in an ajax popup
#   pb_init('#siteaction-sitemap a', '', '', 'ajax', '');
#   // put all colophon links in an iframe popup
#   pb_init('#portal-colophon a', '', '', 'iframe', '');    
# });
#         """
