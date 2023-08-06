from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

from Acquisition import aq_inner
from DateTime.DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from Products.ATContentTypes.interface import IATTopic

class IContentSearchPortlet(IPortletDataProvider):
    """ A portlet displaying a (live) search box
    """

#    enableLivesearch = schema.Bool(
#            title = _(u"Enable LiveSearch"),
#            description = _(u"Enables the LiveSearch feature, which shows "
#                             "live results if the browser supports "
#                             "JavaScript."),
#            default = True,
#            required = False)

#    header = schema.TextLine(title=_(u"Portlet header"),
#                             description=_(u"Title of the rendered portlet"),
#                             required=True)

    target_collection = schema.Choice(title=_(u"Target collection"),
                                  description=_(u"Find the collection which provides the items to list"),
                                  required=True,
                                  source=SearchableTextSourceBinder({'object_provides' : IATTopic.__identifier__},
                                                                    default_query='path:'))

class Assignment(base.Assignment):
    implements(IContentSearchPortlet)

    target_collection=None

#    def __init__(self, enableLivesearch=True):
#        self.enableLivesearch=enableLivesearch

    def __init__(self, target_collection=None):
        self.target_collection = target_collection

    @property
    def title(self):
        return _(u"Search")


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('contentsearchportlet.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)

        portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
        self.portal_url = portal_state.portal_url()

#    def enable_livesearch(self):
#        return self.data.enableLivesearch

#    def search_form(self):
#        return '%s/search_form' % self.portal_url

#    def search_action(self):
#        return '%s/search' % self.portal_url

    def action_url(self):
        return '%s/@@content-search-result-view' % self.portal_url

    @memoize
    def collection(self):
        """ get the collection the portlet is pointing to"""
        
        collection_path = self.data.target_collection
        if not collection_path:
            return None

        if collection_path.startswith('/'):
            collection_path = collection_path[1:]
        
        if not collection_path:
            return None

        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        return portal.restrictedTraverse(collection_path, default=None)

    def collection_query(self):
        """Returns list of collection query with search words."""
        words = self.request.get('SearchableContentText', None)
        if words:
            return self.collection().queryCatalog(SearchableText=words)
        else:
            return None

    def collection_title_url(self):
        """Returns list of title and url dictionary of collection_query."""
        collection_query = self.collection_query()
        if collection_query:
            return [{'title':i.Title,'url':i.getURL()} for i in collection_query]
        else:
            return None

class AddForm(base.AddForm):
    form_fields = form.Fields(IContentSearchPortlet)

    label = _(u"Add Search Portlet")
    description = _(u"This portlet shows a search box.")

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(IContentSearchPortlet)
    form_fields['target_collection'].custom_widget = UberSelectionWidget
    label = _(u"Edit Search Portlet")
    description = _(u"This portlet shows a search box.")


#from zope.interface import implements

#from plone.portlets.interfaces import IPortletDataProvider
#from plone.app.portlets.portlets import base

#from zope import schema
#from zope.formlib import form
#from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

#from collective.portlet.contentsearch import ContentSearchPortletMessageFactory as _


#class IContentSearchPortlet(IPortletDataProvider):
#    """A portlet

#    It inherits from IPortletDataProvider because for this portlet, the
#    data that is being rendered and the portlet assignment itself are the
#    same.
#    """

#    # TODO: Add any zope.schema fields here to capture portlet configuration
#    # information. Alternatively, if there are no settings, leave this as an
#    # empty interface - see also notes around the add form and edit form
#    # below.

#    # some_field = schema.TextLine(title=_(u"Some field"),
#    #                              description=_(u"A field to use"),
#    #                              required=True)


#class Assignment(base.Assignment):
#    """Portlet assignment.

#    This is what is actually managed through the portlets UI and associated
#    with columns.
#    """

#    implements(IContentSearchPortlet)

#    # TODO: Set default values for the configurable parameters here

#    # some_field = u""

#    # TODO: Add keyword parameters for configurable parameters here
#    # def __init__(self, some_field=u""):
#    #    self.some_field = some_field

#    def __init__(self):
#        pass

#    @property
#    def title(self):
#        """This property is used to give the title of the portlet in the
#        "manage portlets" screen.
#        """
#        return "Content Search Portlet"


#class Renderer(base.Renderer):
#    """Portlet renderer.

#    This is registered in configure.zcml. The referenced page template is
#    rendered, and the implicit variable 'view' will refer to an instance
#    of this class. Other methods can be added and referenced in the template.
#    """

#    render = ViewPageTemplateFile('contentsearchportlet.pt')


#class AddForm(base.AddForm):
#    """Portlet add form.

#    This is registered in configure.zcml. The form_fields variable tells
#    zope.formlib which fields to display. The create() method actually
#    constructs the assignment that is being added.
#    """
#    form_fields = form.Fields(IContentSearchPortlet)

#    def create(self, data):
#        return Assignment(**data)


## NOTE: If this portlet does not have any configurable parameters, you
## can use the next AddForm implementation instead of the previous.

## class AddForm(base.NullAddForm):
##     """Portlet add form.
##     """
##     def create(self):
##         return Assignment()


## NOTE: If this portlet does not have any configurable parameters, you
## can remove the EditForm class definition and delete the editview
## attribute from the <plone:portlet /> registration in configure.zcml


#class EditForm(base.EditForm):
#    """Portlet edit form.

#    This is registered with configure.zcml. The form_fields variable tells
#    zope.formlib which fields to display.
#    """
#    form_fields = form.Fields(IContentSearchPortlet)
