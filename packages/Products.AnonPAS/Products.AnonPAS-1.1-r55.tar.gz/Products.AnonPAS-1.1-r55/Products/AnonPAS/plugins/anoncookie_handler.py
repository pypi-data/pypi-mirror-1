""" Class: AnonCookiePlugin

This hacked PlonePAS collection of plugins was mostly ripped
from other plugins, especially from CookieAuthHelper
It gives anonymous users an automatic userid + roles
so this plugin can be used for anonymous content submission

$Id: anoncookie_handler.py,v 1.1 2007-12-11 16:00:00 bouma Exp $
"""

import md5
import random
from AccessControl.SecurityManagement import getSecurityManager
from base64 import encodestring, decodestring
from urllib import quote, unquote
from Acquisition import aq_base
from AccessControl.SecurityInfo import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile
from Products.PluggableAuthService.plugins.CookieAuthHelper \
    import CookieAuthHelper as BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.authservice \
        import IPluggableAuthService
from Products.PluggableAuthService.interfaces.plugins import \
        IRolesPlugin, IExtractionPlugin, IAuthenticationPlugin, \
        IPropertiesPlugin, IUserEnumerationPlugin

from Products.CMFPlone.utils import log
from Products.AnonPAS.config import *

# This hacked PlonePAS collection of plugins was mostly ripped
# from other plugins, especially from CookieAuthHelper

def manage_addAnonCookiePlugin (self, id, title='',
                                RESPONSE=None, **kw):
    """Create an instance of a anon cookie helper.
    """

    self = self.this()

    o = AnonCookiePlugin(id, title, **kw)
    self._setObject(o.getId(), o)
    o = getattr(aq_base(self), id)

    if RESPONSE is not None:
        RESPONSE.redirect('manage_workspace')

manage_addAnonCookieForm = DTMLFile("www/AnonCookieForm", globals())


class AnonCookiePlugin(BasePlugin):
    """Multi-plugin which adds ability to override the updating of cookie via
    a setAuthCookie method/script.
    """

    _properties = ( { 'id'    : 'title'
                    , 'label' : 'Title'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'cookie_name'
                    , 'label' : 'Cookie Name'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'anon_roles'
                    , 'label' : 'Anonymous Roles'
                    , 'type'  : 'lines'
                    , 'mode'  : 'w'
                    }
                  )

    meta_type = 'Anon Cookie Plugin'
    security = ClassSecurityInfo()
    cookie_name = 'anon_cookie'
    anon_roles = ['Contributor',]

    def __init__(self, id, title=None, cookie_name='', anon_roles=None):
        random.seed()
        self._setId(id)
        self.title = title
        if cookie_name:
            self.cookie_name = cookie_name
        if anon_roles:
            self.anon_roles = ['Contributor',]

        self.password_prefix = ''
        for i in range(0, 20):
            self.password_prefix += chr(ord('a')+random.randint(0,26))

    security.declarePrivate('getRolesForPrincipal')
    def getRolesForPrincipal(self, principal, request=None):

        return self.anon_roles


    security.declarePrivate( 'extractCredentials' )
    def extractCredentials( self, request ):

        """ Extract credentials from cookie or 'request'. """

        #return {}

        if request._authUserPW():
          return {} # allow normal ZMI access..

        if request.form.get('__ac_name', None):
          return {} # allow form based login..

        if request.get('__ac', None):
          return {} # already logged in user..

        creds = {}
        cookie = request.get(self.cookie_name, '')

        if cookie and cookie != 'deleted':
            cookie_val = decodestring(unquote(cookie))
            try:
                login, password = cookie_val.split(':')
            except ValueError:
                # Cookie is in a different format, so it is not ours
                return {}

            creds['login'] = login.decode('hex')
            creds['password'] = password.decode('hex')

        if not creds:
            login_suffix = random.random()
            
            login = 'anon_%s' % login_suffix
            password_plain = '%s_%s' % (self.password_prefix,login_suffix)
            password = md5.new(password_plain).digest()
            creds['login'] = login
            creds['password'] = password

            # store credentials in cookie
            
            cookie_str = '%s:%s' % (login.encode('hex'), password.encode('hex'))
            cookie_val = encodestring(cookie_str)
            cookie_val = cookie_val.rstrip()
            request.response.setCookie(self.cookie_name, quote(cookie_val), path='/')

        creds['remote_host'] = request.get('REMOTE_HOST', '')

        try:
            creds['remote_address'] = request.getClientAddr()
        except AttributeError:
            creds['remote_address'] = request.get('REMOTE_ADDR', '')

        return creds

    def authenticateCredentials(self, credentials):

        login = credentials['login']
        password = credentials['password']
        if login.startswith('anon_'):
            login_suffix = login[len('anon_'):]
            password_plain = '%s_%s' % (self.password_prefix,login_suffix)
            check_password = md5.new(password_plain).digest()

            if check_password == password:
                return (login, login)
            else:
                log("invalid login/password combination, possible break in attempt!")

        return None

    def getPropertiesForUser(self, user, request=None):

        """Get property values for a user or group.
        Returns a dictionary of values or a PropertySheet.
        """

        username = user.getId()
      
        if not username.startswith('anon_'):
          return None

        data = {}

        data['fullname']=username

        if DEBUG: log("Returning data: %s" % data)

        return data

    def enumerateUsers(self, id=None, login=None, exact_match=False,
                       sort_by=None, max_results=None, **kw):

        return_list = ()
        results = []
        userid = id or login
        if exact_match and userid:
            if userid.startswith('anon_'):
                results = [userid,]

        for usr in results:
            val = {'id' : usr,
                   'login' : usr,
                   'pluginid' : self.getId(),
                   'fullname' : usr,
                  }

            return_list += val,

        return return_list


classImplements(AnonCookiePlugin,
                IRolesPlugin,
                IExtractionPlugin,
                IAuthenticationPlugin,
                IPropertiesPlugin,
                IUserEnumerationPlugin
               )

InitializeClass(AnonCookiePlugin)
