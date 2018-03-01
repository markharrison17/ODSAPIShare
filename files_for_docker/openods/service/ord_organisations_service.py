from openods.model import model_entry
from openods.translation import translation_entry
from openods.serialisation import serialisation_entry

from openods import constants
from openods import log_utils


def get_ord_organisations_summary(request, format, app_hostname, request_id):
    log_utils.log_layer_entry(constants.SERVICE, request_id )

    limit, offset = set_ord_offset_and_limit(request.args)

    orgs_summary_dict, total_record_count, returned_record_count = model_entry.get_ord_orgs_summary(request.args, limit,
                                                                                                    offset, request_id)

    structured_orgs_summary_dict = translation_entry.structure_ord_org_summary(orgs_summary_dict, app_hostname,
                                                                               request_id)

    response_body = serialisation_entry.create_response_body(structured_orgs_summary_dict, format, request_id,
                                                             is_fhir=False)

    log_utils.log_layer_exit(constants.SERVICE, request_id)

    return response_body, returned_record_count, total_record_count


def set_ord_offset_and_limit(request_args):
    limit = request_args.get(constants.LIMIT)
    if not limit:
        limit = constants.LIMIT_DEFAULT
    offset = request_args.get(constants.OFFSET)
    if not offset:
        offset = constants.OFFSET_DEFAULT
    return limit, offset


