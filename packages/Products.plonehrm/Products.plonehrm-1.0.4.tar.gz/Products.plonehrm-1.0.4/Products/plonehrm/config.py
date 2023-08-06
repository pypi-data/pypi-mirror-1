PROJECTNAME = "plonehrm"
product_globals = globals()

QI_DEPS = (
    'CMFPlacefulWorkflow',
    'plonehrm.jobperformance',
    'plonehrm.checklist',
    'plonehrm.contracts',
    'plonehrm.personaldata',
    'plonehrm.notes',
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
