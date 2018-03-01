from openods.model import organisation, address, contact, role, version, relationship, successor, codesystem

from openods import connection
from openods import constants
from openods import exception


def get_org_data(ods_code, request_id, is_fhir):
    with connection.get_db_cursor(request_id) as cursor:
        org_organisation = organisation.get_by_odscode(ods_code, request_id, cursor)
        if org_organisation is None:
            raise exception.UnfoundOrgError

        org_address = address.get_for_odscode(ods_code, request_id, cursor)
        org_role = role.get_for_odscode(ods_code, request_id, cursor)
        org_contact = contact.get_for_odscode(ods_code, request_id, cursor)
        org_relationships = None
        org_successors = None
        if not is_fhir:
            org_relationships= relationship.get_for_odscode(ods_code, request_id, cursor)
            org_successors = successor.get_for_odscode(ods_code, request_id, cursor)

    return org_organisation, org_address, org_role, org_contact, org_relationships, org_successors

# ORD

def get_ord_orgs_summary(request_args, limit, offset, request_id):
    where_sql, count_data, table_dict = get_ord_where_sql_data(request_args, request_id)

    result_data = count_data  + (offset, limit)

    orgs, total_record_count = organisation.get_ord_orgs_summary_from_db(where_sql, result_data, count_data, table_dict, request_id)

    returned_record_count = len(orgs)

    return orgs, total_record_count, returned_record_count


def get_ord_where_sql_data(request_args, request_id):

    table_dict = {}
    where_sql = []
    data = ()


    name = request_args.get(constants.ORG_NAME)
    if name:
        query_param = organisation.get_where_statement_for_ord_orgname_search(name, where_sql, table_dict, request_id)
        data = data + (query_param,)

    last_changed_since = request_args.get(constants.LAST_CHANGED_SINCE)
    if last_changed_since:
        query_param = organisation.get_where_statement_for_ord_last_changed_since_search(last_changed_since, where_sql,
                                                                                         table_dict, request_id)
        data = data + (query_param,)

    postcode = request_args.get(constants.POSTCODE)
    if postcode:
        query_param = address.get_where_statement_for_ord_postcode_search(postcode, where_sql, table_dict, request_id)
        data = data + (query_param,)

    status = request_args.get(constants.STATUS)
    if status:
        query_param = organisation.get_where_statement_for_ord_status_search(status, where_sql, table_dict, request_id)
        data = data + (query_param,)

    primary_role_code = request_args.get(constants.PRIMARY_ROLE_CODE)
    if primary_role_code:
        query_param = role.get_where_statement_for_ord_primary_role_code_search(primary_role_code, where_sql, table_dict,
                                                                                request_id)
        data = data + (query_param,)

    non_primary_role_code = request_args.get(constants.NON_PRIMARY_ROLE_CODE)
    if non_primary_role_code:
        query_param = role.get_where_statement_for_ord_non_primary_role_code_search(non_primary_role_code, where_sql,
                                                                                    table_dict, request_id)
        data = data + (query_param,)

    record_class = request_args.get(constants.RECORD_CLASS)
    if record_class:
        query_param = organisation.get_where_statement_for_ord_record_class_search(record_class, where_sql, table_dict,
                                                                                   request_id)
        data = data + (query_param,)

    count_data = data
    return where_sql, count_data,  table_dict


def get_ord_ods_codes_last_changed_since(request_args, request_id):

    last_changed_since = request_args.get(constants.LAST_CHANGED_SINCE)

    ods_codes = organisation.get_orgs_last_changed_since(last_changed_since, request_id)

    return ods_codes

#FHIR

def get_fhir_ods_codes(request_args, page, limit, request_id):
    where_sql, count_data, table_dict = get_fhir_where_sql(request_args, request_id)

    result_data  = count_data + ((int(float(page)) - 1) * int(float(limit)), limit)

    ods_codes, total_record_count = organisation.get_fhir_ods_codes_from_db(where_sql, table_dict, count_data,
                                                                            result_data, request_id)
    returned_record_count = len(ods_codes)

    return ods_codes, total_record_count, returned_record_count

def get_fhir_where_sql(request_args, request_id):
    table_dict = {}
    where_sql = []
    data = ()

    nameList = request_args.getlist(constants.FHIR_ORG_NAME)
    for name in nameList:
        query_param = organisation.get_where_statement_for_fhir_name_search(name, where_sql, request_id)
        data = data + (query_param,)

    nameContainsList = request_args.getlist(constants.FHIR_ORG_NAME_CONTAINS)
    for name in nameContainsList:
        query_param = organisation.get_where_statement_for_fhir_name_contains_search(name, where_sql, request_id)
        data = data + (query_param,)

    nameEqualsList = request_args.getlist(constants.FHIR_ORG_NAME_EXACT)
    for name in nameEqualsList:
        query_param = organisation.get_where_statement_for_fhir_name_exact_search(name, where_sql, request_id)
        data = data + (query_param,)

    postcodeList = request_args.getlist(constants.FHIR_POSTCODE)
    for postcode in postcodeList:
        query_param = address.get_where_statement_for_fhir_postcode_search(postcode, where_sql, table_dict, request_id)
        data = data + (query_param,)

    postcodeContainsList = request_args.getlist(constants.FHIR_POSTCODE_CONTAINS)
    for postcode in postcodeContainsList:
        query_param = address.get_where_statement_for_fhir_postcode_contains_search(postcode, where_sql, table_dict,
                                                                                    request_id)
        data = data + (query_param,)

    postcodeEqualsList = request_args.getlist(constants.FHIR_POSTCODE_EXACT)
    for postcode in postcodeEqualsList:
        query_param = address.get_where_statement_for_fhir_postcode_exact_search(postcode, where_sql, table_dict,
                                                                                 request_id)
        data = data + (query_param,)

    address_cityList = request_args.getlist(constants.FHIR_ADDRESS_CITY)
    for city in address_cityList:
        query_param = address.get_where_statement_for_fhir_city_search(city, where_sql, table_dict, request_id)

        data = data + (query_param,)

    address_cityContainsList = request_args.getlist(constants.FHIR_ADDRESS_CITY_CONTAINS)
    for city in address_cityContainsList:
        query_param = address.get_where_statement_for_fhir_city_contains_search(city, where_sql, table_dict, request_id)

        data = data + (query_param,)

    address_cityExactList = request_args.getlist(constants.FHIR_ADDRESS_CITY_EXACT)
    for city in address_cityExactList:
        query_param = address.get_where_statement_for_fhir_city_exact_search(city, where_sql, table_dict, request_id)
        data = data + (query_param,)

    active_boolList = request_args.getlist(constants.FHIR_STATUS_ARG)
    for active_bool in active_boolList:
        query_param = organisation.get_where_statement_for_fhir_active_bool_search(active_bool, where_sql, request_id)
        data = data + (query_param,)

    last_updatedList = request_args.getlist(constants.FHIR_LAST_UPDATED)
    for date in last_updatedList:
        query_param = organisation.get_where_statement_for_fhir_last_updated(date, where_sql, request_id)
        data = data + (query_param,)

    roleList = request_args.getlist(constants.FHIR_ROLE)
    primaryRole = request_args.get(constants.FHIR_PRIMARY_ROLE)
    role_idx = 1
    for rolearg in roleList:
        query_param = role.get_where_statement_for_fhir_role(rolearg, primaryRole, role_idx, table_dict, where_sql,
                                                             request_id)
        data = data + query_param
        role_idx += 1

    identifiers = request_args.getlist(constants.FHIR_IDENTIFIER)
    for identifier in identifiers:

        if "|" in identifier:
            tmp = identifier.split("|")
            identifier = tmp[1]

        query_param = organisation.get_where_statement_for_fhir_identifier(identifier, where_sql, request_id)
        data = data + (query_param,)

    ids = request_args.getlist(constants.FHIR_ID)
    for id in ids:
        query_param = organisation.get_where_statement_for_fhir_identifier(id, where_sql, request_id)
        data = data + (query_param,)

    count_data = data

    return where_sql, count_data, table_dict


def get_fhir_roles_codesystem(request_id):

    organisation_roles_dict = codesystem.get_organisation_roles(request_id)

    return organisation_roles_dict

