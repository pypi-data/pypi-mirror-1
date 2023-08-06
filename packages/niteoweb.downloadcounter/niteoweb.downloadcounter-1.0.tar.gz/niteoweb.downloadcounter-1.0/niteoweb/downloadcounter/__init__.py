# -*- coding: utf-8 -*-
"""Initializer."""

import AccessControl


# Allow access to increase_download_count() from Script (Python)
AccessControl.ModuleSecurityInfo('niteoweb.downloadcounter').declarePublic('increase_download_count')

def increase_download_count(file):
    """Increases download count integer on a File."""
    if hasattr(file, 'download_count'):
        file.download_count += 1

def initialize(context):
    """Initializer called when used as a Zope 2 product."""


