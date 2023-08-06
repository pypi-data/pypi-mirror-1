from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import BaseContent
from Products.Archetypes.atapi import BaseSchema
from Products.Archetypes.atapi import CalendarWidget
from Products.Archetypes.atapi import DateTimeField
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import registerType
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

from Products.plonehrm.interfaces import IEmployeeModule
from plonehrm.personaldata import PersonalMessageFactory as _
from plonehrm.personaldata import config
from plonehrm.personaldata.interfaces import IPersonalData


schema = Schema((
    StringField(
        name='address',
        widget=StringWidget(
            label=_(u'label_address', default='Address'),
        ),
    ),
    StringField(
        name='postalCode',
        widget=StringWidget(
            label=_(u'label_postalCode', default=u'Postalcode'),
        ),
    ),
    StringField(
        name='city',
        widget=StringWidget(
            label=_(u'label_city', default=u'City'),
        ),
    ),
    StringField(
        name='state',
        widget=StringWidget(
            label=_(u'label_state', default=u'State/Province'),
        ),
    ),
    StringField(
        name='country',
        widget=StringWidget(
            label=_(u'label_country', default=u'Country'),
        ),
    ),
    StringField(
        name='telephone',
        widget=StringWidget(
            label=_(u'label_telephone', default=u'Phone'),
        ),
    ),
    StringField(
        name='mobilePhone',
        widget=StringWidget(
            label=_(u'label_mobilePhone', default=u'Mobilephone'),
        ),
    ),
    StringField(
        name='email',
        widget=StringWidget(
            label=_(u'label_email', default=u'Email'),
        ),
    ),
    DateTimeField(
        name='birthDate',
        widget=CalendarWidget(
            starting_year=1940,
            show_hm=0,
            label=_(u'label_birthDate', default=u'Birth date'),
        ),
    ),
    StringField(
        name='placeOfBirth',
        widget=StringWidget(
            label=_(u'label_placeOfBirth', default=u'Place of birth'),
        ),
    ),
    StringField(
        name='gender',
        widget=SelectionWidget(
            format="select",
            label=_(u'label_gender', default=u'Gender'),
        ),
        vocabulary='_genderVocabulary'
    ),
    StringField(
        name='civilStatus',
        widget=SelectionWidget(
            format="select",
            label=_(u'label_civilStatus', default=u'Civil status'),
        ),
        vocabulary='_civilStatusVocabulary'
    ),
    StringField(
        name='idType',
        widget=SelectionWidget(
            format="select",
            label=_(u'label_idType', default=u'Type of ID'),
        ),
        vocabulary='_idTypeVocabulary'
    ),
    StringField(
        name='idNumber',
        widget=StringWidget(
            label=_(u'label_idNumber', default=u'ID number'),
        ),
    ),
    DateTimeField(
        name='idEndDate',
        widget=CalendarWidget(
            show_hm=0,
            starting_year=2007,
            label=_(u'label_idEndDate', default=u'Expiration date'),
        ),
    ),
    StringField(
        name='nationality',
        widget=StringWidget(
            label=_(u'label_nationality', default=u'Nationality'),
        ),
    ),
    StringField(
        name='socialSecurityNumber',
        widget=StringWidget(
            label=_(u'label_socialSecurityNumber',
                    default=u'Social security number'),
        ),
    ),
    StringField(
        name='bankNumber',
        widget=StringWidget(
            label=_(u'label_bankNumber', default=u'Bank number'),
        ),
    ),
),
)

PersonalData_schema = BaseSchema.copy() + schema.copy()

PersonalData_schema['title'].widget.visible = 0
PersonalData_schema['state'].widget.condition = 'object/showState'
PersonalData_schema['country'].widget.condition = 'object/showCountry'


class PersonalData(BaseContent):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (BaseContent.__implements__,)
    implements(IEmployeeModule, IPersonalData)

    _at_rename_after_creation = True

    schema = PersonalData_schema

    security.declarePublic('showState')
    def showState(self):
        """Should the state widget be shown?
        """
        return self._extractVocabulary(name='show_state',
                                       default=True)

    security.declarePublic('showCountry')
    def showCountry(self):
        """Should the country widget be shown?
        """
        return self._extractVocabulary(name='show_country',
                                       default=True)

    security.declarePublic('_genderVocabulary')
    def _genderVocabulary(self):
        """Return vocabulary for gender.
        """
        return self._extractVocabulary(name='gender_vocabulary',
                                       default=[])

    security.declarePublic('_civilStatusVocabulary')
    def _civilStatusVocabulary(self):
        """Return vocabulary for civil status.
        """
        return self._extractVocabulary(name='civil_status_vocabulary',
                                       default=[])

    security.declarePublic('_idTypeVocabulary')
    def _idTypeVocabulary(self):
        """Return vocabulary for ID type.
        """
        return self._extractVocabulary(name='id_type_vocabulary',
                                       default=[])

    def _extractVocabulary(self, name='', default=True):
        """Return vocabulary for ID type.
        """
        pp = getToolByName(self, 'portal_properties')
        pdp = getattr(pp, 'personaldata_properties', None)
        if not pdp:
            return default
        return pdp.getProperty(name, default)

    security.declarePublic('view')
    def view(self):
        """Redirect to the employee.

        Plone adds /view to the URL of personaldata objects in the 'recently
        changed items' portlet.  This gives a 'page not found'.  Adding this
        view() method gives a handy way of circumventing it.  It (a) doesn't
        give us a 404 anymore and (b) redirects to the employee itself.

        """
        response = self.REQUEST.response
        our_url = self.absolute_url()
        response.redirect(our_url + '/..')

registerType(PersonalData, config.PROJECTNAME)
