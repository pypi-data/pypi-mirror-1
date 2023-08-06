from Products.CMFPlomino.fields.text import ITextField
from Products.CMFPlomino.fields.selection import ISelectionField
from Products.CMFPlomino.fields.number import INumberField
from Products.CMFPlomino.fields.datetime import IDatetimeField
from Products.CMFPlomino.fields.name import INameField
from Products.CMFPlomino.fields.doclink import IDoclinkField

import logging
logger = logging.getLogger('Plomino migration')

def migrate_to_130(db):
    """ PlominoField schema has been changed, all type-specific parameters
    have been removed and are now handled through specific adapters.
    """
    db.setDebugMode(False)
    
    for form in db.getForms():
        for field in form.getFields():
            type = field.getFieldType()
            if type == "TEXT":
                adapt = ITextField(field)
                adapt.widget = "TEXT"
            elif type == "NUMBER":
                adapt = INumberField(field)
                adapt.type = "INTEGER"
            elif type == "FLOAT":
                field.setFieldType("NUMBER")
                adapt = INumberField(field)
                adapt.type = "FLOAT"
            elif type == "NAME":
                adapt = INameField(field)
                adapt.type = "SINGLE"
            elif type == "NAMES":
                field.setFieldType("NAME")
                adapt = INameField(field)
                adapt.type = "MULTI"
            elif type in ("SELECTION", "MULTISELECTION", "CHECKBOX", "RADIO"):
                field.setFieldType("SELECTION")
                adapt = ISelectionField(field)
                l = getattr(field, "SelectionList", None)
                if l is not None:
                    adapt.selectionlist = list(l)
                v = getattr(field, "SelectionListFormula", None)
                if v is not None:
                    adapt.selectionlistformula = v.raw
                adapt.separator = getattr(field, "DisplayModList", getattr(field, "OtherDisplayMod", None))
                if type == "SELECTION":
                    adapt.widget = "SELECT"
                elif type == "MULTISELECTION":
                    adapt.widget = "MULTISELECT"
                elif type == "CHECKBOX":
                    adapt.widget = "CHECKBOX"
                elif type == "RADIO":
                    adapt.widget = "RADIO"
            elif type == "DOCLINK":
                adapt = IDoclinkField(field)
                v = getattr(field, "SelectionListFormula", None)
                if v is not None:
                    adapt.documentslistformula = v.raw
                
    db.plomino_version = "1.3.0"