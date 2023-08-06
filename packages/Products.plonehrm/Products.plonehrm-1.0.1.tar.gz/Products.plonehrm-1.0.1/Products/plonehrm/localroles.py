from zope.interface import implements
from plone.app.workflow.interfaces import ISharingPageRole

# Please keep this 'PMF' and not '_' as otherwise i18ndude picks it
# up, does not realize it is for the plone domain and puts it in the
# pot/po files of plonehrm.  Alternatively: exclude this file in
# rebuild_i18n.sh
from Products.CMFPlone import PloneMessageFactory as PMF


# Only managers can manage these

class HrmManagerRole(object):
    implements(ISharingPageRole)

    title = PMF(u"title_hrm_manager_role",
                default="HRM manager")
    required_permission = 'Manage portal'


class WorklocationManagerRole(object):
    implements(ISharingPageRole)

    title = PMF(u"title_worklocation_manager_role",
                default="HRM worklocation manager")
    required_permission = 'Manage portal'
