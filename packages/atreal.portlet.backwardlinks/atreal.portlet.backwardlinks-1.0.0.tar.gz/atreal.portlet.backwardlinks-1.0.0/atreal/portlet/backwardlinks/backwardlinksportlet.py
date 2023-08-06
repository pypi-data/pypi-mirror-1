from zope.interface import implements
from ZTUtils import make_query

from Products.CMFCore.utils import getToolByName

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.app.portlets.cache import render_cachekey
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize

from zope import schema
from zope.formlib import form
from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from atreal.portlet.backwardlinks import BackwardLinksPortletMessageFactory as _

DEFAULT_ALLOWED_TYPES = (
    'News Item',
    'Document',
    'Event',
)

class IBackwardLinksPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """
    user_title= schema.TextLine(
        title=_(u'Portlet title'),
        description=_(u'The title that will be displayed to the users.'),
        default=_(u'Backward links'),
        required=False,
    )
    count = schema.Int(
        title=_(u'Number of items to display'),
        description=_(u'How many related items to list.'),
        required=True,
        default=10
    )

    states = schema.Tuple(
        title=_(u"Workflow state"),
        description=_(u"Items in which workflow state to show."),
        default=('published', ),
        required=True,
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.WorkflowStates"
        )
    )

    allowed_types = schema.Tuple(
        title=_(u"Allowed Types"),
        description=_(u"Select the targeted content types."),
        default=DEFAULT_ALLOWED_TYPES,
        required=True,
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes"
        )
    )
    
    show_more_link = schema.Bool(
        title=_(u"Show the 'More...' link"),
        description=_(u"If selected, the 'More...' link at the bottom of the "
                       "portlet will be displayed."),
        default=True,
    )


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IBackwardLinksPortlet)

    def __init__(self,
                 user_title=_(u'Backward links'),
                 count=5,
                 states=('published',),
                 allowed_types=DEFAULT_ALLOWED_TYPES,
                 show_more_link=True):
        self.user_title=user_title
        self.count = count
        self.states = states
        self.allowed_types = allowed_types
        self.show_more_link=show_more_link


    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return self.user_title 


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    _template = ViewPageTemplateFile('backwardlinksportlet.pt')

    @ram.cache(render_cachekey)
    def render(self):
        """ We cache the rendered html """
        return xhtml_compress(self._template())


    @property
    def available(self):
        """ Shall we display the portlet ? """
        if self.context.portal_type == 'Plone Site':
            return False
        else:
            return len(self._data())


    def getTitle(self):
        """ """
        return self.data.user_title or _(u'Backward links')
    

    def getBackwardLinks(self):
        """ Return the data """
        return self._data()


    def showMoreLink(self):
        """ Do we have to display the 'More...' link """
        return self.data.show_more_link


    def getAllBackwardLinks(self):
        """ """
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal_url = portal_state.portal_url()        
        return '%s/search?%s' % (portal_url, make_query(self._buildQuery()))
    
    
    @memoize
    def _data(self):
        """ Compute the links to display """
        pc = getToolByName(self.context, 'portal_catalog')
        query = self._buildQuery()
        catbrains = pc(query)
        return catbrains
    

    def _buildQuery(self):
        """ """
        refc = getToolByName(self.context, 'reference_catalog')
        refbrains = refc(relationship='isReferencing',
                         targetUID=self.context.UID())
        query = dict(UID=[brain.sourceUID for brain in refbrains
                          if brain.sourceUID != self.context.UID()],
                     review_state=list(self.data.states),
                     portal_type=list(self.data.allowed_types),)
        return query


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IBackwardLinksPortlet)

    label = _(u"Add Backward Links Portlet")
    description = _(u"This portlet displays backward links.")

    def create(self, data):
        return Assignment(**data)



class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IBackwardLinksPortlet)
    label = _(u"Edit Backward Links Portlet")
    description = _(u"This portlet displays backward links.")
  

