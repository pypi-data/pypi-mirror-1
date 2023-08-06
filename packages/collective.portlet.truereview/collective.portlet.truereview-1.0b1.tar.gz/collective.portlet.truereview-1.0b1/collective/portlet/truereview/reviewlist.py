from zope.component import getMultiAdapter, getUtility

from plone.i18n.normalizer.interfaces import IIDNormalizer

from Acquisition import aq_inner
from AccessControl import getSecurityManager

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import Batch

class ReviewListView(BrowserView):
    """The review list
    """

    def __init__(self, context, request):
        super(ReviewListView, self).__init__(context, request)
        self.request.set('disable_border', True)

    def review_list(self, states=None, types=None, sort_limit=None, batch=False):
        """Get the review list items.
        """
        
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')

        if not states:
            states = self.request.get('states', ('pending',))
        if not types:
            types = self.request.get('types', ())

        plone_view = getMultiAdapter((context, self.request), name=u'plone')
        getIcon = plone_view.getIcon
        toLocalizedTime = plone_view.toLocalizedTime

        idnormalizer = getUtility(IIDNormalizer)
        norm = idnormalizer.normalize
        items = []
        
        user = getSecurityManager().getUser()
        query = dict(sort_on='modified',
                     reviewerRolesAndUsers=catalog._listAllowedRolesAndUsers(user))
        
        if not batch and sort_limit:
            query['sort_limit']= sort_limit
        
        if types:
            query['portal_type'] = types
            
        if states:
            query['review_state'] = states
        
        for brain in catalog(**query):
            items.append(dict(
                url = brain.getURL(),
                title = brain.Title,
                description = brain.Description,
                portal_type = brain.portal_type,
                portal_type_class = 'contenttype-%s' % norm(brain.portal_type),
                icon = getIcon(brain).html_tag(),
                creator = brain.Creator,
                review_state = brain.review_state,
                review_state_class = 'state-%s ' % norm(brain.review_state),
                mod_date = toLocalizedTime(brain.ModificationDate),
            ))
        
        if batch:
            b_start = self.request.get('b_start', 0)
            items = Batch(items, sort_limit, int(b_start), orphan=0)
        
        return items