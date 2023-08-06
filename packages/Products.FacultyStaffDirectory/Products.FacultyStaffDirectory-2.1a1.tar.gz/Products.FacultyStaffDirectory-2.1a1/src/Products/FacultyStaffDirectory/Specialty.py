# -*- coding: utf-8 -*-

__author__ = """WebLion <support@weblion.psu.edu>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.Relations.field import RelationField
from Products.FacultyStaffDirectory.config import *
from Products.FacultyStaffDirectory.PersonGrouping import PersonGrouping
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName

from Products.FacultyStaffDirectory.interfaces.specialty import ISpecialty
from Products.FacultyStaffDirectory.permissions import ASSIGN_SPECIALTIES_TO_PEOPLE

from zope.interface import implements

schema = Schema((

    RelationField(
        name='people',
        widget=ReferenceBrowserWidget(
            label=u'People',
            label_msgid='FacultyStaffDirectory_label_people',
            i18n_domain='FacultyStaffDirectory',
            base_query={'portal_type':'FSDPerson', 'sort_on':'getSortableName'},
            allow_browse=0,
            allow_search=1,
            show_results_without_query=1,      
        ),
        write_permission=ASSIGN_SPECIALTIES_TO_PEOPLE,
        allowed_types=('FSDPerson',),
        multiValued=True,
        relationship='SpecialtyInformation'  # weird relationship name is ArchGenXML's fault
    ),
),
)

Specialty_schema = getattr(PersonGrouping, 'schema', Schema(())).copy() + schema.copy()

class Specialty(PersonGrouping):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(PersonGrouping,'__implements__',()),)
    implements(ISpecialty)
    meta_type = portal_type = 'FSDSpecialty'

    _at_rename_after_creation = True
    schema = Specialty_schema
    # Methods
    security.declareProtected(View, 'getSpecialtyInformation')
    def getSpecialtyInformation(self, person):
        """
        Get the specialty information for a specific person
        """
        refCatalog = getToolByName(self, 'reference_catalog')
        refs = refCatalog.getReferences(self, 'SpecialtyInformation', person)

        if refs:
            return refs[0].getContentObject()
        else:
            return None

registerType(Specialty, PROJECTNAME)
