from Persistence.mapping import PersistentMapping
from Products.GenericSetup.interfaces import IFilesystemExporter
from Products.GenericSetup.interfaces import IFilesystemImporter
from Products.PluginRegistry.PluginRegistry import PluginRegistry


# override the default PAS handlers since those assume the setup tool
# is inside the PAS instance
def exportPAS(context):
    IFilesystemExporter(context.getSite().acl_users).export(context,
                                                            'PAS',
                                                            True)

def importPAS(context):
    if context.readDataFile('remopenid.txt') is None:
        return
    if context.isDirectory('PAS'):
        uf = context.getSite().acl_users
        # Delete and recreate the plugins registry by hand b/c it will
        # not be properly initialized otherwise; since we have
        # 'plugins' listed in the GS profile's PAS/.preserve file, it
        # won't be deleted and recreated by the import
        reg_id = 'plugins'
        if reg_id in uf:
            uf._delObject(reg_id)
            registry = PluginRegistry()
            registry._setId(reg_id)
            uf._setObject(reg_id, registry)
            registry._plugins = PersistentMapping()
        IFilesystemImporter(uf).import_(context, 'PAS', True)
            
