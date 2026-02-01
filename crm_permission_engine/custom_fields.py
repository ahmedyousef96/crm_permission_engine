def get_custom_fields():
    """
    Custom fields required by CRM Permission Engine
    """
    return {
        "CRM Settings": [
            # --------------------------------------------------
            # Section: Custom CRM Permissions
            # --------------------------------------------------
            {
                "fieldname": "custom_crm_permissions_section",
                "fieldtype": "Section Break",
                "label": "Custom CRM Permissions",
                "insert_after": "update_timestamp_on_new_communication",
            },

            # --------------------------------------------------
            # Enable Permission Engine
            # --------------------------------------------------
            {
                "fieldname": "custom_enable_permission_engine",
                "fieldtype": "Check",
                "label": "Enable CRM Permission Engine",
                "default": 1,
                "insert_after": "custom_crm_permissions_section",
                "description": (
                    "Enable custom CRM visibility rules based on "
                    "Sales Person and Territory hierarchies. "
                    "Disable this option to fallback to standard ERPNext permissions."
                ),
            },

            # --------------------------------------------------
            # Full Access Roles (Multi Select)
            # --------------------------------------------------
            {
                "fieldname": "custom_crm_full_access_roles",
                "fieldtype": "Table MultiSelect",
                "label": "CRM Full Access Roles",
                "options": "Role",
                "insert_after": "custom_enable_permission_engine",
                "depends_on": "eval:doc.custom_enable_permission_engine == 1",
                "description": (
                    "Roles selected here will have full visibility "
                    "across all CRM records."
                ),
            },
        ]
    }