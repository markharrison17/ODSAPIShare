import collections
import datetime
import re
import uuid

from flask import Response, abort
from werkzeug.datastructures import ImmutableMultiDict

from openods.serialisation import serialisation_entry

from openods import constants
from openods import log_utils



def add_content_type_header_to_response(format, response):
    if format == constants.JSON:
        response.headers[constants.CONTENT_TYPE] = constants.APPLICATION_JSON
    else:
        response.headers[constants.CONTENT_TYPE] = constants.APPLICATION_XML


def determine_format(request, is_fhir):

    content_type = request.headers.get(constants.CONTENT_TYPE)
    if content_type == "": #Should not be needed but mocking a request adds a blank content type
        content_type = None
    url_args = request.args.get(constants.FORMAT)

    format, description = apply_formatting_logic(content_type, url_args, is_fhir)

    return format, description


def apply_formatting_logic(content_type, url_args, is_fhir):
    format = constants.JSON
    description = ""

    if is_fhir:
        json_content_types = [constants.FORMAT_FHIR_APPLICATION_JSON, constants.FORMAT_FHIR_APPLICATION_JSON_2]
        xml_content_types = [constants.FORMAT_FHIR_APPLICATION_XML, constants.FORMAT_FHIR_APPLICATION_XML_2]

        json_request_args = [constants.JSON, constants.TEXT_JSON, constants.APPLICATION_JSON,
                             constants.FORMAT_FHIR_APPLICATION_JSON]
        xml_request_args = [constants.XML, constants.TEXT_XML, constants.APPLICATION_XML,
                            constants.FORMAT_FHIR_APPLICATION_XML]
    else:
        json_content_types = [constants.APPLICATION_JSON]
        xml_content_types = [constants.APPLICATION_XML]

        json_request_args = [constants.JSON, constants.TEXT_JSON, constants.APPLICATION_JSON]
        xml_request_args = [constants.XML, constants.TEXT_XML, constants.APPLICATION_XML]

    if content_type in json_content_types:
        format = constants.JSON
    elif content_type in xml_content_types:
        format = constants.XML
    elif content_type is not None:
        description = 'Unknown content type specified "{0}"'.format(content_type)
    elif url_args in json_request_args:
        format = constants.JSON
    elif url_args in xml_request_args:
        format = constants.XML
    elif url_args is not None:
        description = 'Unknown dialect specified "{0}"'.format(url_args)

    return format, description


def create_fhir_error(format, code, display, request_id, description):

    response = create_fhir_error_dict(code, display, description)

    formatted_response_body = serialisation_entry.create_response_body(response, format, request_id, True)

    return formatted_response_body


def create_fhir_error_dict(codes, displays, descriptions):
    response = collections.OrderedDict()

    response["resourceType"] = "OperationOutcome"
    response["id"] = str(uuid.uuid4())
    response["meta"] = {
        "profile": "https://fhir.nhs.uk/STU3/StructureDefinition/Spine-OperationOutcome-1"}

    issueList = []

    for code, display, description in zip(codes, displays, descriptions):
        issue = collections.OrderedDict()
        issue["severity"] = "error"
        issue["code"] = "invalid"
        detailsDict = collections.OrderedDict()
        codingDict = collections.OrderedDict()
        codingDict["system"] = "https://fhir.nhs.uk/STU3/CodeSystem/Spine-ErrorOrWarningCode-1"
        codingDict["code"] = code
        codingDict["display"] = display
        detailsDict["coding"] = codingDict
        issue["details"] = detailsDict
        if description:
            issue["diagnostics"] = description
        issueList.append(issue)

    response["issue"] = issueList

    return response

def convert_to_fhir_error(code):
    display = ""

    if code == constants.INVALID_PARAMETER_ERROR:
        display = "Invalid parameter"
    elif code == constants.INVALID_VALUE_ERROR:
        display = "An input field has an invalid value for its type"
    elif code == constants.INVALID_CODE_SYSTEM_ERROR:
        display = "Invalid code system"
    elif code == constants.INVALID_CODE_VALUE_ERROR:
        display = "Invalid code value"
    elif code == constants.ACCESS_DENIED:
        display = "Access has been denied to process this request"
    elif code == constants.INVALID_IDENTIFIER_SYSTEM_ERROR:
        display = "Invalid identifier system"
    elif code == constants.INVALID_IDENTIFIER_VALUE_ERROR:
        display = "Invalid identifier value"
    elif code == constants.NO_RECORD_FOUND_ERROR:
        display = "No record found"


    return display

def create_fhir_error_response(format, codes, request_id, descriptions, status):
    displays = []
    for c in codes:
        displays.append(convert_to_fhir_error(c))
    resp_data = create_fhir_error(format, codes, displays, request_id, descriptions)
    status_dict = {"Status": status}
    response = Response(resp_data, status, status_dict)
    add_content_type_header_to_response(format, response)

    log_utils.log_handler_exit(request_id, status, descriptions)

    return response

def ord_error_log_and_abort(abort_number, error_description, request_id):
    log_utils.log_handler_exit(request_id, abort_number, error_description)
    abort(abort_number, error_description)

def valid_format(format):
    return True if format == constants.JSON or format == constants.XML else False


def isValidOdsCodeAPIRequest(request):
    args_list = [constants.FORMAT]

    valid, description = isRequestArgsValid(request, args_list, isFhir=False, argsRequired=False)
    if not valid:
        return valid, description

    return True, ""


def isValidFHIROdsCodeAPIRequest(request):
    final_valid = True
    descriptions = []
    codes = []

    args_list = [constants.FORMAT]

    valid, description_list = isFhirRequestArgsValid(request, args_list)
    if not valid:
        final_valid = False
        for description in description_list:
            descriptions.append(description)
            codes.append(constants.INVALID_PARAMETER_ERROR)

    return final_valid, descriptions, codes

    # valid, description = isFhirRequestArgsValid(request, args_list)
    # if not valid:
    #     return valid, description, constants.INVALID_PARAMETER_ERROR
    #
    # return True, "", ""


def isValidFHIRCapabilitiesOrRolesRequest(request):
    final_valid = True
    descriptions = []
    codes = []

    args_list = [constants.FORMAT]

    valid, description_list = isFhirRequestArgsValid(request, args_list)
    if not valid:
        final_valid = False
        for description in description_list:
            descriptions.append(description)
            codes.append(constants.INVALID_PARAMETER_ERROR)

    return final_valid, descriptions, codes

    # valid, description = isRequestArgsValid(request, args_list, isFhir=True, argsRequired=False)
    # if not valid:
    #     return valid, description, constants.INVALID_PARAMETER_ERROR
    #
    # return True, "", ""


def isValidOrganisationAPIRequest(request):
    args_list = [constants.ORG_NAME, constants.POSTCODE, constants.LAST_CHANGED_SINCE,
                constants.STATUS, constants.PRIMARY_ROLE_CODE, constants.NON_PRIMARY_ROLE_CODE,
                constants.RECORD_CLASS, constants.LIMIT, constants.OFFSET, constants.FORMAT]

    valid, description = isRequestArgsValid(request, args_list, isFhir=False, argsRequired=True)
    if not valid:
        return valid, description

    org_name = request.args.get(constants.ORG_NAME)
    if org_name is not None:
        valid, description = isOrgNameValid(org_name)
        if not valid:
            return valid, description

    postcode = request.args.get(constants.POSTCODE)
    if postcode is not None:
        valid, description = isPostcodeValid(postcode)
        if not valid:
            return valid, description

    last_changed_since = request.args.get(constants.LAST_CHANGED_SINCE)
    if last_changed_since is not None:
        valid, description = isLastChangedSinceValid(last_changed_since)
        if not valid:
            return valid, description

    status = request.args.get(constants.STATUS)
    if status is not None:
        valid, description = isStatusValid(status)
        if not valid:
            return valid, description

    primary_role_code = request.args.get(constants.PRIMARY_ROLE_CODE)
    if primary_role_code is not None:
        valid, description = isRoleCodeValid(primary_role_code, constants.PRIMARY_ROLE_CODE)
        if not valid:
            return valid, description

    non_primary_role_code = request.args.get(constants.NON_PRIMARY_ROLE_CODE)
    if non_primary_role_code is not None:
        valid, description = isRoleCodeValid(non_primary_role_code, constants.NON_PRIMARY_ROLE_CODE)
        if not valid:
            return valid, description

    record_class = request.args.get(constants.RECORD_CLASS)
    if record_class is not None:
        valid, description = isRecordClassValid(record_class)
        if not valid:
            return valid, description

    limit = request.args.get(constants.LIMIT)
    if limit is not None:
        valid, description = isLimitValid(limit)
        if not valid:
            return valid, description

    offset = request.args.get(constants.OFFSET)
    if offset is not None:
        valid, description = isOffsetValid(offset)
        if not valid:
            return valid, description

    return True, ""


def isOrgNameValid(org_name):
    if len(org_name) < 3:
        return False, constants.ORG_NAME_TOO_SHORT
    if len(org_name) > 100:
        return False, constants.ORG_NAME_TOO_LONG
    match = re.match(r'[a-zA-Z0-9_@&.()\'" /:,+;-]*$', org_name)
    if not match:
        return False, constants.ORG_NAME_INVALID_CHARACTER

    return True, ""


def isLastChangedSinceValid(last_changed_since):
    match = re.match('(\d{4}-\d{2}-\d{2})', last_changed_since)
    if not match:
        return False, constants.INVALID_DATE_FORMAT
    if len(last_changed_since) != 10:
        return False, constants.INVALID_DATE_FORMAT

    try:
        date = datetime.date(*(int(s) for s in last_changed_since.split('-')))
    except:
        return False, constants.INVALID_DATE

    current_datetime = datetime.datetime.now()
    current_date = current_datetime.date()

    if date > current_date:
        return False, constants.INVALID_FUTURE_DATE
    if date < current_date - datetime.timedelta(days=185):
        return False, constants.INVALID_PAST_DATE

    return True, ""


def isRequestArgsValid(request, validArgs, isFhir, argsRequired):
    request_copy = ImmutableMultiDict.copy(request.args)
    request_dict = {}
    required_arg = 0

    if isFhir and constants.FHIR_PRIMARY_ROLE in request_copy and constants.FHIR_ROLE not in request_copy:
        return False, constants.FHIR_PRIMARY_ROLE_WITHOUT_ROLE

    for arg in validArgs:
        list = request_copy.getlist(arg)
        if (len(list) > 1 and not isFhir):
            return False, str.format(constants.REPEATED_ARGUMENT, arg)
        elif isFhir and (len(list) > 1) and (arg is constants.FORMAT or arg is constants.FHIR_PAGE or arg is constants.FHIR_LIMIT or arg is constants.FHIR_SUMMARY):
            return False, str.format(constants.REPEATED_ARGUMENT, arg)
        elif (len(list) == 1 or (len(list) > 1 and isFhir)):
            request_dict[arg] = request_copy.pop(arg)
            if arg is not constants.OFFSET and arg is not constants.LIMIT and arg is not constants.FORMAT:
                required_arg+=1
    if (len(request_copy) > 0):
        return False, constants.UNKNOWN_REQUEST_ARG

    if argsRequired and required_arg < 1 and not isFhir:
        return False, constants.INSUFFICIANT_REQUIRED_ARGS

    return True, ""


def isPostcodeValid(postcode):
    # Allow partial postcode matches, eg LS postcode district for all of Leeds.
    if len(postcode) < 2:
        return False, constants.POSTCODE_TOO_SHORT
    elif len(postcode) > 8:
        return False, constants.POSTCODE_INVALID

    mod_uk_govmt_postcode_regex2 = r'^([Gg][Ii][Rr][ ]?0?[Aa]?[Aa]?)|(((([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]))|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2}))|([A-Za-z][0-9]{1,2}))[ ]?[0-9]?[A-Za-z]?[A-Za-z]?)$'
    match = re.match(mod_uk_govmt_postcode_regex2, postcode)

    if not (match and len(postcode.replace(' ','')) == len((match.group(0)).replace(' ',''))):
        return False, constants.POSTCODE_INVALID

    return True, ""


def isStatusValid(status):
    if status.upper() != constants.ACTIVE and status.upper() != constants.INACTIVE:
        return False, constants.STATUS_UNKNOWN

    return True, ""


def isRoleCodeValid(role_code, role_code_type):
    if len(role_code) > 10:
        return False, str.format(constants.INVALID_ROLE_CODE, role_code_type)
    if len(role_code) < 3:
        return False, str.format(constants.INVALID_ROLE_CODE, role_code_type)
    if not role_code.isalnum():
        return False, str.format(constants.INVALID_ROLE_CODE, role_code_type)

    return True, ""


def isRecordClassValid(record_class):
    if len(record_class) > 3:
        return False, constants.INVALID_RECORD_CLASS
    if len(record_class) < 3:
        return False, constants.INVALID_RECORD_CLASS
    if not record_class.isalnum():
        return False, constants.INVALID_RECORD_CLASS

    return True, ""


def isLimitValid(limit):
    if not limit.isdigit():
        return False, constants.INVALID_LIMIT
    limit = int(float(limit))
    if limit < constants.LIMIT_MIN:
        return False, constants.INVALID_LIMIT
    if limit > constants.LIMIT_MAX:
        return False, constants.INVALID_LIMIT

    return True, ""


def isOffsetValid(offset):
    if not offset.isdigit():
        return False, constants.INVALID_OFFSET
    offset = int(float(offset))
    if offset < constants.OFFSET_MIN:
        return False, constants.INVALID_OFFSET

    return True, ""


def isValidSyncAPIRequest(request):
    args_list = [constants.LAST_CHANGED_SINCE, constants.FORMAT]

    valid, description = isRequestArgsValid(request, args_list, isFhir=False, argsRequired=True)

    if valid:
        valid, description = isLastChangedSinceValid(request.args.get(constants.LAST_CHANGED_SINCE))

    return valid, description


def isValidFHIROrganisationAPIRequest(request):
    final_valid = True
    descriptions = []
    codes = []

    args_list = [constants.FHIR_ORG_NAME, constants.FHIR_ORG_NAME_CONTAINS,
                 constants.FHIR_ORG_NAME_EXACT,
                 constants.FORMAT, constants.FHIR_POSTCODE, constants.FHIR_POSTCODE_CONTAINS,
                 constants.FHIR_POSTCODE_EXACT, constants.FHIR_STATUS_ARG,
                 constants.FHIR_ADDRESS_CITY, constants.FHIR_ADDRESS_CITY_CONTAINS, constants.FHIR_ADDRESS_CITY_EXACT,
                 constants.FHIR_PRIMARY_ROLE, constants.FHIR_ROLE, constants.FHIR_LAST_UPDATED,
                 constants.FHIR_IDENTIFIER, constants.FHIR_ID,
                 constants.FHIR_PAGE, constants.FHIR_LIMIT, constants.FORMAT, constants.FHIR_SUMMARY]

    valid, description_list = isFhirRequestArgsValid(request, args_list)
    if not valid:
        # return valid, description, constants.INVALID_PARAMETER_ERROR
        final_valid = False
        for description in description_list:
            descriptions.append(description)
            codes.append(constants.INVALID_PARAMETER_ERROR)

    name_start = request.args.getlist(constants.FHIR_ORG_NAME)
    for x in name_start:
        valid, description = isFhirOrgNameValid(x, constants.FHIR_ORG_NAME)
        if not valid:
            # return valid, description, constants.INVALID_VALUE_ERROR
            final_valid = False
            descriptions.append(description)
            codes.append(constants.INVALID_VALUE_ERROR)

    name_contain = request.args.getlist(constants.FHIR_ORG_NAME_CONTAINS)
    for x in name_contain:
        valid, description = isFhirOrgNameValid(x, constants.FHIR_ORG_NAME_CONTAINS)
        if not valid:
            # return valid, description, constants.INVALID_VALUE_ERROR
            final_valid = False
            descriptions.append(description)
            codes.append(constants.INVALID_VALUE_ERROR)

    name_exact = request.args.getlist(constants.FHIR_ORG_NAME_EXACT)
    for x in name_exact:
        valid, description = isFhirOrgNameValid(x, constants.FHIR_ORG_NAME_EXACT)
        if not valid:
            # return valid, description, constants.INVALID_VALUE_ERROR
            final_valid = False
            descriptions.append(description)
            codes.append(constants.INVALID_VALUE_ERROR)

    postcode_start = request.args.getlist(constants.FHIR_POSTCODE)
    for x in postcode_start:
        valid, description = isFhirPostcodeValid(x)
        if not valid:
            # return valid, description, constants.INVALID_VALUE_ERROR
            final_valid = False
            descriptions.append(description)
            codes.append(constants.INVALID_VALUE_ERROR)

    postcode_contain = request.args.getlist(constants.FHIR_POSTCODE_CONTAINS)
    for x in postcode_contain:
        valid, description = isFhirPostcodeValid(x)
        if not valid:
            # return valid, description, constants.INVALID_VALUE_ERROR
            final_valid = False
            descriptions.append(description)
            codes.append(constants.INVALID_VALUE_ERROR)

    postcode_exact = request.args.getlist(constants.FHIR_POSTCODE_EXACT)
    for x in postcode_exact:
        valid, description = isFhirPostcodeValid(x)
        if not valid:
            # return valid, description, constants.INVALID_VALUE_ERROR
            final_valid = False
            descriptions.append(description)
            codes.append(constants.INVALID_VALUE_ERROR)

    address_start = request.args.getlist(constants.FHIR_ADDRESS_CITY)
    for x in address_start:
        valid, description = isFhirAddressCityValid(x)
        if not valid:
            # return valid, description, constants.INVALID_VALUE_ERROR
            final_valid = False
            descriptions.append(description)
            codes.append(constants.INVALID_VALUE_ERROR)

    address_contain = request.args.getlist(constants.FHIR_ADDRESS_CITY_CONTAINS)
    for x in address_contain:
        valid, description = isFhirAddressCityValid(x)
        if not valid:
            # return valid, description, constants.INVALID_VALUE_ERROR
            final_valid = False
            descriptions.append(description)
            codes.append(constants.INVALID_VALUE_ERROR)

    address_exact = request.args.getlist(constants.FHIR_ADDRESS_CITY_EXACT)
    for x in address_exact:
        valid, description = isFhirAddressCityValid(x)
        if not valid:
            # return valid, description, constants.INVALID_VALUE_ERROR
            final_valid = False
            descriptions.append(description)
            codes.append(constants.INVALID_VALUE_ERROR)

    active_bool = request.args.getlist(constants.FHIR_STATUS_ARG)
    for x in active_bool:
        valid, description = isFhirStatusValid(x)
        if not valid:
            # return valid, description, constants.INVALID_VALUE_ERROR
            final_valid = False
            descriptions.append(description)
            codes.append(constants.INVALID_VALUE_ERROR)

    primary_role = request.args.getlist(constants.FHIR_PRIMARY_ROLE)
    if primary_role:
        valid, description, code = isFhirPrimaryRoleValid(primary_role)
        if not valid:
            # return valid, description, code
            final_valid = False
            descriptions.append(description)
            codes.append(code)

    role = request.args.getlist(constants.FHIR_ROLE)
    for x in role:
        valid, description, code = isFhirRoleValid(x, request.url_root)
        if not valid:
            # return valid, description, code
            final_valid = False
            descriptions.append(description)
            codes.append(code)

    last_updated = request.args.getlist(constants.FHIR_LAST_UPDATED)
    for x in last_updated:
        valid, description = isFhirLastChangedDateValid(x)
        if not valid:
            # return valid, description, constants.INVALID_VALUE_ERROR
            final_valid = False
            descriptions.append(description)
            codes.append(constants.INVALID_VALUE_ERROR)

    identifier = request.args.getlist(constants.FHIR_IDENTIFIER)
    for x in identifier:
        valid, description, code = isFhirIdentifierValid(x)
        if not valid:
            # return valid, description, code
            final_valid = False
            descriptions.append(description)
            codes.append(code)

    ids = request.args.getlist(constants.FHIR_ID)
    for x in ids:
        valid, description = isFhirIdValid(x)
        if not valid:
            # return valid, description, constants.INVALID_VALUE_ERROR
            final_valid = False
            descriptions.append(description)
            codes.append(constants.INVALID_VALUE_ERROR)

    limit = request.args.get(constants.FHIR_LIMIT)
    if limit is not None:
        valid, description = isFhirLimitValid(limit)
        if not valid:
            # return valid, description, constants.INVALID_VALUE_ERROR
            final_valid = False
            descriptions.append(description)
            codes.append(constants.INVALID_VALUE_ERROR)

    page = request.args.get(constants.FHIR_PAGE)
    if page is not None:
        valid, description = isFhirPageValid(page)
        if not valid:
            # return valid, description, constants.INVALID_VALUE_ERROR
            final_valid = False
            descriptions.append(description)
            codes.append(constants.INVALID_VALUE_ERROR)

    summary = request.args.get(constants.FHIR_SUMMARY)
    if summary is not None:
        valid, description = isFhirSummaryValid(summary)
        if not valid:
            # return valid, description, constants.INVALID_VALUE_ERROR
            final_valid = False
            descriptions.append(description)
            codes.append(constants.INVALID_VALUE_ERROR)

    # return True, "", ""
    return final_valid, descriptions, codes


def isFhirRequestArgsValid(request, validArgs):
    request_copy = ImmutableMultiDict.copy(request.args)

    valid = True
    errors_list = []

    if constants.FHIR_PRIMARY_ROLE in request_copy and constants.FHIR_ROLE not in request_copy:
        valid = False
        errors_list.append(constants.FHIR_PRIMARY_ROLE_WITHOUT_ROLE)

    for key in request_copy:
        if key not in validArgs:
            valid = False
            errors_list.append(str.format(constants.UNKNOWN_FHIR_REQUEST_ARG, key))
        if (key is constants.FORMAT or key is constants.FHIR_PAGE or key is constants.FHIR_LIMIT or key is constants.FHIR_SUMMARY):
            list = request_copy.getlist(key)
            if len(list) > 1:
                valid = False
                errors_list.append(str.format(constants.REPEATED_ARGUMENT, key))

    if valid:
        return True, []
    else:
        return False, errors_list


def isFhirIdentifierValid(identifier):
    if "|" in identifier:
        tmp = identifier.split("|")
        system = tmp[0]
        if len(tmp) > 2:
            return False, constants.INVALID_FHIR_IDENTIFIER, constants.INVALID_IDENTIFIER_VALUE_ERROR
        elif system == constants.FHIR_ODSCODE_SYSTEM_URI:
            identifier = tmp[1]
        else:
            return False, constants.INVALID_FHIR_ODSCODE_SYSTEM_URI, constants.INVALID_IDENTIFIER_SYSTEM_ERROR

    if not identifier.isalnum():
        return False, constants.INVALID_FHIR_IDENTIFIER, constants.INVALID_IDENTIFIER_VALUE_ERROR
    return True, "", ""


def isFhirIdValid(identifier):
    if not identifier.isalnum():
        return False, constants.INVALID_FHIR_ID
    return True, ""


def isFhirSummaryValid(summary):
    if summary == constants.FHIR_SUMMARY_COUNT:
        return True, ""
    else:
        return False, constants.INVALID_FHIR_SUMMARY_PARAMETER


def isFhirOrgNameValid(org_name, param_name):
    if len(org_name) < 3:
        return False, str.format(constants.FHIR_ORG_NAME_TOO_SHORT, param_name)
    if len(org_name) > 100:
        return False, str.format(constants.FHIR_ORG_NAME_TOO_LONG, param_name)
    match = re.match(r'[a-zA-Z0-9_@&.()\'" /:,+;-]*$', org_name)
    if not match:
        return False, str.format(constants.FHIR_ORG_NAME_INVALID_CHARACTER, param_name)

    return True, ""


def isFhirLimitValid(limit):
    if not limit.isdigit():
        return False, constants.FHIR_INVALID_LIMIT
    limit = int(float(limit))
    if limit < constants.FHIR_LIMIT_MIN:
        return False, constants.FHIR_INVALID_LIMIT
    if limit > constants.FHIR_LIMIT_MAX:
        return False, constants.FHIR_INVALID_LIMIT

    return True, ""


def isFhirPageValid(page):
    if not page.isdigit():
        return False, constants.FHIR_INVALID_PAGE
    page = int(float(page))
    if page < constants.FHIR_PAGE_MIN:
        return False, constants.FHIR_INVALID_PAGE

    return True, ""


def isFhirPostcodeValid(postcode):
    if len(postcode) < 2:
        return False, constants.FHIR_POSTCODE_TOO_SHORT
    elif len(postcode) > 8:
        return False, constants.FHIR_INVALID_POSTCODE_TOO_LONG

    match = re.match(r"^([a-zA-Z0-9]|\s)+$", postcode)

    if not match:
        return False, constants.FHIR_INVALID_POSTCODE_ILLEGAL_CHAR

    return True, ""


def isFhirStatusValid(active_bool):
    if active_bool != constants.FHIR_ACTIVE_ARG and active_bool != constants.FHIR_INACTIVE_ARG:
        return False, constants.FHIR_INVALID_STATUS

    return True, ""


def isFhirAddressCityValid(address_city):
    if len(address_city) < 3:
        return False, constants.FHIR_INVALID_CITY_SHORT
    if len(address_city) > 75:
        return False, constants.FHIR_INVALID_CITY_LONG

    match= re.match(r"^([a-zA-Z]|\s|-|'|,|\.)+$", address_city)

    if not match:
        return False, constants.FHIR_INVALID_CITY_CHARACTERS

    return True, ""


def isFhirPrimaryRoleValid(primary_role):
    if len(primary_role) != 1:
        return False, constants.TOO_MANY_FHIR_PRIMARY_ROLE_PARAMS, constants.INVALID_PARAMETER_ERROR

    if primary_role[0] != constants.FHIR_ACTIVE_ARG and primary_role[0] != constants.FHIR_INACTIVE_ARG:
        return False, constants.FHIR_INVALID_PRIMARY_ROLE, constants.INVALID_VALUE_ERROR

    return True, "", ""


def isFhirRoleValid(role, url_root):

    codes = []

    if '|' in role:
        roles = role.split('|')
        system = roles[0]
        if len(roles) > 2:
            return False, constants.FHIR_INVALID_ROLE, constants.INVALID_CODE_VALUE_ERROR
        elif system == url_root + "api/" + constants.FHIR_ROLES_ENDPOINT:
            codes = roles[1].split(',')
        else:
            return False, str.format(constants.INVALID_FHIR_ROLE_SYSTEM_URI, url_root), constants.INVALID_CODE_SYSTEM_ERROR
    elif ',' in role:
        codes = role.split(',')
    else:
        codes.append(role)

    for code in codes:
        if not code.isdigit():
            return False, constants.FHIR_INVALID_ROLE, constants.INVALID_CODE_VALUE_ERROR

    return True, "", ""


def isFhirLastChangedDateValid(date):

    if not date.startswith("gt"):
        return False, constants.FHIR_INVALID_LASTUPDATED_DATE_PREFIX

    date_pattern = "^gt(-?[0-9]{4}(-(0[1-9]|1[0-2])(-(0[0-9]|[1-2][0-9]|3[0-1]))?)?)$"

    match = re.match(date_pattern, date)

    if not match:
        return False, constants.FHIR_INVALID_DATE

    date = extrapolateFhirDate(date)

    try:
        date = datetime.date(*(int(s) for s in date.split('-')))
    except:
        return False, constants.FHIR_INVALID_DATE

    return True, ""


def extrapolateFhirDate(date):
    date = date[2:] # remove gt

    if len(date) == 4: #YYYY
        date += "-01-01"
    if len(date) == 7: #YYYY-MM
        date += "-01"

    return date


