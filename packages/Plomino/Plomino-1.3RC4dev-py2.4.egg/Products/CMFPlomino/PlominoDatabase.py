# -*- coding: utf-8 -*-
#
# File: PlominoDatabase.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
# Generator: ArchGenXML Version 2.0
#            http://plone.org/products/archgenxml
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.org>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.CMFPlomino.config import *

##code-section module-header #fill in your manual code here
from Products.Archetypes.public import *
from Products.Archetypes.utils import make_uuid

from zope import event
from zope.app.container.contained import ObjectRemovedEvent
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from OFS.Folder import *
from Products.CMFPlomino.PlominoUtils import *
import string
import Globals

from index.PlominoIndex import PlominoIndex
from PlominoAccessControl import PlominoAccessControl
from PlominoDesignManager import PlominoDesignManager
from PlominoReplicationManager import PlominoReplicationManager
from PlominoScheduler import PlominoScheduler

from Products.CMFCore.PortalFolder import PortalFolderBase as PortalFolder

##/code-section module-header

schema = Schema((

    TextField(
        name='AboutDescription',
        allowable_content_types=('text/html',),
        widget=RichWidget(
            label="About this database",
            description="Describe the database, its objectives, its targetted audience, etc...",
            label_msgid='CMFPlomino_label_AboutDescription',
            description_msgid='CMFPlomino_help_AboutDescription',
            i18n_domain='CMFPlomino',
        ),
        default_output_type="text/html",
    ),
    TextField(
        name='UsingDescription',
        allowable_content_types=('text/html',),
        widget=RichWidget(
            label="Using this database",
            description="Describe how to use the database",
            label_msgid='CMFPlomino_label_UsingDescription',
            description_msgid='CMFPlomino_help_UsingDescription',
            i18n_domain='CMFPlomino',
        ),
        default_output_type="text/html",
    ),
    BooleanField(
        name='IndexAttachments',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Index file attachments",
            description="If enabled, files attached in File Attachments fields will be indexed. It might increase the index size.",
            label_msgid='CMFPlomino_label_IndexAttachments',
            description_msgid='CMFPlomino_help_IndexAttachments',
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='debugMode',
        default="False",
        widget=BooleanField._properties['widget'](
            label="Debug mode",
            description="If enabled, script and formula errors are logged.",
            label_msgid='CMFPlomino_label_debugMode',
            description_msgid='CMFPlomino_help_debugMode',
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='StorageAttachments',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Use File System Storage for attachments",
            description="File System Storage must be installed on the portal",
            label_msgid='CMFPlomino_label_StorageAttachments',
            description_msgid='CMFPlomino_help_StorageAttachments',
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='CountDocuments',
        widget=BooleanField._properties['widget'](
            label="Count the number of documents",
            description="If enabled, count the number of documents for each view. Display might be slower.",
            description_msgid="CMFPlomino_description_ShowDocumentsNumbers",
            label_msgid="CMFPlomino_label_ShowDocumentsNumbers",
            i18n_domain='CMFPlomino',
        ),
    ),
    StringField(
        name='DateTimeFormat',
        default="%Y/%m/%d",
        widget=StringField._properties['widget'](
            label='Datetimeformat',
            label_msgid='CMFPlomino_label_DateTimeFormat',
            i18n_domain='CMFPlomino',
        ),
    ),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoDatabase_schema = getattr(ATFolder, 'schema', Schema(())).copy() + \
    getattr(PlominoAccessControl, 'schema', Schema(())).copy() + \
    getattr(PlominoDesignManager, 'schema', Schema(())).copy() + \
    getattr(PlominoReplicationManager, 'schema', Schema(())).copy() + \
    getattr(PlominoScheduler, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoDatabase(ATFolder, PlominoAccessControl, PlominoDesignManager, PlominoReplicationManager, PlominoScheduler):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IPlominoDatabase)

    meta_type = 'PlominoDatabase'
    _at_rename_after_creation = True

    schema = PlominoDatabase_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('__init__')
    def __init__(self,oid,**kw):
        """
        """
        ATFolder.__init__(self, oid, **kw)
        self.plomino_version = VERSION
        PlominoAccessControl.__init__(self)

    security.declarePublic('at_post_create_script')
    def at_post_create_script(self):
        """DB initialization
        """
        self.initializeACL()
        index = PlominoIndex()
        self._setObject(index.getId(), index)
        resources = Folder('resources')
        resources.title='resources'
        self._setObject('resources', resources)
        scripts = Folder('scripts')
        scripts.title='scripts'
        self._setObject('scripts', scripts)

    security.declarePublic('getForms')
    def getForms(self):
        """return the database forms list
        """
        formlist = self.portal_catalog.search({'portal_type' : ['PlominoForm'], 'path': '/'.join(self.getPhysicalPath())})
        orderedformlist = []
        for f in formlist:
            f_obj = f.getObject()
            if not f_obj is None :
                orderedformlist.append([f_obj.getPosition(), f_obj])
        orderedformlist.sort()
        return [i[1] for i in orderedformlist]

    security.declarePublic('getViews')
    def getViews(self):
        """return the database views list
        """
        viewlist = self.portal_catalog.search({'portal_type' : ['PlominoView'], 'path': '/'.join(self.getPhysicalPath())})
        orderedviewlist = []
        for v in viewlist:
            v_obj = v.getObject()
            if not v_obj is None :
                orderedviewlist.append([v_obj.getPosition(), v_obj])
        orderedviewlist.sort()
        return [i[1] for i in orderedviewlist]

    security.declarePublic('getAgents')
    def getAgents(self):
        """return the database agents list
        """
        list = self.portal_catalog.search({'portal_type' : ['PlominoAgent'], 'path': '/'.join(self.getPhysicalPath())})
        return [a.getObject() for a in list]

    security.declarePublic('getForm')
    def getForm(self,formname):
        """return a PlominoForm
        """
        obj = getattr(self, formname, None)
        if obj is not None and obj.Type() == 'PlominoForm':
            return obj
        else:
            return None

    security.declarePublic('getView')
    def getView(self,viewname):
        """return a PlominoView
        """
        obj = getattr(self, viewname, None)
        if obj is not None and obj.Type() == 'PlominoView':
            return obj
        else:
            return None

    security.declareProtected(CREATE_PERMISSION, 'createDocument')
    def createDocument(self):
        """create a unique ID and invoke PlominoDocument factory
        """
        newid = make_uuid()
        self.invokeFactory( type_name='PlominoDocument', id=newid)
        doc = getattr(self, newid)
        return doc

    security.declarePublic('getDocument')
    def getDocument(self, docid):
        """return a PlominoDocument
        """
        return getattr(self, docid, None)

    security.declareProtected(EDIT_PERMISSION, 'deleteDocument')
    def deleteDocument(self,doc):
        """delete the document from database
        """
        if not self.isCurrentUserAuthor(doc):
            raise Unauthorized, "You cannot delete this document."
        else:
            # execute the onDeleteDocument code of the form
            try:
                form = doc.getForm()
                self.runFormulaScript("form_"+form.id+"_ondelete", doc, form.onDeleteDocument)
            except Exception:
                pass

            self.getIndex().unindexDocument(doc)
            event.notify(ObjectRemovedEvent(doc, self, doc.id))
            return PortalFolder.manage_delObjects(self, doc.id, None)

    security.declarePublic('getIndex')
    def getIndex(self):
        """return the database index
        """
        return getattr(self, 'plomino_index')

    security.declarePublic('getAllDocuments')
    def getAllDocuments(self):
        """return all the database documents
        """
        #return [d.getObject() for d in self.portal_catalog.search({'portal_type' : ['PlominoDocument'], 'path': '/'.join(self.getPhysicalPath())})]
        index = self.getIndex()
        res = index.dbsearch({},None)
        return [d.getObject() for d in res]

    security.declarePublic('isDocumentsCountEnabled')
    def isDocumentsCountEnabled(self):
        """
        """
        try :
            return self.CountDocuments
        except Exception :
            return False


registerType(PlominoDatabase, PROJECTNAME)
# end of class PlominoDatabase

##code-section module-footer #fill in your manual code here
##/code-section module-footer



