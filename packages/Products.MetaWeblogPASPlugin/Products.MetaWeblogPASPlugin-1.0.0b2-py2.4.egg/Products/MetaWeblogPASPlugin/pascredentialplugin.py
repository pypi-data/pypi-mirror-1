from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin

from Products.PageTemplates.PageTemplateFile import PageTemplateFile



manage_addMetaWeblogCredentialPluginForm = PageTemplateFile(
    'www/metaweblogAdd',
    globals(),
    __name__='manage_addMetaWeblogCredentialPluginForm'
    )


def manage_addMetaWeblogCredentialPlugin(dispatcher,
                                         id,
                                         title=None,
                                         REQUEST=None):
    """Add a MetaWeblogCredentialPlugin to a Pluggable Auth Service.
    """
    obj = MetaWeblogCredentialPlugin(id, title)
    dispatcher._setObject(obj.getId(), obj)
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
                                '%s/manage_workspace'
                                '?manage_tabs_message='
                                'MetaWeblogCredentialPlugin+added.'
                            % dispatcher.absolute_url()
                            )


class MetaWeblogCredentialPlugin(BasePlugin):
    """PAS plugin for extracting credentials supplied by a MetaWeblog client.
    """

    meta_type = 'MetaWeblogCredentialPlugin'

    security = ClassSecurityInfo()

    def __init__(self, id, title=None):
        self._id = self.id = id
        self.title = title

    #
    #   IExtractionPlugin implementation
    #
    security.declarePrivate('extractCredentials')
    def extractCredentials(self, request):
        # request.args looks like this if a MetaWeblog client made the request:
        #    ('', username, password)
        try:
            login = request.args[1]
            password = request.args[2]
            return { 'login' : login, 'password' : password }
        except IndexError:
            return {}


classImplements(MetaWeblogCredentialPlugin, IExtractionPlugin)

InitializeClass(MetaWeblogCredentialPlugin)
