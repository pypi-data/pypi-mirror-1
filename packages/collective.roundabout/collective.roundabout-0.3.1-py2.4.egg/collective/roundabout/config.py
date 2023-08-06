"""Common configuration constants
"""
from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = 'collective.roundabout'

ADD_PERMISSIONS = {
    'RoundAbout Map Hotspot': 'collective.roundabout: Add RoundAbout Map Hotspot',
    'RoundAbout Map': 'collective.roundabout: Add RoundAbout Map',
    'RoundAbout Image Hotspot': 'collective.roundabout: Add RoundAbout Image Hotspot',
    'RoundAbout Image': 'collective.roundabout: Add RoundAbout Image',
    'RoundAbout Tour': 'collective.roundabout: Add RoundAbout Tour',
}

setDefaultRoles('collective.roundabout: Add RoundAbout Map Hotspot', ('Manager', 'Contributer'))
setDefaultRoles('collective.roundabout: Add RoundAbout Map', ('Manager', 'Contributer'))
setDefaultRoles('collective.roundabout: Add RoundAbout Image Hotspot', ('Manager', 'Contributer'))
setDefaultRoles('collective.roundabout: Add RoundAbout Image', ('Manager', 'Contributer'))
setDefaultRoles('collective.roundabout: Add RoundAbout Tour', ('Manager', 'Contributer'))
