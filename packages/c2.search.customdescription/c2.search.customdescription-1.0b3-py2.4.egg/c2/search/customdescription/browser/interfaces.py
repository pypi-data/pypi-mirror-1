#!/usr/bin/env python
# encoding: utf-8
"""
interfaces.py

Created by Manabu Terada on 2009-11-12.
Copyright (c) 2009 CMScom. All rights reserved.
"""
from zope.interface import Interface

class ICustomPlone(Interface):
    def cropText(self, text, length, ellipsis='...'):
        """Crop text on a word boundary
        """