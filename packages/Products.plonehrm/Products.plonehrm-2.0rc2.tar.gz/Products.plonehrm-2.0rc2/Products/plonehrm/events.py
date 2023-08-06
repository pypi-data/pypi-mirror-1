from Products.plonehrm.utils import updateEmployee
from Products.plonehrm.utils import set_plonehrm_workflow_policy


def employeeModified(object, event):
    """An employee has been modified.

    Do what we would previously do in an initializeArchetypes.
    """
    if not getattr(object, '_v_employee_is_updated', False):
        updateEmployee(object)
        object._v_employee_is_updated = True


def worklocationCreated(object, event):
    """A Worklocation has been created.  Give it a placeful workflow."""
    set_plonehrm_workflow_policy(object)
