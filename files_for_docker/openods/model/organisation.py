import openods.model.role as role
import openods.model.address as address
from openods.model import model_utils

from openods import connection
from openods import constants
from openods import log_utils

ORG_TABLE_NAME = "organisations"
ORG_TABLE_ALIAS = "o"

def get_by_odscode(odscode, request_id, cursor):
    try:
        sql = "SELECT o.name, o.status, o.odscode, o.record_class, c.displayname, o.operational_start_date, " \
              "o.operational_end_date, o.legal_start_date, o.legal_end_date, o.last_changed, o.ref_only " \
              "FROM organisations o " \
              "JOIN codesystems c " \
              "ON o.record_class = c.id " \
              "WHERE o.odscode = UPPER(%s) " \
              "AND c.name = 'OrganisationRecordClass' " \
              "LIMIT 1;"

        data = (odscode,)

        log_utils.log_database_query_statement(request_id, str.format(sql, data))

        cursor.execute(sql, data)
        organisation = cursor.fetchone()

        log_utils.log_database_return(request_id, organisation)

    except Exception:
        raise

    return organisation


def get_orgs_last_changed_since(last_changed_since, request_id):
    try:
        sql = "SELECT odscode " \
              "FROM organisations " \
              "WHERE last_changed >= %s;"
        data = (last_changed_since,)


        with connection.get_db_cursor(request_id) as cursor:
            log_utils.log_database_query_statement(request_id, str.format(sql, data))

            cursor.execute(sql, data)
            organisation = cursor.fetchall()

            log_utils.log_database_return(request_id, organisation)

    except Exception:
        raise

    return organisation


def get_where_statement_for_ord_orgname_search(name, where_sql, table_dict, request_id):
    model_utils.add_table_and_alias_to_dict(table_dict, ORG_TABLE_NAME, ORG_TABLE_ALIAS)

    query_param = str.format("%{0}%", name)

    where_sql.append("UPPER(" + ORG_TABLE_ALIAS + ".name) LIKE UPPER(%s)")

    return query_param


def get_where_statement_for_ord_last_changed_since_search(last_changed_since, where_sql, table_dict, request_id):
    model_utils.add_table_and_alias_to_dict(table_dict, ORG_TABLE_NAME, ORG_TABLE_ALIAS)

    query_param = str.format("{0}", last_changed_since)

    where_sql.append("%s <= " + ORG_TABLE_ALIAS + ".last_changed")

    return query_param


def get_where_statement_for_ord_status_search(status, where_sql, table_dict, request_id):
    model_utils.add_table_and_alias_to_dict(table_dict, ORG_TABLE_NAME, ORG_TABLE_ALIAS)

    query_param = str.format("{0}", status)

    where_sql.append("UPPER(" + ORG_TABLE_ALIAS + ".status) LIKE UPPER(%s)")

    return query_param

def get_where_statement_for_ord_record_class_search(record_class, where_sql, table_dict, request_id):
    model_utils.add_table_and_alias_to_dict(table_dict, ORG_TABLE_NAME, ORG_TABLE_ALIAS)

    query_param = str.format("{0}", record_class)

    where_sql.append("UPPER(" + ORG_TABLE_ALIAS + ".record_class) LIKE UPPER(%s)")

    return query_param


def get_ord_orgs_summary_from_db(select_sql, result_data, count_data, table_dict, request_id):

    model_utils.add_table_and_alias_to_dict(table_dict, ORG_TABLE_NAME, ORG_TABLE_ALIAS)
    model_utils.add_table_and_alias_to_dict(table_dict, role.ROLE_TABLE_NAME, role.ROLE_TABLE_ALIAS)
    model_utils.add_table_and_alias_to_dict(table_dict, address.ADDRESS_TABLE_NAME, address.ADDRESS_TABLE_ALIAS)
    model_utils.add_table_and_alias_to_dict(table_dict, "codesystems", "c")

    organisations = {}
    if len(select_sql) < 1:
        return organisations, 0

    try:
        result_sql = "SELECT " + ORG_TABLE_ALIAS + ".name, "
        result_sql += ORG_TABLE_ALIAS + ".odscode, "
        result_sql += address.ADDRESS_TABLE_ALIAS + ".post_code, "
        result_sql += ORG_TABLE_ALIAS + ".record_class, "
        result_sql += ORG_TABLE_ALIAS + ".status, "
        result_sql += ORG_TABLE_ALIAS + ".last_changed, "
        result_sql += role.ROLE_TABLE_ALIAS + ".code, "
        result_sql += "c.displayname "

        count_sql = "SELECT COUNT(1) "

        sql = "FROM " + hashset_csv(table_dict)

        sql += " WHERE " + ORG_TABLE_ALIAS + ".odscode = " + role.ROLE_TABLE_ALIAS + ".org_odscode "
        sql += "AND " + ORG_TABLE_ALIAS + ".odscode = " + address.ADDRESS_TABLE_ALIAS + ".org_odscode "
        sql += "AND " + role.ROLE_TABLE_ALIAS + ".primary_role = 'TRUE' "
        sql += "AND c.name = 'OrganisationRole' "
        sql += "AND c.id = " + role.ROLE_TABLE_ALIAS + ".code "

        sql += generate_query_sql_AND_clauses(select_sql, startWithWhere=False)

        count_sql += sql

        sql += "ORDER BY " + ORG_TABLE_ALIAS + ".name, " + ORG_TABLE_ALIAS + ".odscode "
        sql += "OFFSET %s "
        sql += "LIMIT %s"

        result_sql += sql


        with connection.get_db_cursor(request_id) as cursor:

            log_utils.log_database_query_statement(request_id, str.format(count_sql, count_data))

            cursor.execute(count_sql, count_data)
            count = cursor.fetchone()['count']

            log_utils.log_database_return(request_id, count)

            log_utils.log_database_query_statement(request_id, str.format(result_sql, result_data))

            cursor.execute(result_sql, result_data)
            organisations = cursor.fetchall()

            log_utils.log_database_return(request_id, organisations)

    except Exception:
        raise

    return organisations, count


def hashset_csv(hashset):
    text = ""
    count2 = 0
    for key, value in dict.items(hashset):
        count1 = 0
        for v in value:
            text += key + " " + v
            if (count1 < len(value) - 1):
                text += ", "
            count1 += 1
        if count2 < (len(hashset) - 1):
            text += ", "
        count2 += 1
    return text


def generate_query_sql_AND_clauses(sql_snippets, startWithWhere):
    sql = ""
    count = 0
    for statement in sql_snippets:
        if count == 0 and startWithWhere:
            sql += "WHERE " + statement + " "
        else:
            sql += "AND " + statement + " "
        count += 1
    return sql

def get_where_statement_for_fhir_name_search(name, where_sql, request_id):
    query_param = str.format("{0}%", name)

    where_sql.append("UPPER(" + ORG_TABLE_ALIAS + ".name) LIKE UPPER(%s)")

    return query_param

def get_where_statement_for_fhir_name_contains_search(name, where_sql, request_id):
    query_param = str.format("%{0}%", name)

    where_sql.append("UPPER(" + ORG_TABLE_ALIAS + ".name) LIKE UPPER(%s)")

    return query_param

def get_where_statement_for_fhir_name_exact_search(name, where_sql, request_id):
    query_param = str.format("{0}", name)

    where_sql.append(ORG_TABLE_ALIAS + ".name = %s")

    return query_param

def get_where_statement_for_fhir_active_bool_search(active_bool, where_sql, request_id):
    if active_bool == constants.FHIR_ACTIVE_ARG:
        status = constants.STATUS_ACTIVE
    else:
        status = constants.STATUS_INACTIVE

    query_param = str.format("{0}", status)

    where_sql.append(ORG_TABLE_ALIAS + ".status = %s")

    return query_param

def get_where_statement_for_fhir_last_updated(date, where_sql, request_id):
    date = extrapolate_fhir_date(date)

    query_param = str.format("{0}", date)

    where_sql.append("%s < " + ORG_TABLE_ALIAS + ".last_changed")

    return query_param


def extrapolate_fhir_date(date):
    date = date[2:] # remove gt

    if len(date) == 4: #YYYY
        date += "-01-01"
    if len(date) == 7: #YYYY-MM
        date += "-01"

    return date

def get_where_statement_for_fhir_identifier(id, where_sql, request_id):
    query_param = str.format("{0}", id)

    where_sql.append(ORG_TABLE_ALIAS + ".odscode = %s")

    return query_param

def get_fhir_ods_codes_from_db(select_sql, table_dict, count_data, result_data, request_id):
    try:
        result_sql = "SELECT DISTINCT " + ORG_TABLE_ALIAS + ".odscode "

        count_sql = "SELECT COUNT(DISTINCT(" + ORG_TABLE_ALIAS + ".odscode)) "

        sql = "FROM " + ORG_TABLE_NAME + " " + ORG_TABLE_ALIAS + " "

        if table_dict:
            sql += create_joins(table_dict)

        sql += generate_query_sql_AND_clauses(select_sql, startWithWhere=True)

        count_sql += sql

        sql += "ORDER BY " + ORG_TABLE_ALIAS + ".odscode "
        sql += "OFFSET %s "
        sql += "LIMIT %s"

        result_sql += sql

        with connection.get_db_cursor(request_id) as cursor:

            log_utils.log_database_query_statement(request_id, str.format(sql, result_data))

            cursor.execute(result_sql, result_data)
            organisations = cursor.fetchall()

            log_utils.log_database_return(request_id, organisations)

            log_utils.log_database_query_statement(request_id, str.format(sql, count_data))

            cursor.execute(count_sql, count_data)
            count = cursor.fetchone()['count']

            log_utils.log_database_return(request_id, count)

    except Exception as e:
        print(e)
        raise

    return organisations, count


def create_joins(table_dict):
    sql = ""

    for key, value in table_dict.items():
        for alias in value:
            sql += "JOIN"
            sql += " " + key + " " + alias
            sql += " ON"
            sql += " o.odscode=" + alias + ".org_odscode "

    return sql