##############################################################################
#
# Copyright (c) 2002-2009 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" JRedirector main module

$Id: JRedirector.py 1810 2009-06-23 10:57:31Z jens $
"""

import os
import time

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import manage_properties
from AccessControl.Permissions import view_management_screens
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from App.class_init import default__class_init__ as InitializeClass
from App.Common import package_home
from App.special_dtml import DTMLFile
from BTrees.OOBTree import OOBTree
from DateTime.DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from Globals import PersistentMapping
from zope.interface import implements

from Products.JRedirector.interfaces import IJRedirector

_dtmldir = os.path.join(package_home(globals()), 'dtml')
addJRedirectorForm = DTMLFile('add', _dtmldir)


class JRedirector(SimpleItem):
    """ JRedirector 
    """
    security = ClassSecurityInfo()
    meta_type = 'JRedirector'
    implements(IJRedirector)

    manage_log = DTMLFile('dtml/log', globals())
    manage_map = DTMLFile('dtml/mappings', globals())
    manage_settings = DTMLFile('dtml/settings', globals())
    manage = manage_main = manage_settings
    manage_main._setName('manage_main')
    manage_settings._setName('manage_settings')

    manage_options = ( 
                ( { 'label' : 'Properties', 'action' : 'manage_settings',
                    'help' : ('JRedirector', 'Properties.stx') }
                , { 'label' : 'Mappings', 'action' : 'manage_map',
                    'help' : ('JRedirector', 'Mappings.stx') }
                , { 'label' : 'Log', 'action' : 'manage_log',
                    'help' : ('JRedirector', 'Log.stx') }
                )
                + SimpleItem.manage_options
    )


    def __init__(self, id, title='', default_redirect='', loglevel=3):
        self.id = id
        self.title = title
        self._default_redirect = default_redirect
        self._redirects = PersistentMapping()
        self._log = OOBTree()
        self._loglevel = int(loglevel)


    security.declarePrivate('_getRedirectData')
    def _getRedirectData(self, REQUEST):
        """ Get the redirect URL and log 
        """
        wildcard_match = 0
        server_url = REQUEST.get('SERVER_URL')
        referrer = REQUEST.get('HTTP_REFERER', '').strip() or 'n/a'
        full_url = REQUEST.get('PATH_INFO')

        if ( full_url.find('VirtualHostBase') != -1 or
             full_url.find('VirtualHostRoot') != -1 ):
            full_url = REQUEST.get('URL')
            trp = list(REQUEST.get('TraversalRequestNameStack'))
            vpp = REQUEST.get('VirtualRootPhysicalPath')

            if len(trp) > 0:
                trp.reverse()
                full_url = '%s/%s' % (full_url, '/'.join(trp))

            nonvirtual_path = full_url.replace(server_url, '')
            old_path = '%s%s' % ('/'.join(vpp), nonvirtual_path)
        else:
            old_path = full_url.replace(server_url, '')

        redir_handled = self._redirects.has_key(old_path)

        if not redir_handled:
            # Test if this path is to be handled case-insensitively
            lc_old_path = old_path.lower()
            if ( self._redirects.has_key(lc_old_path) and
                 self._redirects[lc_old_path].get('case_insensitive', None) ):
                redir_handled = 1
                old_path = lc_old_path

        if not redir_handled:
            # Last resort: does one of the wildcards match?
            filt = lambda x: x[1].get('is_wildcard', None) and x[0] or None
            wildcards = filter(None, map(filt, self._redirects.items()))
            for wildcard in wildcards:
                wc_dict = self._redirects.get(wildcard)
                if wc_dict.get('case_insensitive', None):
                    test_against = old_path.lower()
                else:
                    test_against = old_path

                if test_against.find(wildcard) != -1:
                    old_path = wildcard
                    redir_handled = 1
                    wildcard_match = 1
                    break

        ll = getattr(self, '_loglevel', 3)
        if ( ll == 3 or 
             (ll == 1 and redir_handled == 0) or 
             (ll == 2 and redir_handled == 1) ):
            log = self._getLogStore()
            redir_rec = log.get(old_path, {})
            redir_count = redir_rec.get('total_count', 0)
            refs = redir_rec.get('referrers', [])
            if referrer not in refs:
                refs.append(referrer)

            get_transaction().abort()
            log[old_path] = { 'total_count' : redir_count + 1
                            , 'last_access' : time.time()
                            , 'redirected' : redir_handled
                            , 'wildcard_match' : wildcard_match
                            , 'referrers' : refs
                            }
            get_transaction().note('JRedirector redirected %s' % old_path)
            get_transaction().commit()

        return self._redirects.get(old_path)


    security.declarePublic('redirect')
    def redirect(self, REQUEST):
        """ Handle a redirect for a given URL 
        """
        redir_data = self._getRedirectData(REQUEST)

        if redir_data:
            redir_path = redir_data.get('redir_path', self._default_redirect)
            redir_status = redir_data.get('redir_status', '301')

            REQUEST.RESPONSE.redirect( redir_path
                                     , status=int(redir_status)
                                     , lock=1
                                     )

    __call__ = redirect


    security.declarePublic('getRedirectURL')
    def getRedirectURL(self, REQUEST):
        """ Get URL and status for a redirect 
        """
        redir_path = ''
        redir_status = ''

        redir_data = self._getRedirectData(REQUEST)

        if redir_data:
            redir_path = redir_data.get('redir_path', self._default_redirect)
            redir_status = redir_data.get('redir_status', '301')

        return redir_path, redir_status


    security.declareProtected(manage_properties, 'manage_edit')
    def manage_edit( self
                   , title=''
                   , default_redirect=''
                   , loglevel=3
                   , REQUEST=None
                   ):
        """ Edit the JRedirector folder properties 
        """
        self.title = title
        self._default_redirect = default_redirect
        self._loglevel = int(loglevel)

        if REQUEST is not None:
            msg = 'Properties changed.'
            return self.manage_settings(manage_tabs_message=msg)


    security.declareProtected(view_management_screens, 'getLoglevel')
    def getLoglevel(self):
        """ Return the level of logging 
        """
        return getattr(self, '_loglevel', 3)


    security.declareProtected(view_management_screens, 'getMappings')
    def getMappings(self):
        """ Return the existing mappings 
        """
        return self._redirects.items()


    security.declareProtected(view_management_screens, 'getMapping')
    def getMapping(self, old_url):
        """ Return a specific mapping 
        """
        return self._redirects.get(old_url, {})


    security.declarePrivate('_getLogStore')
    def _getLogStore(self):
        """ Indirection to allow flexibility in backend stores 
        """
        cur_log = self._log

        if not isinstance(cur_log, OOBTree):
            self._log = OOBTree()

            for key, value in cur_log.items():
                self._log[key] = value

            cur_log = self._log

        return cur_log


    security.declareProtected(view_management_screens, 'getLog')
    def getLog(self):
        """ Return the log 
        """
        log = self._getLogStore()
        log_items = list(log.items())
        sort_f = lambda a, b: cmp(b[1]['total_count'], a[1]['total_count'])
        log_items.sort(sort_f)
        
        return log_items


    security.declareProtected(view_management_screens, 'clearLog')
    def clearLog(self, REQUEST=None):
        """ Clear out the log 
        """
        self._getLogStore().clear()

        if REQUEST is not None:
            msg = 'Log cleared'
            return self.manage_log(manage_tabs_message=msg)


    security.declareProtected(view_management_screens, 'getDefaultRedirect')
    def getDefaultRedirect(self):
        """ Return the default redirect path value 
        """
        return self._default_redirect


    security.declareProtected(manage_properties, 'addRedirectorMapping')
    def addRedirectorMapping( self
                            , old_path
                            , new_path
                            , redir_status='301'
                            , case_insensitive=0
                            , is_wildcard=0
                            , REQUEST=None 
                            ):
        """ Add a new redirector mapping 
        """
        if old_path.endswith('/'):
            old_path = old_path[:-1]

        if case_insensitive:
            old_path = old_path.lower()

        self._redirects[old_path] = { 'redir_path' : new_path
                                    , 'redir_status' : redir_status
                                    , 'case_insensitive' : case_insensitive
                                    , 'is_wildcard' : is_wildcard
                                    }

        if REQUEST is not None:
            msg = 'Mapping added'
            return self.manage_map(manage_tabs_message=msg)
    

    security.declareProtected(manage_properties, 'deleteRedirectorMappings')
    def deleteRedirectorMappings(self, old_paths, REQUEST=None):
        """ Delete a redirector mapping 
        """
        for old_path in old_paths:
            if self._redirects.has_key(old_path):
                del self._redirects[old_path]

        if REQUEST is not None:
            msg = 'Mapping deleted'
            return self.manage_map(manage_tabs_message=msg)


def manage_addJRedirector( self
                         , id
                         , title=''
                         , default_redirect=''
                         , loglevel=3
                         , REQUEST=None 
                         ):
    """ Called by Zope if you create a JRedirector from the ZMI 
    """
    container = self.this()

    if getattr(aq_base(container), id, None) is not None:
        msg = 'Object already contains an item with id %s' % id
    else:
        jr = JRedirector(id, title, default_redirect, loglevel)
        container._setObject(jr.getId(), jr)
        msg = 'Added JRedirector'

    if REQUEST is not None:
        goto = container.absolute_url()
        qs = 'manage_tabs_message=%s' % msg
        REQUEST.RESPONSE.redirect('%s/manage_main?%s' % (goto, qs))
        

InitializeClass(JRedirector)

