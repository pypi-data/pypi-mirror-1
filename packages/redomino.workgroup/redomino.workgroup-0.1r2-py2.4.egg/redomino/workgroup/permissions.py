from Products.CMFCore.permissions import setDefaultRoles

MANAGE_WORKGROUP = 'redomino.workgroup: manage Workgroups'
setDefaultRoles(MANAGE_WORKGROUP, ('Manager',))

ADD_MEMBER_AREA = "redomino.workgroup: Add member area"
setDefaultRoles(ADD_MEMBER_AREA, ('Manager','Owner',))

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'MemberArea': ADD_MEMBER_AREA,
}

