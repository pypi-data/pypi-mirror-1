from zope.interface import Interface
from zope.component import getMultiAdapter

from zope.interface import implements
from zope.component import getUtility

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from plone.i18n.normalizer.interfaces import IIDNormalizer

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone import utils
from Products.CMFCore.utils import getToolByName

from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from Products.ATContentTypes.interface import IATFolder

from plone.memoize.instance import memoize

from zope.i18nmessageid import MessageFactory

import random

successStoryPortletMessageFactory = MessageFactory('Products.ATSuccessStory')
_ = successStoryPortletMessageFactory


class IsuccessStoryPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    header = schema.TextLine(title=_(u"Header"),
                                  description=_(u"Portlet header"),
                                  required=True)
    searchpath = schema.Choice(title=_(u"Stories Path"),
                                  description=_(u"Search for success stories inside this path"),
                                  required=True,
                                  source=SearchableTextSourceBinder({'object_provides' : IATFolder.__identifier__}))


class Assignment(base.Assignment):
    """Portlet assignment.
    
    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    
    implements(IsuccessStoryPortlet)

    def __init__(self, header='Success Stories', searchpath='/'):
        self.header = header
        self.searchpath = searchpath


    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        return _(u"Success Story Portlet")

class Renderer(base.Renderer):
    """Portlet renderer.
    
    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('../templates/portlet_success.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        self.portal_url = portal_state.portal_url()
        self.portal = portal_state.portal()

    def search_stories(self):
        folder_path = self.get_searchpath()

        if folder_path:
            results = self.context.portal_catalog(path = folder_path, portal_type = 'ATSuccessStory')

            #import pdb;pdb.set_trace()
            if results:
                return random.choice(results)
            else:
                return None
        else:
            return None

    @property
    def header(self):
        return self.data.header

    @memoize
    def get_searchpath(self):
        folder_path = self.data.searchpath

        if folder_path[0]=='/':
            folder_path = folder_path[1:]

        folder = self.portal.restrictedTraverse(folder_path, default=None)

        if IATFolder.providedBy(folder):
            return '/'.join(folder.getPhysicalPath())
        else:
            return None



class AddForm(base.AddForm):
    """Portlet add form.
    
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IsuccessStoryPortlet)
    label = _(u"Add Success Story Portlet")
    description = _(u"This portlet displays a random success story")
    
    def create(self, data):
        assignment = Assignment()
        form.applyChanges(assignment, self.form_fields, data)
        return assignment

class EditForm(base.EditForm):
    """Portlet edit form.
    
    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IsuccessStoryPortlet)
    label = _(u"Add Success Story Portlet")
    description = _(u"This portlet displays a random success story")
