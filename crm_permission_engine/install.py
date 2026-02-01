import frappe
from .custom_fields import get_custom_fields
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_install():
    """
    Setup required configuration after app installation
    """
    create_custom_fields(get_custom_fields())


def before_uninstall():
    """
    Cleanup custom fields before uninstall
    """
    remove_custom_fields()


def remove_custom_fields():
    fields = get_custom_fields()

    for doctype, custom_fields in fields.items():
        for field in custom_fields:
            frappe.db.delete(
                "Custom Field",
                {
                    "dt": doctype,
                    "fieldname": field["fieldname"],
                },
            )