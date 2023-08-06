from Products.CMFCore.utils import getToolByName

def cleanUpFactoryTool(portal):
    tool = getToolByName(portal, 'portal_factory')
    if 'FormReadonlyStringField' in tool._factory_types.keys():
        del tool._factory_types['FormReadonlyStringField']

def uninstall(context):
    # Only run step if a flag file is present (e.g. not an extension profile)
    if context.readDataFile(
        'quintagroup.ploneformgen.readonlystringfield_uninstall.txt') is None:
        return
    out = []
    site = context.getSite()
    cleanUpFactoryTool(site)
