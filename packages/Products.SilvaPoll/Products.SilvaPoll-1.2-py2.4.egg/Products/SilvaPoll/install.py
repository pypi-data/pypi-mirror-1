from Products.Silva.install import add_fss_directory_view
from Products.Silva import roleinfo
from Globals import package_home
import os

def install(root):
    add_fss_directory_view(root.service_views, 'SilvaPoll', __file__, 'views')
    add_fss_directory_view(root.service_resources, 'SilvaPoll', __file__, 'resources')
    registerViews(root.service_view_registry)
    setupMetadata(root)
    configureSecurity(root)

def uninstall(root):
    unregisterViews(root.service_view_registry)
    root.service_views.manage_delObjects(['SilvaPoll'])
    root.service_resources.manage_delObjects(['SilvaPoll'])

def is_installed(root):
    return hasattr(root.service_views, 'SilvaPoll')

def registerViews(reg):
    reg.register('edit', 'Silva Poll Question',
                    ['edit', 'VersionedContent', 'PollQuestion'])
    reg.register('add', 'Silva Poll Question',
                    ['add', 'PollQuestion'])
    reg.register('public', 'Silva Poll Question',
                    ['public', 'PollQuestion'])
    reg.register('public', 'Silva Poll Question Version',
                    ['public', 'PollQuestion'])
    reg.register('preview', 'Silva Poll Question Version',
                    ['public', 'PollQuestion'])

def unregisterViews(reg):
    """Unregister core views on registry.
    """
    reg.unregister('edit', 'Silva Poll Question')
    reg.unregister('public', 'Silva Poll Question Version')
    reg.unregister('add', 'Silva Poll Question')

def configureSecurity(root):
    root.manage_permission('Add Silva Poll Question Versions', 
                            roleinfo.AUTHOR_ROLES)
    root.manage_permission('Add Silva Poll Questions', 
                            roleinfo.AUTHOR_ROLES)
  
def setupMetadata(root):
    root.service_metadata.addTypesMapping(['Silva Poll Question Version'],
                                            ('silva-content', 'silva-extra'))
