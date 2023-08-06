#!/usr/bin/env python
# encoding: utf-8
"""
forms.py

Created by Daniel Greenfeld on 2008-06-10.
Copyright (c) 2008 __NASA__. All rights reserved.
"""

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView




class Utility(BrowserView):
    
    def get_user_friendly_types(self):
        """return user friendly types"""
        utils = getToolByName(self.context,"plone_utils")
        return sorted(utils.getUserFriendlyTypes())