import logging

from Products.CMFCore.utils import getToolByName

from Products.plonehrm import utils


logger = logging.getLogger("plonehrm")


def update_worklocations(context):
    """Make sure all work locations have all the plonehrm placeful workflow.
    """
    catalog = getToolByName(context, 'portal_catalog')
    for brain in catalog(portal_type='WorkLocation'):
        worklocation = brain.getObject()
        utils.set_plonehrm_workflow_policy(worklocation)
    logger.info('Set the plonehrm workflow policy in all work locations.')
    workflow = getToolByName(context, 'portal_workflow')
    workflow.updateRoleMappings()
    logger.info('Updated the role mappings in the site.')


def merge_personal_data(context):
    """Merge personal data from old separate object in employee itself.

    When adding a new Employee, we used to create an object 'personal'
    inside this employee.  That would contain most of the fields of
    the employee.  This worked mostly but not completely and gave some
    problems.  And it was hackish and complex anyway, so we got rid of
    it.

    What we do in this migration is to go over each Employee object
    and get the info from its personal object, put that inside the
    employee itself and remove the personal object.
    """
    logger.info("Starting migration of personal data to employee.")
    # First we remove PersonalData from the portal_types_to_create
    # property.

    catalog = getToolByName(context, 'portal_catalog')
    employee_brains = catalog.searchResults(
        portal_type=('Employee'))
    logger.info("Found %s Employees.", len(employee_brains))
    for brain in employee_brains:
        try:
            employee = brain.getObject()
        except AttributeError:
            logger.warn("AttributeError getting employee object at %s",
                        brain.getURL())
            continue
        try:
            personal = employee.personal
        except AttributeError:
            logger.debug("Employee already migrated: %s",
                         employee.absolute_url())
            continue
        logger.info("Migrating employee at %s", employee.absolute_url())

        # Now we can get the values of the fields of the old personal
        # object and put them in the employee object.
        employee.setBirthDate(personal.getBirthDate())
        employee.setAddress(personal.getAddress())
        employee.setPostalCode(personal.getPostalCode())
        employee.setCity(personal.getCity())
        employee.setState(personal.getState())
        employee.setCountry(personal.getCountry())
        employee.setTelephone(personal.getTelephone())
        employee.setMobilePhone(personal.getMobilePhone())
        employee.setEmail(personal.getEmail())
        employee.setPlaceOfBirth(personal.getPlaceOfBirth())
        employee.setGender(personal.getGender())
        employee.setCivilStatus(personal.getCivilStatus())
        employee.setIdType(personal.getIdType())
        employee.setIdNumber(personal.getIdNumber())
        employee.setIdEndDate(personal.getIdEndDate())
        employee.setNationality(personal.getNationality())
        employee.setSocialSecurityNumber(personal.getSocialSecurityNumber())
        employee.setBankNumber(personal.getBankNumber())
        employee.setWorkStartDate(personal.getWorkStartDate())

        # We delete the 'personal' object
        employee._delObject('personal')

        # This seems a good time to reindex the employee for good measure.
        employee.reindexObject()


def cleanup_portal_types_to_create(context):
    portal_props = getToolByName(context,
                                 'portal_properties', None)
    if portal_props is not None:
        hrm_props = portal_props.get('plonehrm_properties', None)
        if hrm_props is not None:
            create = list(hrm_props.getProperty('portal_types_to_create', []))
            try:
                create.remove('PersonalData,personal')
                hrm_props._updateProperty('portal_types_to_create', create)
                logger.info("Removed PersonalData,personal from "
                            "portal_types_to_create.")
            except ValueError:
                # Already removed
                pass


def remove_old_import_step(context):
    # context is portal_setup which is nice
    registry = context.getImportStepRegistry()
    old_step = u'register_personaldata'
    if old_step in registry.listSteps():
        try:
            registry.unregisterStep(old_step)
        except AttributeError:
            # BBB for GS 1.3
            del registry._registered[old_step]

        # Unfortunately we manually have to signal the context
        # (portal_setup) that it has changed otherwise this change is
        # not persisted.
        context._p_changed = True
        logger.info("Old %s import step removed from import registry.",
                    old_step)


gender_mapping = dict(
    man='male',
    vrouw='female',
    )

civilStatus_mapping = dict(
    gehuwd='married',
    ongehuwd='not_married',
    )


def update_employee_vocabularies(context):
    """Use the values from new vocabularies.

    This works when until now you have used Dutch values in the
    personaldata_properties.  Else you will have to write your own, sorry.

    gender field:
    - man -> male
    - vrouw -> female

    civilStatus field:
    - gehuwd -> married
    - ongehuwd -> not_married
    """
    logger.info("Starting migration of gender and civilStatus of employees.")
    catalog = getToolByName(context, 'portal_catalog')
    employee_brains = catalog.searchResults(portal_type='Employee')
    logger.info("Found %s Employees.", len(employee_brains))

    for brain in employee_brains:
        try:
            employee = brain.getObject()
        except AttributeError:
            logger.warn("AttributeError getting employee object at %s",
                        brain.getURL())

        gender = employee.getGender()
        new = gender_mapping.get(gender)
        if new:
            employee.setGender(new)
            logger.info("Setting gender %s for %s", new, employee.Title())

        civilStatus = employee.getCivilStatus()
        new = civilStatus_mapping.get(civilStatus)
        if new:
            employee.setCivilStatus(new)
            logger.info("Setting civilStatus %s for %s", new, employee.Title())
