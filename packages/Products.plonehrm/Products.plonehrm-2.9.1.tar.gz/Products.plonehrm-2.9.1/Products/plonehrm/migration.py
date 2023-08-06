import logging

from zope.component import queryMultiAdapter
from zope.i18n import translate
from Products.CMFCore.utils import getToolByName
from zope.event import notify
from Products.Archetypes.event import ObjectInitializedEvent
from Acquisition import aq_parent

from Products.plonehrm import utils
from Products.plonehrm import PloneHrmMessageFactory as _


logger = logging.getLogger("plonehrm")


def update_worklocations(context):
    """Make sure all work locations have all the plonehrm placeful workflow.
    """
    catalog = getToolByName(context, 'portal_catalog')
    for brain in catalog(portal_type='WorkLocation'):
        try:
            worklocation = brain.getObject()
        except (AttributeError, KeyError):
            logger.warn("Error getting object at %s", brain.getURL())
            continue
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
        except (AttributeError, KeyError):
            logger.warn("Error getting object at %s", brain.getURL())
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


def update_employee_vocabularies(context):
    """Use the values from new vocabularies.

    This works when until now you have used Dutch values in the
    personaldata_properties.  Else you will have to write your own, sorry.

    gender field:
    - man -> male
    - vrouw -> female

    For the civilStatus field we did the same, but undid that later...:
    - gehuwd -> married
    - ongehuwd -> not_married
    """
    logger.info("Starting migration of gender and civilStatus of employees.")
    catalog = getToolByName(context, 'portal_catalog')
    employee_brains = catalog.searchResults(portal_type='Employee')
    logger.info("Found %s Employees.", len(employee_brains))


    language_tool = getToolByName(context, 'portal_languages')
    if language_tool:
        language = language_tool.getDefaultLanguage()
    else:
        language = 'en'
    married = _('label_married', u'married')
    not_married = _('label_not_married', u'not married')
    civilStatus_mapping = dict(
        married=translate(married, target_language=language),
        notmarried=translate(not_married, target_language=language),
        )

    for brain in employee_brains:
        try:
            employee = brain.getObject()
        except (AttributeError, KeyError):
            logger.warn("Error getting object at %s", brain.getURL())
            continue

        gender = employee.getGender()
        if isinstance(gender, basestring):
            gender = gender.lower()
        new = gender_mapping.get(gender)
        if new:
            employee.setGender(new)
            logger.info("Setting gender %s for %s", new, employee.Title())

        civilStatus = employee.getCivilStatus()
        new = civilStatus_mapping.get(civilStatus)
        if new:
            employee.setCivilStatus(new)
            logger.info("Setting civilStatus %s for %s", new, employee.Title())


def update_worklocations_addresses(context):
    """Make sure all work locations address are well converted from list
    to string.
    """
    logger.info('Updating addresses of work locations to strings.')

    catalog = getToolByName(context, 'portal_catalog')
    for brain in catalog(portal_type='WorkLocation'):
        try:
            worklocation = brain.getObject()
        except (AttributeError, KeyError):
            logger.warn("Error getting object at %s", brain.getURL())
            continue

        old_wl_address = worklocation.getRawAddress()
        old_company_address = worklocation.getRawCompanyAddress()

        if isinstance(old_wl_address, tuple):
            worklocation.setAddress("; ".join(old_wl_address))
        if isinstance(old_company_address, tuple):
            worklocation.setCompanyAddress("; ".join(old_company_address))

    logger.info('Updated worklocations addresses.')


def reindex_employees(context):
    """Reindex all employees, needed to display the Facebook has two
    new metadata have been added.
    """
    logger.info("Starting reindexing employees.")
    catalog = getToolByName(context, 'portal_catalog')
    employee_brains = catalog.searchResults(portal_type='Employee')
    logger.info("Found %s Employees.", len(employee_brains))

    for employee in employee_brains:
        employee = employee.getObject()
        employee.reindexObject()


def replace_old_substitution_parameters(context):
    """Replace old substitution parameters.

    Sometimes we rename substitution parameters, e.g.
    [company_official_name] was renamed to [company_legal_name].

    In this upgrade step we go through all the pages within our tools
    and update their text when old parameters are found.

    Note that in default Plone HRM the tools (portal_contracts and
    portal_jobperformance) are always in the root of the site, but in
    third party deployments there may be several instances throughout
    the site.
    """
    logger.info("Starting migrating old substitution parameters.")
    view = queryMultiAdapter((context, context.REQUEST),
                             name=u'substituter')
    try:
        old_parameters = view.old_parameters
    except AttributeError:
        logger.warn("AttributeError getting old_parameters from substituter "
                    "view. Aborting migration.")
        return
    if not old_parameters:
        logger.info("No old parameters known.  Stopping migration.")
        return
    catalog = getToolByName(context, 'portal_catalog')
    page_brains = catalog.searchResults(portal_type='Document')
    logger.info("Found %s pages.", len(page_brains))

    count = 0
    for brain in page_brains:
        url = brain.getURL()
        parent_id = url.split('/')[-2]
        if parent_id not in ('portal_contracts', 'portal_jobperformance'):
            continue
        try:
            page = brain.getObject()
        except (AttributeError, KeyError):
            logger.warn("Error getting object at %s", url)
            continue
        text = page.getText()
        for old, new in old_parameters.items():
            text = text.replace(old, new)
        if text != page.getText():
            count += 1
            logger.info("Replaced parameters in page at %s", url)
            page.setText(text)
            page.reindexObject()

    logger.info("%d templates needed updating.", count)


def create_template(template_location, template_type, old_template):
    """ Code factorization for the update_template method.
    """
    new_id = template_location.generateUniqueId('Template')
    template_location.invokeFactory('Template',
                                    id=new_id,
                                    title=old_template.title,
                                    type=template_type)

    new_template = getattr(template_location, new_id)

    new_template.description = old_template.description
    new_template.setText(old_template.getText())

    new_template.changeOwnership(old_template.getOwner())

    new_template.unmarkCreationFlag()
    new_template._renameAfterCreation()
    notify(ObjectInitializedEvent(new_template))

    if template_type == 'undefined':
        logger.warn("Could not assign type to %s, please specify it" % \
                    new_template.title)
    else:
        logger.info('Created template %s with type %s' % \
                    (new_template.title, template_type))

    return new_template


def update_templates(context):
    """ This method migrates old templates (pages in portal_contract,
    portal_jobperformance, portal_absence) to Template archetype.

    It also change Absence Evaluation. The previous ones were created using
    JobPerformance archetype. This class seeks for templates in
    portal_jobperformance. With this upgrade, templates for absence
    evaluations are stored in portal_absence and it we can not update absence
    evaluation as templates are not found.
    So we delete every JobPerformance located in absences, and create a real
    EvaluationInterview objects with the values of the previous JobPerformance.

    It tries to automatically sets the new type of the template by looking
    where it was used.
    The table below explains the cases and were the new template is located
    and its new type.

    Old location          | Used in               | New type           | New location
    ------------------------------------------------------------------------------------------
    portal_contracts      | never used            | undefined          | portal_contracts
    ------------------------------------------------------------------------------------------
    portal_contracts      | contracts only        | contract           | portal_contracts
    ------------------------------------------------------------------------------------------
    portal_contracts      | letters only          | letter             | portal_contracts
    ------------------------------------------------------------------------------------------
    portal_contracts      | letters and contracts | undefined          | portal_contracts
    ------------------------------------------------------------------------------------------
    portal_jobperformance | never user            | undefined          | portal_jobperformance
    ------------------------------------------------------------------------------------------
    portal_jobperformance | job perfomance only   | job_performance    | portal_jobperformance
    ------------------------------------------------------------------------------------------
    portal_jobperformance | absence only          | absence_evaluation | portal_absence
    ------------------------------------------------------------------------------------------
    portal_jobperformance | both                  | job_performance    | portal_jobperformance
                          |                       | absence_evaluation | portal_absence
    ------------------------------------------------------------------------------------------
    """
    logger.info("Starting migrating old templates.")
    catalog = getToolByName(context, 'portal_catalog')

    logger.info("Migrating portal_contract templates.")
    portal_contracts = getToolByName(context, 'portal_contracts')

    contentFilter = {'portal_type': 'Document'}
    old_templates = portal_contracts.getFolderContents(
        contentFilter=contentFilter)

    # The list of objects that should be deleted after the upgrade
    # mainly old templates and some job performance interviews.
    to_delete = []

    # We get all contracts and letters.
    contracts = [contract.getObject() for contract in
                 catalog.searchResults(portal_type='Contract')]

    letters = [contract.getObject() for contract in
               catalog.searchResults(portal_type='Letter')]

    for old_template in old_templates:
        # We look how much contracts used this template.
        old_template = old_template.getObject()

        # We get contracts and letters using this template.
        concerned_contracts = [contract for contract in contracts
                               if contract.getTemplate() == old_template.id]
        concerned_letters = [letter for letter in letters
                             if letter.getTemplate() == old_template.id]

        template_type = 'undefined'
        if concerned_contracts and not concerned_letters:
            template_type = 'contract'
        elif concerned_letters and not concerned_contracts:
            template_type = 'letter'

        # We create the new template
        new_template = create_template(portal_contracts,
                                       template_type,
                                       old_template)

        # We updates the contracts and letter.
        # Note: the only interrest is to define default template of the next
        # contract/letter.
        for contract in concerned_contracts:
            contract.setTemplate(new_template.id)

        for letter in concerned_letters:
            letter.setTemplate(new_template.id)

        to_delete.append(old_template)

    # Now we do the same thing for Job performances/Evaluation template.
    logger.info("Migrating portal_jobperformance templates.")

    portal_absence = getToolByName(context, 'portal_absence')
    portal_jobperformance = getToolByName(context, 'portal_jobperformance')

    interviews = [interview.getObject() for interview in
                  catalog.searchResults(portal_type='JobPerformanceInterview')]

    evaluations = [evaluation.getObject() for evaluation in
                  catalog.searchResults(portal_type='EvaluationInterview')]

    # We do not look for old template in portal_absence as this tool
    # never accepted simple documents as templates.
    contentFilter = {'portal_type': 'Document'}
    old_templates = portal_jobperformance.getFolderContents(
        contentFilter=contentFilter)

    for old_template in old_templates:
        old_template = old_template.getObject()

        # We get interviews and contracts using this template.
        concerned_interviews = [
            interview for interview in interviews
            if interview.getTemplate() == old_template.id]

        concerned_evaluations = [
            evaluation for evaluation in evaluations
            if evaluation.getTemplate() == old_template.id]

        # We create the template.
        # Depending on the case, we create an undefined template
        # in portal_jobperformances, a job_performance template
        # in portal_jobperformance, a absence_evaluation in
        # portal absence or two templates.
        if not concerned_interviews and not concerned_evaluations:
            create_template(portal_jobperformance, 'undefined', old_template)

        if concerned_interviews:
            new_jp_template = create_template(portal_jobperformance,
                                              'job_performance',
                                              old_template)
            # We update the interviews.
            for interview in concerned_interviews:
                interview.setTemplate(new_jp_template.id)

        if concerned_evaluations:
            new_abs_template = create_template(portal_absence,
                                               'absence_evaluation',
                                               old_template)

            for evaluation in concerned_evaluations:
                if evaluation.__class__.__name__ == 'JobPerformanceInterview':
                    # We create a new EvaluationInterview with the
                    # data of the previous interview as the actual object
                    # is a JobPerformance, not a real EvaluationInterview.
                    logger.info("Found EvaluationInterview with bad type.")
                    absence = aq_parent(evaluation)

                    new_id = absence.generateUniqueId('EvaluationInterview')
                    absence.invokeFactory('EvaluationInterview',
                                          id=new_id,
                                          title=evaluation.title)

                    new_evaluation = getattr(absence, new_id)

                    new_evaluation.setTemplate(new_abs_template.id)
                    new_evaluation.setDate(evaluation.getDate())
                    new_evaluation.setText(evaluation.getText())
                    new_evaluation.setImprovementAreas(
                        evaluation.getImprovementAreas())

                    new_evaluation.changeOwnership(evaluation.getOwner())

                    new_evaluation.unmarkCreationFlag()
                    new_evaluation._renameAfterCreation()
                    notify(ObjectInitializedEvent(new_evaluation))

                    logger.info("Created new EvaluationInterview in %s." % \
                                absence.title)

                    to_delete.append(evaluation)
                else:
                    evaluation.setTemplate(new_abs_template.id)

        to_delete.append(old_template)

    logger.info("Deleting useless objects. %s objects to delete" % \
                len(to_delete))

    for obj in to_delete:
        obj_id = obj.id
        obj_context = aq_parent(obj)
        obj_context._delObject(obj_id)
        logger.info("Deleted %s" % obj_id)


    logger.info("Migrating templates finished.")


def update_absence_workflow(context):
    """ This migration step is needed with the creation of the absence
    workflow.
    It seeks for every absence and checks if an end date has been set. In
    this case, the state will be 'closed', in the other case the absence
    will be in the state 'opened'.
    """

    logger.info("Starting applying absence workflow.")
    catalog = getToolByName(context, 'portal_catalog')
    absences = catalog.searchResults(portal_type='Absence')

    workflowTool = getToolByName(context, "portal_workflow")

    absence_count = 0
    for absence in absences:
        absence = absence.getObject()
        status = workflowTool.getStatusOf("absence_workflow", absence)

        if absence.getEndDate():
            try:
                workflowTool.doActionFor(absence, "close")
                absence_count += 1
            except:
                # The absence might already be closed.
                pass

    logger.info("%s absences changed state" % absence_count)


def update_employees_overview_viewlets(context):
    """ Removes plonehrm.checklist viewlet from the employeesOverview
    (default view of a worklocation) and add three more viewlets:
    - plonehrm.address
    - plonehrm.zipcode
    - plonehrm.city
    """
    portal_props = getToolByName(context, 'portal_properties', None)
    if portal_props is not None:
        hrm_props = getattr(portal_props, 'plonehrm_properties', None)
        if hrm_props is not None:
            viewlets = hrm_props.getProperty('EmployeesOverviewViewlets', ())

            if viewlets:
                viewlets = list(viewlets)
                if 'plonehrm.checklist' in viewlets:
                    viewlets.remove('plonehrm.checklist')

                new = ['plonehrm.address',
                       'plonehrm.zipcode',
                       'plonehrm.city']
                for viewlet in new:
                    if not viewlet in viewlets:
                        viewlets.append(viewlet)

                viewlets = tuple(viewlets)

                hrm_props.EmployeesOverviewViewlets = viewlets


def run_workflow_step(context):
    context.runImportStepFromProfile('profile-Products.plonehrm:default',
                                     'workflow')
    # Run the update security on the workflow tool.
    logger.info('Updating security settings.  This may take a while...')
    wf_tool = getToolByName(context, 'portal_workflow')
    wf_tool.updateRoleMappings()
    logger.info('Done updating security settings.')
