import frappe


# -------------------------------------------------------------------
# Global toggle
# -------------------------------------------------------------------

def is_permission_engine_enabled():
    """
    Check if custom CRM permission engine is enabled
    via CRM Settings custom field.
    """
    try:
        return (
            frappe.db.get_single_value(
                "CRM Settings",
                "custom_enable_permission_engine"
            ) == 1
        )
    except Exception:
        return False


# -------------------------------------------------------------------
# Global visibility (single source of truth)
# -------------------------------------------------------------------

def has_global_crm_visibility(user):
    """
    Users who bypass all CRM visibility rules.

    Includes:
    - Permission engine disabled
    - System Manager
    - CRM Full Access Roles (configurable)
    """
    if not is_permission_engine_enabled():
        return True

    if user_has_any_role(user, ["System Manager"]):
        return True

    if user_has_crm_full_access(user):
        return True

    return False


# -------------------------------------------------------------------
# Role helpers
# -------------------------------------------------------------------

def user_has_any_role(user, roles):
    try:
        user_roles = frappe.get_roles(user)
        return any(role in user_roles for role in roles)
    except Exception:
        return False


def user_has_crm_full_access(user):
    """
    Configurable full-access roles from CRM Settings child table.
    """
    if not is_permission_engine_enabled():
        return False

    try:
        user_roles = set(frappe.get_roles(user))
        if not user_roles:
            return False

        rows = frappe.db.get_all(
            "CRM Full Access Role",
            fields=["role"]
        )

        allowed_roles = {r.role for r in rows}
        return bool(user_roles.intersection(allowed_roles))

    except Exception:
        return False


# -------------------------------------------------------------------
# Sales Person helpers
# -------------------------------------------------------------------

def get_user_sales_person(user):
    """
    Resolve user's Sales Person via Employee.
    Guaranteed 1:1 mapping.
    """
    employee = frappe.db.get_value(
        "Employee",
        {"user_id": user},
        "name"
    )
    if not employee:
        return None

    return frappe.db.get_value(
        "Sales Person",
        {"employee": employee},
        "name"
    )


def get_sales_person_tree_bounds(sales_person):
    """
    Get lft / rgt bounds for a Sales Person node.
    """
    if not sales_person:
        return None, None

    return frappe.db.get_value(
        "Sales Person",
        sales_person,
        ["lft", "rgt"]
    )


def is_sales_person_in_user_tree(user, owner_user):
    """
    Check if owner's Sales Person is inside user's Sales Person subtree.
    """
    user_sp = get_user_sales_person(user)
    owner_sp = get_user_sales_person(owner_user)

    if not user_sp or not owner_sp:
        return False

    user_lft, user_rgt = get_sales_person_tree_bounds(user_sp)
    owner_lft, _ = get_sales_person_tree_bounds(owner_sp)

    return (
        user_lft is not None
        and owner_lft is not None
        and user_lft <= owner_lft <= user_rgt
    )


# -------------------------------------------------------------------
# Territory helpers
# -------------------------------------------------------------------

def get_user_managed_territory_bounds(user):
    """
    Return ALL territory tree ranges managed by the user.

    A user may manage multiple territories.
    Each territory may have children.
    """
    sales_person = get_user_sales_person(user)
    if not sales_person:
        return []

    territories = frappe.db.get_all(
        "Territory",
        filters={"territory_manager": sales_person},
        fields=["lft", "rgt"]
    )

    return [
        (t.lft, t.rgt)
        for t in territories
        if t.lft is not None and t.rgt is not None
    ]


def is_record_in_user_territory_tree(user, territory):
    """
    Check if a record's territory is inside ANY territory tree
    managed by the user (including child territories).

    Generic helper for Lead / Opportunity / Quotation / Customer.
    """
    if not territory:
        return False

    ranges = get_user_managed_territory_bounds(user)
    if not ranges:
        return False

    territory_lft, _ = frappe.db.get_value(
        "Territory",
        territory,
        ["lft", "rgt"]
    )

    if territory_lft is None:
        return False

    for lft, rgt in ranges:
        if lft <= territory_lft <= rgt:
            return True

    return False