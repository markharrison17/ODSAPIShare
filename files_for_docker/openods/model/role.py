from openods.model import organisation
from openods.model import model_utils

from openods import log_utils
from openods import connection

ROLE_TABLE_NAME = "roles"
ROLE_TABLE_ALIAS = "r"
ROLE_TABLE_ALIAS2 = "r2"


def get_for_odscode(odscode, request_id, cursor):

    try:
        sql = "SELECT r.code, r.unique_id, c.displayname, r.primary_role, r.status, r.operational_start_date, r.operational_end_date, " \
              "r.legal_start_date, r.legal_end_date " \
              "FROM roles r " \
              "JOIN codesystems c " \
              "ON r.code = c.id " \
              "WHERE r.org_odscode = UPPER(%s) " \
              "AND c.name = 'OrganisationRole';"

        data = (odscode,)

        log_utils.log_database_query_statement(request_id, str.format(sql, data))

        cursor.execute(sql, data)
        roles = cursor.fetchall()

        log_utils.log_database_return(request_id, roles)

    except Exception:
        raise

    return roles


def get_where_statement_for_ord_primary_role_code_search(primary_role_code, where_sql, table_dict, request_id):
    model_utils.add_table_and_alias_to_dict(table_dict, ROLE_TABLE_NAME, ROLE_TABLE_ALIAS)

    query_param = str.format("{0}", primary_role_code)

    where_sql.append("UPPER(" + ROLE_TABLE_ALIAS + ".code) LIKE UPPER(%s)")

    return query_param


def get_where_statement_for_ord_non_primary_role_code_search(non_primary_role_code, where_sql, table_dict, request_id):
    model_utils.add_table_and_alias_to_dict(table_dict, ROLE_TABLE_NAME, ROLE_TABLE_ALIAS2)
    query_param = str.format("{0}", non_primary_role_code)

    where_sql.append(organisation.ORG_TABLE_ALIAS + ".odscode = " + ROLE_TABLE_ALIAS2 + ".org_odscode")
    where_sql.append(ROLE_TABLE_ALIAS2 + ".primary_role = 'FALSE'")
    where_sql.append("UPPER(" + ROLE_TABLE_ALIAS2 + ".code) LIKE UPPER(%s)")

    return query_param


def get_where_statement_for_fhir_role(rolearg, primaryRole, role_idx, table_dict, where_sql, request_id):
    sql = ""
    query_param = ()

    alias = ROLE_TABLE_ALIAS + str(role_idx)
    model_utils.add_table_and_alias_to_dict(table_dict, ROLE_TABLE_NAME, alias)

    if "|" in rolearg:
        rolearg = rolearg.split("|")[1]

    roles = rolearg.split(",")

    sql += alias + ".code in ("
    count = 0
    for role in roles:
        query_param = query_param + (str.format("RO{0}", role),)
        if count > 0:
            sql += ","
        sql += "%s"
        count += 1
    sql += ")"

    if primaryRole is not None:
        sql += " AND " + alias + ".primary_role = %s"
        query_param = query_param + (str.format("{0}", primaryRole),)

    where_sql.append(sql)

    return query_param