from Products.Silva.ExtensionRegistry import extensionRegistry
from Products.Silva.fssite import registerDirectory
from Products.SilvaMetadata.Compatibility import registerTypeForMetadata
import PollQuestion
import ServicePolls, ServicePollsMySQL
import install

def initialize(context):
    extensionRegistry.register(
        'SilvaPoll', 'Silva Poll', context, [PollQuestion], 
        install, depends_on='SilvaExternalSources')

    context.registerClass(
        ServicePolls.ServicePolls,
        constructors = (ServicePolls.manage_addServicePollsForm,
                        ServicePolls.manage_addServicePolls),
        icon = 'www/poll_service.png'
    )

    context.registerClass(
        ServicePollsMySQL.ServicePollsMySQL,
        constructors = (ServicePollsMySQL.manage_addServicePollsMySQLForm,
                        ServicePollsMySQL.manage_addServicePollsMySQL),
        icon = 'www/pollquestion.gif'
    )

    registerDirectory('views', globals())
    registerDirectory('resources', globals())
    registerTypeForMetadata('Silva Poll Question Version')

from AccessControl import allow_module

allow_module('Products.SilvaPoll.i18n')
