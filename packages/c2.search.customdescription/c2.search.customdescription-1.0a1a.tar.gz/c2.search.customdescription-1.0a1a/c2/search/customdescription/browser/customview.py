#!/usr/bin/env python
# encoding: utf-8
"""
customview.py

Created by Manabu Terada on 2009-11-12.
Copyright (c) 2009 CMScom. All rights reserved.
"""
from Acquisition import aq_inner
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils

def _cut_shortname(text):
    return text.split(u' ', 1)[-1]

def _get_position(text, target):
    try:
        position = text.index(target)
    except ValueError:
        position = None
    return position

def _cut_text(text, target, length, position):
    if position is None:
        return text[:length], False, True
    text_len = len(text)
    pre_len = max(0, position-length/2)
    is_pre_cut = bool(pre_len)
    is_suf_cut = True
    if is_pre_cut:
        suf_len = position + length/2
        if text_len < suf_len:
            pre_len = max(0, pre_len - (suf_len - text_len))
            is_suf_cut = False
    else:
        suf_len = length
    t = text[pre_len:suf_len]
    t_withclass = _ins_hightlight_class(t, target, position)
    return t_withclass, is_pre_cut, is_suf_cut

def _ins_hightlight_class(text, target, position):
    target_length = len(target)
    pre_t = text[:position]
    t = '<span class="highlightedSearchTerm">' + text[position:position+target_length] + '</span>'
    suf_t = text[position+target_length:]
    return pre_t + t + suf_t

class Plone(BrowserView):
    def cropText(self, text, target, length, ellipsis=u'...'):
        """Crop text on a word boundary
        """
        converted = False
        encoding = utils.getSiteEncoding(aq_inner(self.context))
        if not isinstance(text, unicode):
            text = unicode(text, encoding)
            converted = True
        if not isinstance(target, unicode):
            target = unicode(target, encoding)
        if not isinstance(ellipsis, unicode):
            ellipsis = unicode(ellipsis, encoding)
        ex_text = _cut_shortname(text)
        position = _get_position(ex_text, target)
        if len(ex_text)>length:
            ex_text, is_pre_cut, is_suf_cut = _cut_text(ex_text, target, length, position)
            if ex_text:
                if is_pre_cut:
                    ex_text = ellipsis + ex_text
                if is_suf_cut:
                    ex_text += ellipsis
        else:
            if position is not None:
                ex_text = _ins_hightlight_class(ex_text, target, position)
        if converted:
            # encode back from unicode
            ex_text = ex_text.encode(encoding)
        return ex_text