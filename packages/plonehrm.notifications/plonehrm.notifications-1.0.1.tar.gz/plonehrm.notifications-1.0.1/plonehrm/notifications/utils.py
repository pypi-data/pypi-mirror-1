from Products.CMFCore.utils import getToolByName


def get_employees_for_checking(context):
    """Get the employees that need to be checked.

    Get them from the catalog.  Return only the active employees.
    """
    cat = getToolByName(context, 'portal_catalog')
    return cat(portal_type='Employee', review_state='active')
