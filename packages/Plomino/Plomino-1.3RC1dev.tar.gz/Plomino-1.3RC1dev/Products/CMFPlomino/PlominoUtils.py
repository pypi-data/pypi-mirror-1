# -*- coding: utf-8 -*-
#
# File: PlominoAccessControl.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.com>"""
__docformat__ = 'plaintext'

from DateTime import DateTime
from time import strptime
from Products.CMFCore.utils import getToolByName
import htmlentitydefs as entity

def DateToString(d, format='%d/%m/%Y'):
    """return the date as string using the given format, default is '%d/%m/%Y'
    """
    #return DateTime(*d[0:6]).strftime(format)
    return d.strftime(format)

def StringToDate(str_d, format='%d/%m/%Y'):
    """parse the string using the given format (default is '%d/%m/%Y') and return the date 
    """
    dt = strptime(str_d, format)
    if len(dt)>=5:
        return DateTime(dt[0], dt[1], dt[2], dt[3], dt[4])
    else:
        return DateTime(dt[0], dt[1], dt[2])

def DateRange(d1, d2):
    """return all the days from the d1 date to the d2 date (included)
    """
    duration = int(d2-d1)
    result=[]
    current=d1
    for d in range(duration+1):
        result.append(current)
        current = current+1
    return result

def Now():
    """ current date and tile
    """
    return DateTime()

def sendMail(db, recipients, title, html_message):
    """Send an email
    """
    host = getToolByName(db, 'MailHost')
    plone_tools = getToolByName(db, 'plone_utils')
    message = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
    message = message + "<html>"
    message = message + html_message
    message = message + "</html>"
    sender = db.getCurrentUser().getProperty("email")
    mail = "From: "+sender+'\n'
    mail = mail + "To: "+recipients+'\n'
    mail = mail + "Subject: "+ title + '\n'
    mail = mail + 'Content-type: text/html\n\n'
    mail = mail + message
    #host.send(mail)
    #host.send(message, mto=recipients, mfrom=sender, subject=title, encode="ISO-8859-1")
    encoding = plone_tools.getSiteEncoding()
    host.secureSend(message, recipients,
        sender, subject=title,
        subtype='html', charset=encoding,
        debug=False, From=sender)
    
def userFullname(db, userid):
    """ return user fullname if exist, else return userid, and return Unknown if user not found
    """
    user=getToolByName(db, 'portal_membership').getMemberById(userid)
    if not(user is None):
        fullname=user.getProperty('fullname')
        if fullname=='':
            return userid
        else:
            return fullname
    else:
        return "Unknown"
        
def userInfo(db, userid):
    """ return user object
    """
    user=getToolByName(db, 'portal_membership').getMemberById(userid)
    return user

def PlominoTranslate(message, context, domain='CMFPlomino'):
    """
    """
    plone_tools = getToolByName(db, 'plone_utils')
    encoding = plone_tools.getSiteEncoding()
    translation_service = getToolByName(context, 'translation_service')
    if isinstance(message, Exception):
        try:
            message = message[0]
        except (TypeError, IndexError):
            pass     
    msg = translation_service.translate(msgid=message, domain=domain)
    return msg.encode(encoding) # convert unicode to site encoding

def htmlencode(s):
    """ replace unicode characters with their corresponding html entities
    """
    
    t=""
    for i in s:
        if ord(i) in entity.codepoint2name:
            name = entity.codepoint2name.get(ord(i))
            entityCode = entity.name2codepoint.get(name)
            t +="&#" + str(entityCode)
        else:
            t+=i
    return t

           