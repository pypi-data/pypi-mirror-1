#!/usr/bin/env python
# encoding: utf-8
"""
monkey.py

Created by Manabu Terada on 2009-09-20.
Copyright (c) 2009 CMScom. All rights reserved.
"""

from Products.ZCTextIndex.Lexicon import Lexicon
from Products.ZCTextIndex.Lexicon import _text2list

def termToWordIds(self, text):
    last = _text2list(text)
    for element in self._pipeline:
        process = getattr(element, "process_post_glob", element.process)
        last = process(last)
    wids = []
    for word in last:
        wids.append(self._wids.get(word, 0))
    return wids

Lexicon.termToWordIds = termToWordIds


## Hotfix of Plone catalog
from Products.GenericSetup.ZCatalog.exportimport import ZCatalogXMLAdapter
from Products.CMFCore.utils import getToolByName

from zope.component import queryMultiAdapter
from Products.GenericSetup.interfaces import INode
from Products.GenericSetup.ZCatalog.exportimport import _extra

def ng_initIndexes(self, node):
    zcatalog = self.context
    overwrite_indexs = []
    for child in node.childNodes:
        if child.nodeName != 'index':
            continue
        if child.hasAttribute('deprecated'):
            continue
        #zcatalog = self.context

        idx_id = str(child.getAttribute('name'))
        if child.hasAttribute('remove'):
            # Remove index if it is there; then continue to the next
            # index.  Removing a non existing index should not cause an
            # error, so you can apply the profile twice without problems.
            if idx_id in zcatalog.indexes():
                zcatalog.delIndex(idx_id)
            continue

        if child.hasAttribute('overwrite'):
            """ Hotfix Custom Attribute """
            if idx_id in zcatalog.indexes():
                zcatalog.delIndex(idx_id)
            overwrite_indexs.append(idx_id)

        if idx_id not in zcatalog.indexes():
            extra = _extra()
            for sub in child.childNodes:
                if sub.nodeName == 'extra':
                    name = str(sub.getAttribute('name'))
                    value = str(sub.getAttribute('value'))
                    setattr(extra, name, value)
            extra = extra.__dict__ and extra or None

            meta_type = str(child.getAttribute('meta_type'))
            zcatalog.addIndex(idx_id, meta_type, extra)

        idx = zcatalog._catalog.getIndex(idx_id)
        importer = queryMultiAdapter((idx, self.environ), INode)
        if importer:
            importer.node = child
    if overwrite_indexs:
        zcatalog.reindexIndex(name=overwrite_indexs, REQUEST=None)

ZCatalogXMLAdapter._initIndexes = ng_initIndexes