# -*- coding: utf-8 -*-
"""Viewlets."""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import ViewletBase
from plone.memoize.view import memoize

class DownloadCountViewlet(ViewletBase):
    """Browser view for displaying download count."""
    render = ViewPageTemplateFile("download_count.pt")

    def __init__(self, context, request, view, manager):
        super(DownloadCountViewlet, self).__init__(context, request, view, manager)
        
    @memoize
    def has_count(self):
        """Checks if this File has a download_count field."""
        return hasattr(self.context, 'download_count')
        
    @memoize
    def count(self):
        return self.context.download_count