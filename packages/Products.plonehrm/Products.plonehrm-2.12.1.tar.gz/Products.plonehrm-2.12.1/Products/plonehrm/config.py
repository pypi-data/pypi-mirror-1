PROJECTNAME = "plonehrm"
product_globals = globals()

QI_DEPS = (
    'CMFPlacefulWorkflow',
    'plonehrm.jobperformance',
    'plonehrm.checklist',
    'plonehrm.contracts',
    'plonehrm.notes',
    'plonehrm.absence',
    )

# Make a dict of dicts to list the properties.
PLONEHRM_PROPERTIES = {}
PLONEHRM_PROPERTIES['birthday_notification_period'] = \
    dict(default=7, type='int')
PLONEHRM_PROPERTIES['contract_expiry_notification_period'] = \
    dict(default=6*7, type='int')
PLONEHRM_PROPERTIES['trial_ending_notification_period'] = \
    dict(default=2*7, type='int')
PLONEHRM_PROPERTIES['birthday_notification'] = \
    dict(default=True, type='boolean')
PLONEHRM_PROPERTIES['contract_expiry_notification'] = \
    dict(default=True, type='boolean')
PLONEHRM_PROPERTIES['trial_ending_notification'] = \
    dict(default=True, type='boolean')
PLONEHRM_PROPERTIES['EmployeeDetailsViewlets'] = \
    dict(default=('plonehrm.personaldata',
                  'plonehrm.contract',
                  'plonehrm.notes',
                  'plonehrm.jobperformance',
                  'plonehrm.checklist',
                  'plonehrm.absence',
                  'plonehrm.files',
                  ), type='lines')

PLONEHRM_PROPERTIES['EmployeesOverviewViewlets'] = \
    dict(default=('plonehrm.fullname',
                  'plonehrm.phone',
                  'plonehrm.mobile',
#                  'plonehrm.checklist',
                  'plonehrm.address',
                  'plonehrm.zipcode',
                  'plonehrm.city',
                  ), type='lines')

PLONEHRM_PROPERTIES['EmployeesAbsenceViewlets'] = \
    dict(default=('plonehrm.fullname',
#                  'plonehrm.sicknespermonth',
#                  'plonehrm.totalsickdays',
#                  'plonehrm.annualpercentagesick',
                  ), type='lines')

PLONEHRM_PROPERTIES['EmployeesImprovementsOverviewViewlets'] = \
    dict(default=('plonehrm.fullname',
                  'plonehrm.improvements',
                  ), type='lines')


# We do the same for the personaldata_properties sheet.
PERSONALDATA_PROPERTIES = {}

PERSONALDATA_PROPERTIES['show_state'] = \
    dict(default=False, type='boolean')

PERSONALDATA_PROPERTIES['show_country'] = \
    dict(default=False, type='boolean')

PERSONALDATA_PROPERTIES['civil_status_vocabulary'] = \
    dict(default=("Married",
                  "Not married",
                  ), type='lines')

PERSONALDATA_PROPERTIES['id_type_vocabulary'] = \
    dict(default=("passport",
                  ), type='lines')
