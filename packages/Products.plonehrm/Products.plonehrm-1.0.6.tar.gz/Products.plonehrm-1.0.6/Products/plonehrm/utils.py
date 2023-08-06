from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest


class HRMConfigException(Exception):
    pass


def updateEmployee(employee):
    """Add missing employee modules to the employee.
    """

    available_ids = employee.objectIds()
    needed_objects = []
    portal_props = getToolByName(employee,
                                 'portal_properties', None)
    if portal_props is not None:
        #hrm_props = getattr(portal_props, 'plonehrm_properties', None)
        hrm_props = portal_props.get('plonehrm_properties', None)
        if hrm_props is not None:
            needed_objects = hrm_props.getProperty(
                'portal_types_to_create', [])
    type_id_mapping = {}
    for item in needed_objects:
        parts = item.split(',')
        if len(parts) != 2:
            raise HRMConfigException, \
                "Bad item found in portal_types_to_create: %s" % item
        parts = [p.strip() for p in parts]
        portal_type = parts[0]
        id_ = parts[1]
        type_id_mapping[id_] = portal_type
    needed_ids = type_id_mapping.keys()
    to_create = [t for t in needed_ids
                 if t not in available_ids]
    pt = getToolByName(employee, 'portal_types')
    for id_ in to_create:
        portal_type = type_id_mapping[id_]
        try:
            #_createObjectByType(portal_type, employee, id_)
            pt.constructContent(portal_type, employee, id_)
            obj = employee[id_]
            obj.setTitle(id_)
        except BadRequest:
            # Already added, even though we checked this so why is
            # this getting called then.  Lunacy!
            pass


def email_adresses_of_local_managers(context):
    """Return email adresses of the local managers."""

    # Partially copied from plone's computeRoleMap.py.
    pu = context.plone_utils
    acquired_roles = pu.getInheritedLocalRoles(context)
    local_roles = context.acl_users.getLocalRolesForDisplay(context)
    mtool = context.portal_membership

    worklocation_managers = []
    hrm_managers = []
    worklocation_role = 'WorklocationManager'
    hrm_role = 'HrmManager'

    def process_member(name, roles, type, id):
        if not id.startswith('group_'):
            member = mtool.getMemberById(name)
            if (member is not None
                and not member.getProperty('email', '') == ''
                and not member.getProperty('fullname', '') == ''):
                name = member.getProperty('fullname')
                email = member.getProperty('email')
                full_email = '%s <%s>' % (name, email)
                if worklocation_role in roles:
                    worklocation_managers.append(full_email)
                if hrm_role in roles:
                    hrm_managers.append(full_email)

    # first process acquired roles
    for name, roles, type, id in acquired_roles:
        process_member(name, roles, type, id)

    # second process local roles
    for name, roles, type, id in local_roles:
        process_member(name, roles, type, id)

    return {'worklocation_managers': worklocation_managers,
            'hrm_managers': hrm_managers
            # Later, employees might be added. That's why I'm not returning a tuple.
            }


def set_plonehrm_workflow_policy(context):
    """Give the context the plonehrm placeful workflow policy."""
    pw = getToolByName(context, 'portal_placeful_workflow')
    config = pw.getWorkflowPolicyConfig(context)

    if not config:
        # Add the config.
        adder = context.manage_addProduct['CMFPlacefulWorkflow']
        adder.manage_addWorkflowPolicyConfig()
        config = pw.getWorkflowPolicyConfig(context)

    # Set the config.
    config.setPolicyIn(policy='plonehrm')
    getToolByName(context, 'portal_workflow').updateRoleMappings()
