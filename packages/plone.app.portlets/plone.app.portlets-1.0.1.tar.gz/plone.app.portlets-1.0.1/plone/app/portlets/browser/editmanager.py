import urllib

from Acquisition import Explicit, aq_parent, aq_inner
from ZODB.POSException import ConflictError

from zope.interface import implements, Interface
from zope.component import adapts, getMultiAdapter, queryMultiAdapter, getUtilitiesFor

from zope.annotation.interfaces import IAnnotations

from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from zope.contentprovider.interfaces import UpdateNotCalled

from plone.memoize.view import memoize

from plone.portlets.interfaces import IPortletRetriever
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import ILocalPortletAssignmentManager

from plone.portlets.constants import CONTEXT_ASSIGNMENT_KEY

from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import CONTENT_TYPE_CATEGORY

from plone.app.portlets.interfaces import IDashboard, IPortletPermissionChecker

from plone.app.portlets.browser.interfaces import IManageColumnPortletsView
from plone.app.portlets.browser.interfaces import IManageContextualPortletsView
from plone.app.portlets.browser.interfaces import IManageDashboardPortletsView

from Products.Five.browser import BrowserView 
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.portlets.utils import hashPortletInfo

class EditPortletManagerRenderer(Explicit):
    """Render a portlet manager in edit mode.
    
    This is the generic renderer, which delegates to the view to determine
    which assignments to display.
    """
    implements(IPortletManagerRenderer)
    adapts(Interface, IDefaultBrowserLayer, IManageColumnPortletsView, IPortletManager)

    def __init__(self, context, request, view, manager):
        self.__parent__ = view
        self.manager = manager # part of interface
        self.context = context
        self.request = request
        self.template = ViewPageTemplateFile('templates/edit-manager.pt')
        self.__updated = False
        
    @property
    def visible(self):
        return True

    def filter(self, portlets):
        return portlets

    def update(self):
        self.__updated = True

    def render(self):
        if not self.__updated:
            raise UpdateNotCalled
        return self.template()
    
    # Used by the view template

    def normalized_manager_name(self):
        return self.manager.__name__.replace('.', '-')

    def baseUrl(self):
        return self.__parent__.getAssignmentMappingUrl(self.manager)

    def portlets(self):
        baseUrl = self.baseUrl()
        assignments = self._lazyLoadAssignments(self.manager)
        data = []
        
        manager_name = self.manager.__name__
        category = self.__parent__.category
        key = self.__parent__.key
        
        for idx in range(len(assignments)):
            name = assignments[idx].__name__
            
            editview = queryMultiAdapter((assignments[idx], self.request), name='edit', default=None)
            if editview is None:
                editviewName = ''
            else:
                editviewName = '%s/%s/edit' % (baseUrl, name)
            
            portlet_hash = hashPortletInfo(dict(manager=manager_name, category=category, 
                                                key=key, name=name,))
            
            data.append( {'title'      : assignments[idx].title,
                          'editview'   : editviewName,
                          'hash'       : portlet_hash,
                          'up_url'     : '%s/@@move-portlet-up?name=%s' % (baseUrl, name),
                          'down_url'   : '%s/@@move-portlet-down?name=%s' % (baseUrl, name),
                          'delete_url' : '%s/@@delete-portlet?name=%s' % (baseUrl, name),
                          })
        if len(data) > 0:
            data[0]['up_url'] = data[-1]['down_url'] = None
        return data
        
    def addable_portlets(self):
        baseUrl = self.baseUrl()
        addviewbase = baseUrl.replace(self.context.absolute_url(), '')
        return [ {'title' : p.title,
                  'description' : p.description,
                  'addview' : '%s/+/%s' % (addviewbase, p.addview)
                  } for p in self.manager.getAddablePortletTypes()]
        
    @memoize
    def referer(self):
        view_name = self.request.get('viewname', None)
        key = self.request.get('key', None)
        base_url = self.request['ACTUAL_URL']
        
        if view_name:
            base_url = self.context.absolute_url() + '/' + view_name
        
        if key:
            base_url += '?key=%s' % key
        
        return base_url
        
    # See note in plone.portlets.manager
    
    @memoize    
    def _lazyLoadAssignments(self, manager):
        return self.__parent__.getAssignmentsForManager(manager)
    
          
class ContextualEditPortletManagerRenderer(EditPortletManagerRenderer):
    """Render a portlet manager in edit mode for contextual portlets
    """
    adapts(Interface, IDefaultBrowserLayer, IManageContextualPortletsView, IPortletManager)

    def __init__(self, context, request, view, manager):
        EditPortletManagerRenderer.__init__(self, context, request, view, manager)
        self.template = ViewPageTemplateFile('templates/edit-manager-contextual.pt')
    
    def blacklist_status_action(self):
        baseUrl = str(getMultiAdapter((self.context, self.request), name='absolute_url'))
        return baseUrl + '/@@set-portlet-blacklist-status'
    
    def manager_name(self):
        return self.manager.__name__
    
    def context_blacklist_status(self):
        assignable = getMultiAdapter((self.context, self.manager,), ILocalPortletAssignmentManager)
        return assignable.getBlacklistStatus(CONTEXT_CATEGORY)

    def group_blacklist_status(self):
        assignable = getMultiAdapter((self.context, self.manager,), ILocalPortletAssignmentManager)
        return assignable.getBlacklistStatus(GROUP_CATEGORY)
    
    def content_type_blacklist_status(self):
        assignable = getMultiAdapter((self.context, self.manager,), ILocalPortletAssignmentManager)
        return assignable.getBlacklistStatus(CONTENT_TYPE_CATEGORY)
  
class DashboardEditPortletManagerRenderer(EditPortletManagerRenderer):
    """Render a portlet manager in edit mode for the dashboard
    """
    adapts(Interface, IDefaultBrowserLayer, IManageDashboardPortletsView, IDashboard)
        
class ManagePortletAssignments(BrowserView):
    """Utility views for managing portlets for a particular column
    """
    
    # view @@move-portlet-up
    def move_portlet_up(self, name):
        assignments = aq_inner(self.context)
        IPortletPermissionChecker(assignments)()
        
        keys = list(assignments.keys())
        
        idx = keys.index(name)
        keys.remove(name)
        keys.insert(idx-1, name)
        assignments.updateOrder(keys)
        
        self.request.response.redirect(self._nextUrl())
        return ''
    
    # view @@move-portlet-down
    def move_portlet_down(self, name):
        assignments = aq_inner(self.context)
        IPortletPermissionChecker(assignments)()
        
        keys = list(assignments.keys())
        
        idx = keys.index(name)
        keys.remove(name)
        keys.insert(idx+1, name)
        assignments.updateOrder(keys)
        
        self.request.response.redirect(self._nextUrl())
        return ''
    
    # view @@delete-portlet
    def delete_portlet(self, name):
        assignments = aq_inner(self.context)
        IPortletPermissionChecker(assignments)()
        del assignments[name]
        self.request.response.redirect(self._nextUrl())
        return ''
        
    def _nextUrl(self):
        referer = self.request.get('referer')
        if not referer:
            context = aq_parent(aq_inner(self.context))
            url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))    
            referer = '%s/@@manage-portlets' % (url,)
        return referer