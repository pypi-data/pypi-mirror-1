# -*- coding: utf-8 -*-

import grokcore.component as grok
from zope.app.container import btree


class Container(grok.Context, btree.BTreeContainer):
    """Example Container. 
    """
    __name__ = u'container'


class Content(grok.Context):
    """Example Content.
    """
    def __init__(self, title, number):
        self.title = title
        self.number = number
