# -*- coding: utf-8 -*-
"""Extend default Plone content types."""

from Products.Archetypes.public import IntegerField
from archetypes.schemaextender.field import ExtensionField

class MyIntegerField(ExtensionField, IntegerField):
    """A simple integer field."""
    
from zope.component import adapts
from zope.interface import implements
from archetypes.schemaextender.interfaces import ISchemaExtender
from Products.Archetypes.public import StringWidget
from Products.ATContentTypes.interface import IATFile

class FileExtender(object):
    """Extends default File content type."""
    adapts(IATFile)
    implements(ISchemaExtender)

    fields = [
        MyIntegerField(
            "download_count",
            widget = StringWidget(label="How many times was this file downloaded", modes=('view', )),
            default=0,
            ),
            ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
