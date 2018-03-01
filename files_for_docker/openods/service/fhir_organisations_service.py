from werkzeug.datastructures import ImmutableMultiDict

from openods.model import model_entry
from openods.service import service_utils
from openods.translation import translation_entry
from openods.serialisation import serialisation_entry

from openods import constants
from openods import log_utils


def get_fhir_organisations(request, format, request_id):
    log_utils.log_layer_entry(constants.SERVICE, request_id )

    request_args = ImmutableMultiDict.copy(request.args)

    limit, page = get_pagination_parameters(request_args)

    ods_codes_dict, total_record_count, returned_record_count = model_entry.get_fhir_ods_codes(
        request_args, page, limit, request_id)

    list_of_org_dicts = []
    for ods_code in ods_codes_dict:
        org, address, role, contact, relationship, successor = model_entry.get_org_data(ods_code['odscode'], request_id,
                                                                                        is_fhir=True)
        org_dict = service_utils.build_org(org, address, role, contact, relationship, successor, is_fhir=True)
        list_of_org_dicts.append(org_dict)

    structured_bundle_dict = translation_entry.structure_fhir_organisations_bundle(list_of_org_dicts,
                                                                                   total_record_count, limit, page,
                                                                                   request, request_id)

    response_body = serialisation_entry.create_response_body(structured_bundle_dict, format, request_id, is_fhir=True)

    log_utils.log_layer_exit(constants.SERVICE, request_id)

    return response_body, returned_record_count, total_record_count


def get_pagination_parameters(request_args):
    limit = request_args.get(constants.FHIR_LIMIT)
    if not limit:
        limit = constants.FHIR_LIMIT_DEFAULT
    page = request_args.get(constants.FHIR_PAGE)
    if not page:
        page = constants.FHIR_PAGE_DEFAULT
    summary = request_args.get(constants.FHIR_SUMMARY)

    if summary == constants.FHIR_SUMMARY_COUNT:
        limit = 0
    return limit, page


