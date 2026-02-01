# crm_permission_engine/permissions/quotation.py

def permission_query(user, doctype=None):
    """
    Permission query condition for Quotation list views.
    """
    return ""


def has_permission(doc, user):
    """
    Permission check for single Quotation document.
    """
    return True