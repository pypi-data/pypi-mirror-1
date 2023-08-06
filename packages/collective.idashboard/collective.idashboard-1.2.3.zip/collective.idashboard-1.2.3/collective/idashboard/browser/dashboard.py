# Licensed under GNU General Public License (GPL)
# http://www.opensource.org/licenses/gpl-license.php

import logging
import sys

from Acquisition import aq_acquire, aq_inner
from ZODB.POSException import ConflictError

from zope.component import adapts
from zope.component import getUtility, getMultiAdapter
from zope.component import queryUtility, queryMultiAdapter 
from zope.exceptions.interfaces import DuplicationError
from zope.interface import Interface
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserView

from plone.app.kss.interfaces import IPloneKSSView
from plone.app.kss.plonekssview import PloneKSSView
from plone.app.portlets.browser.editmanager import EditPortletManagerRenderer
from plone.app.portlets.browser.interfaces import IManageDashboardPortletsView
from plone.app.portlets.interfaces import IDashboard
from plone.app.portlets.interfaces import IPortletPermissionChecker
from plone.app.portlets.manager import ColumnPortletManagerRenderer
from plone.app.portlets.utils import assignment_mapping_from_key
from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
from plone.portlets.interfaces import IPortletManager, IPortletRenderer
from plone.portlets.utils import hashPortletInfo
from plone.portlets.utils import unhashPortletInfo

from kss.core import force_unicode

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.idashboard.interfaces import IIDashboardLayer

log = logging.getLogger('collective.idashboard/browser/dashboard.py')

class DashboardPortletManagerRenderer(ColumnPortletManagerRenderer):
    """ Render a column of the dashboard
    """
    adapts(Interface, IIDashboardLayer, IBrowserView, IDashboard)
    template = ViewPageTemplateFile('templates/dashboard-column.pt')

    def normalized_manager_name(self):
        return self.manager.__name__.replace('.', '-')

    def manager_name(self):
        return self.manager.__name__


class DashboardEditPortletManagerRenderer(EditPortletManagerRenderer):
    """Render a portlet manager in edit mode for the dashboard
    """
    adapts(Interface, IIDashboardLayer, IManageDashboardPortletsView, IDashboard)
    error_message = ViewPageTemplateFile('templates/error_message.pt')

    def __init__(self, context, request, view, manager):
        EditPortletManagerRenderer.__init__(self, context, request, view, manager)
        self.template = ViewPageTemplateFile('templates/dashboard-edit-manager.pt')

    def manager_name(self):
        return self.manager.__name__

    def safe_render(self, portlet_renderer):
        try:
            return portlet_renderer.render()
        except ConflictError:
            raise
        except Exception:
            log.exception('Error while rendering %r' % (self,))
            aq_acquire(self, 'error_log').raising(sys.exc_info())
            return self.error_message()

    def portlets(self):
        context  = self.context
        request = self.request
        baseUrl = self.baseUrl()
        assignments = self._lazyLoadAssignments(self.manager)
        data = []
        manager_name = self.manager.__name__
        category = self.__parent__.category
        key = self.__parent__.key
        for idx in range(len(assignments)):
            name = assignments[idx].__name__
            editview = queryMultiAdapter((assignments[idx], self.request), 
                                          name='edit', 
                                          default=None
                                        )
            if editview is None:
                editviewName = ''
            else:
                editviewName = '%s/%s/edit' % (baseUrl, name)
            
            portlet_hash = hashPortletInfo(dict(manager=manager_name, 
                                                category=category, 
                                                key=key, name=name,
                                                )
                                            )
            portal = context.portal_url.getPortalObject()
            manager = getUtility(IPortletManager, name=manager_name, context=portal)
            view = portal.restrictedTraverse('@@plone')
            manager = getUtility(IPortletManager, name=manager_name)
            renderer = getMultiAdapter((context, 
                                        request, 
                                        view, 
                                        manager, 
                                        assignments[idx]), 
                                        IPortletRenderer
                                      )
            renderer.update()
            data.append( {'title'      : assignments[idx].title,
                          'manager'    : manager_name,
                          'name'       : name,
                          'key'        : key,
                          'editview'   : editviewName,
                          'hash'       : portlet_hash,
                          'renderer'   : renderer.__of__(self.context),
                          'up_url'     : '%s/@@move-portlet-up?name=%s' % (baseUrl, name),
                          'down_url'   : '%s/@@move-portlet-down?name=%s' % (baseUrl, name),
                          'delete_url' : '%s/@@delete-portlet?name=%s' % (baseUrl, name),
                          })
        if len(data) > 0:
            data[0]['up_url'] = data[-1]['down_url'] = None
        return data


class KSSViewMixin(PloneKSSView):
    implements(IPloneKSSView)

    def macroContent(self, macropath, **kw):
        """ Renders a macro and returns its text 
            Customization of plone/app/kss/plonekssview.py macroContent to allow
            browser view template macros to be rendered as well.
        """
        path = macropath.split('/')
        if len(path) < 2 or path[-2] != 'macros':
            raise RuntimeError, 'Path must end with macros/name_of_macro (%s)' % (repr(macropath), )
        # needs string, do not tolerate unicode (causes but at traverse)
        jointpath = '/'.join(path[:-2]).encode('ascii')
        macroobj = self.context.restrictedTraverse(jointpath)
        try:
            the_macro = macroobj.macros[path[-1]]
        except  AttributeError:
            # XXX: Customization, the only way I could get macros 
            # of browser templates to render. - JC Brand
            the_macro = macroobj.index.macros[path[-1]]
        except IndexError:
            raise RuntimeError, 'Macro not found'

        # put parameters on the request, by saving the original context
        self.request.form, orig_form = kw, self.request.form
        content = self.header_macros.__of__(macroobj.aq_parent)(the_macro=the_macro)
        self.request.form = orig_form
        # Always encoded as utf-8
        content = force_unicode(content, 'utf')
        return content


class DashboardAjax(KSSViewMixin):

    def getCharset(self):
        """ Returns the site default charset, or utf-8.
        """
        properties = getToolByName(self, 'portal_properties', None)
        if properties is not None:
            site_properties = getattr(properties, 'site_properties', None)
            if site_properties is not None:
                return site_properties.getProperty('default_charset')
        return 'utf-8'


    def generateNewId(self, title):
        """ Suggest an id for this object.
        """
        if not isinstance(title, unicode):
            charset = self.getCharset()
            title = unicode(title, charset)

        request = self.context.request 
        if request is not None:
            return IUserPreferredURLNormalizer(request).normalize(title)

        return queryUtility(IURLNormalizer).normalize(title)


    def movePortlet(self, portlethash, manager, prev_id):
        """ """
        context = self.context
        info = unhashPortletInfo(portlethash)
        new_assignment_map = assignment_mapping_from_key(
                self.context, manager, info['category'], info['key'], create=True,
                )
        IPortletPermissionChecker(new_assignment_map.__of__(aq_inner(self.context)))()
        keys = list(new_assignment_map.keys())
        # Calculate the position of the portlet
        if (prev_id):
            prev_hash = prev_id.split('-')[-1]
            prev_name = unhashPortletInfo(prev_hash)['name']
            new_index = keys.index(prev_name)+1
        else:
            new_index = 0

        name = info['name']
        if info['manager'] != manager:
            # Remove form old assignments and add to new
            old_assignment_map = assignment_mapping_from_key(
                    self.context, info['manager'], info['category'], info['key']
                    )
            title = old_assignment_map[name].title
            nrm_title = self.generateNewId(title)
            new_name = nrm_title or name 
            idx = 1
            while True:
                try:
                    new_assignment_map[new_name] = old_assignment_map[name]
                    break
                except DuplicationError:
                    new_name = "%s-%d" % (nrm_title, idx)
                    idx += 1

            keys = list(new_assignment_map.keys())
            old_index = keys.index(new_name)
            del keys[old_index]
            keys.insert(new_index, new_name)
            del old_assignment_map[name]
        else:
            old_index = keys.index(name)
            keys[old_index] = 'dummy'
            keys.insert(new_index, name)
            del keys[keys.index('dummy')]
            new_name = name 

        new_assignment_map.updateOrder(keys)
        info['manager'] = manager
        info['name'] = new_name 
        return hashPortletInfo(info)

    def removePortlet(self, portlethash):
        """ """
        info = unhashPortletInfo(portlethash)
        portlets = assignment_mapping_from_key(
                self.context, info['manager'], info['category'], info['key']
                )
        del portlets[info['name']]

        
    def configurePortlet(self, portlethash): 
        """ """
        context = self.context
        request = context.request
        info = unhashPortletInfo(portlethash)
        portal = context.portal_url.getPortalObject()
        mapping = portal.restrictedTraverse(
                        '++dashboard++%s+%s' % (info['manager'], info['key']))

        assignment = portal.restrictedTraverse(
                        '++dashboard++%s+%s/%s' % (info['manager'], 
                                                   info['key'], 
                                                   info['name']))

        assignment = assignment.__of__(mapping)
        assignment.request.URL = '%s/++dashboard++%s+%s/%s/edit' % (
                                                   portal.absolute_url(),
                                                   info['manager'], 
                                                   info['key'], 
                                                   info['name'])
        assignment.request.set('portlethash', portlethash)
        editform = assignment.restrictedTraverse('edit')
        editform.request.set('portlethash', portlethash)
        return self._render_portlet_edit_form(info, editform)


    def savePortletConfiguration(self, **kwargs):
        """ """
        context = self.context
        request = context.request
        portal = context.portal_url.getPortalObject()
        portlethash = request.get('portlethash')
        info = unhashPortletInfo(portlethash)
        mapping = context.restrictedTraverse(
                        '++dashboard++%s+%s' % (info['manager'], info['key']))

        assignment = context.restrictedTraverse(
                        '++dashboard++%s+%s/%s' % (info['manager'], 
                                                   info['key'], 
                                                   info['name']))

        assignment = assignment.__of__(mapping)
        editform = assignment.restrictedTraverse('edit')
        # Hack to make zope.formlib.form.handleSubmit work, the button must be
        # submitted.
        for action in editform.actions:
            if action.label == u'label_save':
                action.form.request.form[action.__name__] = 1

        editform.update()
        # Remove browser 302 redirect added during update.
        editform.request.response.setStatus('200')
        editform.request.response.setHeader('Location', None)

        if editform.errors:
            return self._render_portlet_edit_form(info, 
                                                  editform, 
                                                  editform.errors
                                                  )
        return self._render_portlet_view(info, assignment)


    def cancelPortletConfiguration(self, portlethash):
        """ """
        info = unhashPortletInfo(portlethash)
        assignments = assignment_mapping_from_key(
                self.context, info['manager'], info['category'], info['key']
                )
        assignment = assignments[info['name']]
        return self._render_portlet_view(info, assignment)


    def _render_portlet_view(self, info, assignment):
        """ """
        portal = self.context.portal_url.getPortalObject()
        manager = getUtility(IPortletManager, name=info['manager'], context=portal)
        view = portal.restrictedTraverse('@@plone')
        renderer = getMultiAdapter((self.context, 
                                    self.context.request, 
                                    view, 
                                    manager, 
                                    assignment), 
                                    IPortletRenderer
                                   )
        html = renderer.__of__(portal).render()
        portlethash = self.request.form.get('portlethash')
        kw = { 'portlethash': portlethash,
               'portlethtml-%s' % str(portlethash): html, 
             }
        return self.macroContent('@@dashboard-macros/macros/portlet-manage-view', **kw)


    def _render_portlet_edit_form(self, info, view, errors={}):
        """ """
        context = aq_inner(self.context)
        request = context.REQUEST

        view.template = \
            ViewPageTemplateFile('templates/customize_portlet.pt')
        html = view()

        portlethash = self.request.form.get('portlethash')
        kw = { 'portlethash': portlethash,
               'portlethtml-%s' % str(portlethash): html, 
             }
        return self.macroContent('@@dashboard-macros/macros/portlet-edit', **kw)


