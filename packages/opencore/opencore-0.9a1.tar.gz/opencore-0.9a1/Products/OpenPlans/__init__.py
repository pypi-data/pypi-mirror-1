"""
OpenPlans
"""

__authors__ = 'Rob Miller <ra@burningman.com>'
__docformat__ = 'restructuredtext'

from AccessControl import ModuleSecurityInfo
from AccessControl import allow_module, allow_class, allow_type

from Globals import package_home

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore import utils as cmf_utils
from Products.CMFCore.FSPageTemplate import FSPageTemplate
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.DirectoryView import registerFileExtension
from Products.Archetypes import public as atapi

from Products.listen.permissions import AddMailingList

from zope.component import getUtility

from topp.featurelets.interfaces import IFeatureletRegistry

import config
from permissions import initialize as initialize_permissions

import monkey
import Extensions.setup
from opencore.nui import indexing

# Register Global Tools/Services/Config
# (Skins)
registerFileExtension('xsl', FSPageTemplate)
registerDirectory(config.SKINS_DIR, config.GLOBALS)


def initialize(context):
    # Importing the content types allows for their registration
    # with the Archetypes runtime
    from content import *
    from opencore.content import *
    from opencore.featurelets.roster import RosterFeaturelet
    from opencore.featurelets.listen import ListenFeaturelet
    from opencore.tasktracker.featurelet import TaskTrackerFeaturelet
    from opencore.listen import mailinglist

    # Register customization policy
    import policy
    policy.register(context, config.GLOBALS)

    from AccessControl import ModuleSecurityInfo

    msi = ModuleSecurityInfo('Products.OpenPlans.interfaces')
    msi.declarePublic('IWriteWorkflowPolicySupport')

    # Ask Archetypes to handback all the type information needed
    # to make the CMF happy.
    types = atapi.listTypes(config.PROJECTNAME)
    content_types, constructors, ftis = atapi.process_types(types,
                                                            config.PROJECTNAME)

    # XXX make this a 'z3types' data structure
    content_types = content_types + (mailinglist.OpenMailingList,)
    constructors = constructors + (mailinglist.addOpenMailingList,)
    ftis = ftis + z3ftis

    permissions = initialize_permissions()
    permissions['Open Mailing List'] = AddMailingList
    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (config.PROJECTNAME,
                           getattr(atype,'archetype_name','portal_type'))
        cmf_utils.ContentInit(
            kind,
            content_types      = (atype,),
            permission         = permissions[atype.portal_type],
            extra_constructors = (constructor,),
            fti                = ftis,
            ).initialize(context)

    flet_registry = getUtility(IFeatureletRegistry)
    flet_registry.registerFeaturelet(RosterFeaturelet())
    flet_registry.registerFeaturelet(ListenFeaturelet())
    flet_registry.registerFeaturelet(TaskTrackerFeaturelet())
    
    from opencore.auth import SignedCookieAuthHelper
    from AccessControl.Permissions import add_user_folders
    context.registerClass( SignedCookieAuthHelper.SignedCookieAuthHelper,
                           permission = add_user_folders,
                           constructors = ( SignedCookieAuthHelper.manage_addSignedCookieAuthHelperForm,
                                            SignedCookieAuthHelper.manage_addSignedCookieAuthHelper ),
                           visibility = None
                           )
    
    # do all at import cataloging setup
    indexing.register_indexable_attrs()
    
