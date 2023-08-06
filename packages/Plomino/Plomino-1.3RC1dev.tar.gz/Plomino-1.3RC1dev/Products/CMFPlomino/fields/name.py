# -*- coding: utf-8 -*-
#
# File: name.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.com>"""
__docformat__ = 'plaintext'

from zope.formlib import form
from zope.interface import implements
from zope.schema import getFields
from zope.schema import TextLine, Text, List, Choice
from zope.schema.vocabulary import SimpleVocabulary
from dictionaryproperty import DictionaryProperty

from Products.Five.formlib.formbase import EditForm

from base import IBaseField, BaseField

class INameField(IBaseField):
    """
    Name field schema
    """
    type = Choice(vocabulary=SimpleVocabulary.fromItems([("Single valued", "SINGLE"),
                                                           ("Multi valued", "MULTI")
                                                           ]),
                    title=u'Type',
                    description=u'Single or multi valued name field',
                    default="SINGLE",
                    required=True)
    separator = TextLine(title=u'Separator',
                      description=u'Only apply if multi-valued',
                      required=False)
    
class NameField(BaseField):
    """
    """
    implements(INameField)
    
    def getNamesList(self):
        """return a list, format: fullname|userid
        """
        
        all = self.context.getPortalMembers()
        s=[]
        for m in all:
            userid=m.getUserId()
            fullname = m.getProperty("fullname")
            if fullname=='':
                s.append(userid+'|'+userid)
            else:
                s.append(fullname+'|'+userid)
        return s
        
for f in getFields(INameField).values():
    setattr(NameField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(EditForm):
    """
    """
    form_fields = form.Fields(INameField)
    