from AccessControl.Permissions import add_user_folders

from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin

from pascredentialplugin import MetaWeblogCredentialPlugin, \
    manage_addMetaWeblogCredentialPlugin, manage_addMetaWeblogCredentialPluginForm


def initialize(context):
    """Initialize the MetaWeblogCredentialPlugin.
    """
    registerMultiPlugin(MetaWeblogCredentialPlugin.meta_type)
    context.registerClass( MetaWeblogCredentialPlugin
        , permission=add_user_folders
        , constructors=( manage_addMetaWeblogCredentialPluginForm
            , manage_addMetaWeblogCredentialPlugin
            )
        , icon=''
        , visibility=None
    )
