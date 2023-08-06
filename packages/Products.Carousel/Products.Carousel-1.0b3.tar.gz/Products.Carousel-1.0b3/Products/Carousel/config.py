"""Common configuration constants
"""

PROJECTNAME = 'Carousel'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'Carousel Banner': 'Carousel: Add Carousel Banner',
}

from Products.CMFCore.permissions import setDefaultRoles
setDefaultRoles(ADD_PERMISSIONS['Carousel Banner'], ('Manager',))
