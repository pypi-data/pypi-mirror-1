from Products.CMFCore.permissions import setDefaultRoles

MANAGE_WORKGROUP = 'redomino.workgroup: manage Workgroups'
setDefaultRoles(MANAGE_WORKGROUP, ('Manager',))
