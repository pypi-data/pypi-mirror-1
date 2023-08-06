import logging
from AccessControl import Unauthorized
from DateTime import DateTime
from zope.component import queryMultiAdapter
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest

logger = logging.getLogger("plonehrm")


class HRMConfigException(Exception):
    pass


def updateEmployee(object, event=None):
    """Add missing employee modules to the employee.

    This method can be used as event handler; but event is ignored: we
    only need the object.  The function signature needs to accept
    events though, otherwise you get TypeErrors.
    """
    employee = object
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
        except ValueError, exc:
            # Probably: content type does not exist.
            logger.warn(exc)


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
            'hrm_managers': hrm_managers,
            # Later, employees might be added. That's why I'm not
            # returning a tuple.
            }


def set_plonehrm_workflow_policy(context):
    """Give the context the plonehrm placeful workflow policy."""
    pw = getToolByName(context, 'portal_placeful_workflow')
    try:
        config = pw.getWorkflowPolicyConfig(context)
    except Unauthorized:
        logger.warn("User is not allowed to get/set the workflow policy "
                    "in his work location.  Using the default.")
        return

    if not config:
        # Add the config.
        adder = context.manage_addProduct['CMFPlacefulWorkflow']
        adder.manage_addWorkflowPolicyConfig()
        config = pw.getWorkflowPolicyConfig(context)

    # Set the config.
    config.setPolicyIn(policy='plonehrm')
    getToolByName(context, 'portal_workflow').updateRoleMappings()


def next_anniversary(employee, now=None):
    """Helper function to get the next anniversary of the employee

    If the employee has his anniversary today, then next_anniversary
    will also return today.

    The 'now' parameter is only there to ease testing.


    We test the next_anniversary and age functions here .  We create
    some easier dummy classes:

    >>> class DummyEmployee(object):
    ...     def __init__(self, birthdate=None):
    ...         self.birthDate = birthdate
    ...     def getBirthDate(self):
    ...         return self.birthDate
    >>> emp = DummyEmployee()
    >>> next_anniversary(emp) is None
    True

    Let's take a normal birthday:


    >>> emp.birthdate = DateTime('1976/01/27')
    >>> next_anniversary(emp, now=DateTime('1999/01/12'))
    DateTime('1999/01/27')
    >>> age(emp, now=DateTime('1999/01/12'))
    22

    >>> next_anniversary(emp, now=DateTime('1999/01/27'))
    DateTime('1999/01/27')
    >>> age(emp, now=DateTime('1999/01/27'))
    23

    >>> next_anniversary(emp, now=DateTime('1999/02/12'))
    DateTime('2000/01/27')
    >>> age(emp, now=DateTime('1999/02/12'))
    23


    Having a birthday at leap day (29 February) should work too).  We
    cheat by setting the anniversay to the 28th of February then.

    >>> emp.birthdate = DateTime('1984/02/29')
    >>> next_anniversary(emp, now=DateTime('1999/02/12'))
    DateTime('1999/02/28')
    >>> age(emp, now=DateTime('1999/02/12'))
    14

    Of course when this year *is* a leap year, then 29 February is
    fine.

    >>> next_anniversary(emp, now=DateTime('2004/02/12'))
    DateTime('2004/02/29')
    >>> age(emp, now=DateTime('2004/02/12'))
    19

    >>> next_anniversary(emp, now=DateTime('2004/02/28'))
    DateTime('2004/02/29')
    >>> age(emp, now=DateTime('2004/02/28'))
    19

    >>> next_anniversary(emp, now=DateTime('2004/02/29'))
    DateTime('2004/02/29')
    >>> age(emp, now=DateTime('2004/02/29'))
    20

    >>> next_anniversary(emp, now=DateTime('2004/03/12'))
    DateTime('2005/02/28')
    >>> age(emp, now=DateTime('2004/03/12'))
    20

    >>> next_anniversary(emp, now=DateTime('2005/02/12'))
    DateTime('2005/02/28')
    >>> age(emp, now=DateTime('2005/02/12'))
    20

    >>> next_anniversary(emp, now=DateTime('2005/02/28'))
    DateTime('2005/02/28')
    >>> age(emp, now=DateTime('2005/02/28'))
    20

    >>> next_anniversary(emp, now=DateTime('2005/03/12'))
    DateTime('2006/02/28')
    >>> age(emp, now=DateTime('2005/03/12'))
    21



   """
    birth_date = employee.getBirthDate()

    if birth_date is None:

        return None
    # When testing we want to make sure that the tests keep passing,
    # also next year, and in the next leap year.  So we allow passing
    # a parameter 'now'.
    if not now:
        now = DateTime().earliestTime()
    birth_month = birth_date.month()
    birth_day = birth_date.day()
    if not now.isLeapYear() and birth_month == 2 and birth_day == 29:
        # This is a leap day, but it is not a leap year.
        birth_day = 28
    anniversary = DateTime(now.year(), birth_month, birth_day)
    if now > anniversary:
        birth_day = birth_date.day()
        next_year = DateTime(now.year()+1, 1, 1)
        if not next_year.isLeapYear() and birth_month == 2 and birth_day == 29:
            # This is a leap day, but it is not a leap year.
            birth_day = 28
        anniversary = DateTime(next_year.year(), birth_month, birth_day)

    return anniversary


def age(employee, now=None):


    """Helper function to get the age of the employee.

    The 'now' parameter is only there to ease testing.

    For tests, see the next_anniversary function above.
    """
    # When testing we want to make sure that the tests keep passing,
    # also next year, and in the next leap year.  So we allow passing
    # a parameter 'now'.
    if not now:
        now = DateTime().earliestTime()

    birth_date = employee.getBirthDate()
    if birth_date is None:
        return None
    birth_year = birth_date.year()
    birth_month = birth_date.month()
    birth_day = birth_date.day()
    birth_date_this_year = (now.year(), birth_month, birth_day)
    this_date = (now.year(), now.month(), now.day())
    age = now.year() - birth_year

    if birth_date_this_year == this_date:
        return age
    if this_date < birth_date_this_year:
        age -= 1
        return age

    return age


def apply_template_of_tool(object, tool_name):
    """After initializing this object, set the text based on template.

    object is likely a job performance interview or absence evaluation
    interview.  For contracts there are some special rules, but that
    is done in plonehrm.contracts.

    This funcion is no event handler, but can be used in event
    handlers.
    """
    view = queryMultiAdapter((object, object.REQUEST),
                             name=u'substituter')
    if view is None:
        raise ValueError('Components are not properly configured, could '
                         'not find "substituter" view')

    tool = getToolByName(object, tool_name, None)
    if tool is None:
        logger.error("%s cannot be found.", tool_name)
        return

    # Get the text from the template
    pages = [t for t in tool.listTemplates()
                     if t.getId() == object.template]
    if not pages:
        logger.warn("Template %r cannot be found." % object.template)
        return
    template_page = pages[0]
    template_text = template_page.getText()

    # Save the substituted text on the object.
    resulting_text = view.substitute(template_text)
    object.setText(resulting_text)
