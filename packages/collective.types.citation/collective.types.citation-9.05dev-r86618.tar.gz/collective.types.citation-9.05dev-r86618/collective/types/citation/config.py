# (C) 2005-2009. University of Washington. All rights reserved.
"""Common configuration constants
"""
from Products.CMFCore.permissions import AddPortalContent

PROJECTNAME = "collective.types.citation"
IMAGE_KEY = 'image'
ADD_PERMISSIONS = {'collective.types.Citation': AddPortalContent,}
