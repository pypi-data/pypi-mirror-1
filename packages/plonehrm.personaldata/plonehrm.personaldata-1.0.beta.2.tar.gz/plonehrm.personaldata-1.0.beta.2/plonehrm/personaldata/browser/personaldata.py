from Acquisition import Explicit # Move to BrowserView?
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import Interface, implements
from zope.viewlet.interfaces import IViewlet


class IPersonalDataView(Interface):

    def getPersonalData():
        """Return all fields in a dict"""


class PersonalDataView(Explicit):
    """ Viewlet that renders the personal data within the employee viewlet manager
    """
    implements(IViewlet)
    render = ViewPageTemplateFile('personaldata.pt')

    def __init__(self, context, request, view=None, manager=None):
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def update(self):
        self.personal = self.context.personal

    def getPersonalData(self):
        data = {}
        fields = self.personal.Schema().viewableFields(self.personal)
        for field in fields:
            data[field.getName()] = field.get(self.personal)
        return data


class PhoneView(Explicit):
    """Return the fullname of the current employee"""
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def header(self):
        return 'Phone'

    def render(self):
        return self.context.personal.getTelephone()

class MobileView(Explicit):
    """Return the fullname of the current employee"""
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def header(self):
        return 'Mobile'

    def render(self):
        return self.context.personal.getMobilePhone()
