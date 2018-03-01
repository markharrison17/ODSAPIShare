import re

from openods.model import model_utils

from openods import log_utils
from openods import connection

ADDRESS_TABLE_NAME = "addresses"
ADDRESS_TABLE_ALIAS = "a"


def get_for_odscode(odscode, request_id, cursor):
    try:
        sql = "SELECT address_line1, " \
              "address_line2, " \
              "address_line3, " \
              "town, county, " \
              "post_code, " \
              "country  " \
              "FROM addresses a " \
              "WHERE a.org_odscode = UPPER(%s);"

        data = (odscode,)
        log_utils.log_database_query_statement(request_id, str.format(sql, data))

        cursor.execute(sql, data)
        address = cursor.fetchone()

        log_utils.log_database_return(request_id, address)

    except Exception:
        raise

    return address


def get_where_statement_for_ord_postcode_search(postcode, where_sql, table_dict, request_id):
    model_utils.add_table_and_alias_to_dict(table_dict, ADDRESS_TABLE_NAME, ADDRESS_TABLE_ALIAS)

    outbound_postcode = r'^((([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]))|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2}))|([A-Za-z][0-9]{1,2}))$'

    if (len(postcode.replace(" ","")) != len(postcode)):
        query_param = str.format("{0}%", postcode)
        where_sql.append("UPPER(" + ADDRESS_TABLE_ALIAS + ".post_code) LIKE UPPER(%s)")
    else:
        match = re.match(outbound_postcode, postcode)
        if (match and (len(postcode.replace(" ","")) == len((match.group(0)).replace(" ","")))):
            query_param = str.format("{0} %", postcode)
            where_sql.append("UPPER(" + ADDRESS_TABLE_ALIAS + ".post_code) LIKE UPPER(%s)")
        else:
            query_param = str.format("{0}%", postcode)
            where_sql.append("REPLACE(UPPER(" + ADDRESS_TABLE_ALIAS + ".post_code),' ','') LIKE UPPER(%s)")

    return query_param

def get_where_statement_for_fhir_postcode_search(postcode, where_sql, table_dict, request_id):
    model_utils.add_table_and_alias_to_dict(table_dict, ADDRESS_TABLE_NAME, ADDRESS_TABLE_ALIAS)

    query_param = str.format("{0}%", postcode)

    where_sql.append("UPPER(" + ADDRESS_TABLE_ALIAS + ".post_code) LIKE UPPER(%s)")


    return query_param


def get_where_statement_for_fhir_postcode_contains_search(postcode, where_sql, table_dict, request_id):
    model_utils.add_table_and_alias_to_dict(table_dict, ADDRESS_TABLE_NAME, ADDRESS_TABLE_ALIAS)

    query_param = str.format("%{0}%", postcode)

    where_sql.append("UPPER(" + ADDRESS_TABLE_ALIAS + ".post_code) LIKE UPPER(%s)")

    return query_param

def get_where_statement_for_fhir_postcode_exact_search(postcode, where_sql, table_dict, request_id):
    model_utils.add_table_and_alias_to_dict(table_dict, ADDRESS_TABLE_NAME, ADDRESS_TABLE_ALIAS)

    query_param = str.format("{0}", postcode)

    where_sql.append(ADDRESS_TABLE_ALIAS + ".post_code = %s")

    return query_param

def get_where_statement_for_fhir_city_search(city, where_sql, table_dict, request_id):
    model_utils.add_table_and_alias_to_dict(table_dict, ADDRESS_TABLE_NAME, ADDRESS_TABLE_ALIAS)

    query_param = str.format("{0}%", city)

    where_sql.append("UPPER(" + ADDRESS_TABLE_ALIAS + ".town) LIKE UPPER(%s)")

    return query_param

def get_where_statement_for_fhir_city_contains_search(city, where_sql, table_dict, request_id):
    model_utils.add_table_and_alias_to_dict(table_dict, ADDRESS_TABLE_NAME, ADDRESS_TABLE_ALIAS)

    query_param = str.format("%{0}%", city)

    where_sql.append("UPPER(" + ADDRESS_TABLE_ALIAS + ".town) LIKE UPPER(%s)")

    return query_param

def get_where_statement_for_fhir_city_exact_search(city, where_sql, table_dict, request_id):
    model_utils.add_table_and_alias_to_dict(table_dict, ADDRESS_TABLE_NAME, ADDRESS_TABLE_ALIAS)

    query_param = str.format("{0}", city)

    where_sql.append(ADDRESS_TABLE_ALIAS + ".town = %s")

    return query_param
