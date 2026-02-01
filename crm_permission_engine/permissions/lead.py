import frappe
from crm_permission_engine.permissions.utils import (
    has_global_crm_visibility,
    is_sales_person_in_user_tree,
    is_record_in_user_territory_tree,
)


# -------------------------------------------------------------------
# Record-level permission
# -------------------------------------------------------------------

def has_permission(doc, user):
    """
    Visibility rules for a single Lead document.
    """

    if has_global_crm_visibility(user):
        return True

    if doc.lead_owner:
        return is_sales_person_in_user_tree(user, doc.lead_owner)

    return is_record_in_user_territory_tree(user, doc.territory)


# -------------------------------------------------------------------
# List-level permission
# -------------------------------------------------------------------

def permission_query(user, doctype=None):
    """
    SQL permission query for Lead list views.
    """

    if has_global_crm_visibility(user):
        return ""

    conditions = []

    # Assigned leads ? Sales Person Tree
    conditions.append(
        """
        `tabLead`.`lead_owner` IN (
            SELECT e2.user_id
            FROM `tabEmployee` e1
            JOIN `tabSales Person` sp1 ON sp1.employee = e1.name
            JOIN `tabSales Person` sp2
                ON sp2.lft BETWEEN sp1.lft AND sp1.rgt
            JOIN `tabEmployee` e2 ON e2.name = sp2.employee
            WHERE e1.user_id = {user}
        )
        """.format(user=frappe.db.escape(user))
    )

    # Unassigned leads ? Territory Tree
    from crm_permission_engine.permissions.utils import (
        get_user_managed_territory_bounds
    )

    ranges = get_user_managed_territory_bounds(user)
    if ranges:
        territory_conditions = [
            "`tabTerritory`.`lft` BETWEEN {lft} AND {rgt}".format(
                lft=lft, rgt=rgt
            )
            for lft, rgt in ranges
        ]

        conditions.append(
            """
            (
                (`tabLead`.`lead_owner` IS NULL OR `tabLead`.`lead_owner` = '')
                AND `tabLead`.`territory` IN (
                    SELECT name FROM `tabTerritory`
                    WHERE {conds}
                )
            )
            """.format(conds=" OR ".join(territory_conditions))
        )

    return "(" + " OR ".join(conditions) + ")"