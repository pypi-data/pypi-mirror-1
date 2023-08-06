# Standard library imports
from StringIO import StringIO

# Zope imports
from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin

# CMF imports
from Products.CMFCore.utils import getToolByName

# Local imports
from Products.MetaWeblogPASPlugin import config


def install(self):
    """Install the MetaWeblog credential extraction PAS plugin.
    """
    out = StringIO()
    pas = getToolByName(self, 'acl_users')
    dispatcher = pas.manage_addProduct['MetaWeblogPASPlugin']
    dispatcher.manage_addMetaWeblogCredentialPlugin(config.PLUGIN_ID,
                                                    config.PLUGIN_TITLE)
    print >> out, u"'%s' plugin added to acl_users." % config.PLUGIN_ID
    # Activate it:
    plugins = pas.plugins
    # plugins is a PluginRegistry
    plugins.activatePlugin(IExtractionPlugin, config.PLUGIN_ID)
    print >> out, u"'%s' plugin activated." % config.PLUGIN_ID
    print >> out, u"Successfully installed %s." % config.PROJECTNAME
    return out.getvalue()


def uninstall(self):
    """Uninstall the PAS plugin.
    """
    out = StringIO()
    pas = getToolByName(self, 'acl_users')
    pas.plugins.deactivatePlugin(IExtractionPlugin, config.PLUGIN_ID)
    print >> out, u"'%s' plugin deactivated." % config.PLUGIN_ID
    pas.manage_delObjects(ids=[config.PLUGIN_ID,])
    print >> out, u"'%s' plugin removed from acl_users." % config.PLUGIN_ID
    print >> out, u"Successfully uninstalled %s." % config.PROJECTNAME
    return out.getvalue()

