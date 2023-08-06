from Products.plonehrm.utils import updateEmployee


def employeeModified(object, event):
    """An employee has been modified.

    Do what we would previously do in an initializeArchetypes.
    """
    if not getattr(object, '_v_employee_is_updated', False):
        updateEmployee(object)
        object._v_employee_is_updated = True
