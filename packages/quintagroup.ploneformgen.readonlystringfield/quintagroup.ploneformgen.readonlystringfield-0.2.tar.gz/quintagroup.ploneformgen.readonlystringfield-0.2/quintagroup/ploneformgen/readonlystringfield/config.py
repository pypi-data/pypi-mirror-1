from Products.CMFCore import permissions

PROJECTNAME = 'quintagroup.ploneformgen.readonlystringfield'


ADD_PERMISSIONS = {
    'FormReadonlyStringField' : permissions.AddPortalContent,
    # -*- extra stuff goes here -*-
}