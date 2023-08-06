#!/usr/bin/env python
# encoding: utf-8
"""
monkey.py

Created by Manabu Terada on 2010-01-30.
Copyright (c) 2010 CMScom. All rights reserved.
"""
from Acquisition import aq_inner
from plone.app.content.browser.foldercontents import FolderContentsTable

from plone.app.content.browser.foldercontents import FolderContentsView

from logging import getLogger
logger = getLogger(__name__)
info = logger.info


def contents_table(self):
    table = FolderContentsTable(aq_inner(self.context), self.request, 
                    contentFilter={"show_inactive":True})
    return table.render()

FolderContentsView.contents_table = contents_table
info('patched %s', str(FolderContentsView.contents_table))
