from zope.interface import implements
from zope.component import getMultiAdapter

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.memoize.instance import memoize

from collective.portlet.truereview import TrueReviewMessageFactory as _

from Acquisition import aq_inner

class ITrueReview(IPortletDataProvider):
    """A review portlet that only shows items for which the current user
    the "review portal content" permission. Also allows limiting by content
    type and state.
    """
    
    states = schema.Tuple(title=_(u"Workflow state"),
                          description=_(u"Items in which workflow state to show. "
                                         "Leave blank for any state."),
                          default=('pending', ),
                          required=False,
                          value_type=schema.Choice(
                              vocabulary="plone.app.vocabularies.WorkflowStates")
                          )
    
    types = schema.Tuple(title=_(u"Content types"),
                         description=_(u"Content types to show. Leave blank for any."),
                         default=(),
                         required=False,
                         value_type=schema.Choice(
                             vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes")
                         )

    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list.'),
                       required=True,
                       default=5,
                       min=0)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ITrueReview)

    states = ('pending',)
    types = ()
    count = 5
    
    def __init__(self, states=('pending',), types=(), count=5):
        self.states = states
        self.types = types
        self.count = count

    @property
    def title(self):
        return _(u"Review list")


class Renderer(base.Renderer):
    """Render the portlet
    """

    render = ViewPageTemplateFile('truereview.pt')

    @property
    def anonymous(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        return portal_state.anonymous()

    @property
    def available(self):
        return len(self._data()) > 0

    def review_items(self):
        return self._data()

    @memoize
    def _data(self):
        if self.anonymous:
            return []
        
        view = getMultiAdapter((self.context, self.request), name=u"true_review_list")
        return view.review_list(states=self.data.states,
                                types=self.data.types,
                                sort_limit=self.data.count)

class AddForm(base.AddForm):
    """Portlet add form.
    """
    form_fields = form.Fields(ITrueReview)
    label = _(u"Add Review Portlet")
    description = _(u"This portlet displays a queue of documents awaiting review.")
    
    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.
    """
    form_fields = form.Fields(ITrueReview)
    label = _(u"Edit Review Portlet")
    description = _(u"This portlet displays a queue of documents awaiting review.")