# -*- coding: utf-8 -*-
#
# File: datetime.py
#
# Copyright (c) 2009 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.com>"""
__docformat__ = 'plaintext'

from zope.formlib import form
from zope.interface import implements
from zope.schema import getFields
from zope.schema import TextLine, Text, Choice
from zope.schema.vocabulary import SimpleVocabulary

from dictionaryproperty import DictionaryProperty

from Products.Five.formlib.formbase import EditForm
from Products.CMFPlomino.PlominoUtils import StringToDate

from base import IBaseField, BaseField

import logging
logger=logging.getLogger("datetime")

class IDatetimeField(IBaseField):
    """
    DateTime field schema
    """
    format = TextLine(title=u'Format',
                      description=u'Date/time format (if different than database default format)',
                      required=False)

class DatetimeField(BaseField):
    """
    """
    implements(IDatetimeField)

    def validate(self, submittedValue):
        """
        """
        errors=[]
        fieldname = self.context.id
        try:
            # calendar widget default format is '%Y-%m-%d %H:%M'
            v = StringToDate(submittedValue, '%Y-%m-%d %H:%M')
        except:
            errors.append(fieldname+" must be a date/time (submitted value was: "+submittedValue+")")
        return errors
    
    def processInput(self, submittedValue):
        """
        """
        # calendar widget default format is '%Y-%m-%d %H:%M'
        logger.error(submittedValue)
        return StringToDate(submittedValue, '%Y-%m-%d %H:%M')
    
for f in getFields(IDatetimeField).values():
    setattr(DatetimeField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(EditForm):
    """
    """
    form_fields = form.Fields(IDatetimeField)
    