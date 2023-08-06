# (C) 2005-2009. University of Washington. All rights reserved.

from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.setuphandlers import DEFAULT_POLICIES

def setVersionedTypes(portal):
    """Set up the types to be versioned.

    This is here instead of in teh policy because I want
    the types versioned no matter which policy is used.
    """
    portal_repository = getToolByName(portal,
                                      'portal_repository')
    versionable_types = list(portal_repository.getVersionableContentTypes())

    for type_id in ('collective.types.Citation',):
        if type_id not in versionable_types:
            versionable_types.append(type_id)
            #Add default versioning policies to the versioned type
            for policy_id in DEFAULT_POLICIES:
                portal_repository.addPolicyForContentType(type_id,
                                                          policy_id)
    portal_repository.setVersionableContentTypes(versionable_types)

def importVarious(context):
    portal = context.getSite()
    setVersionedTypes(portal)
