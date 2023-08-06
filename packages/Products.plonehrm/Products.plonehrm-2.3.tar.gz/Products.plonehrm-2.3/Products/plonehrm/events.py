from Products.plonehrm.utils import set_plonehrm_workflow_policy


def worklocationCreated(object, event):
    """A Worklocation has been created.  Give it a placeful workflow."""
    set_plonehrm_workflow_policy(object)
