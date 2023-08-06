from Products.PluggableAuthService import registerMultiPlugin
from plugins import anoncookie_handler
from permissions import *

registerMultiPlugin(anoncookie_handler.AnonCookiePlugin.meta_type)

def initialize(context):

    context.registerClass(anoncookie_handler.AnonCookiePlugin,
              permission = ManageUsers,
              constructors = (anoncookie_handler.manage_addAnonCookieForm,
              anoncookie_handler.manage_addAnonCookiePlugin),
              visibility = None)

