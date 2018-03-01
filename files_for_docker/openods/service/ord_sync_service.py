from werkzeug.datastructures import ImmutableMultiDict

from openods.model import model_entry
from openods.translation import translation_entry
from openods.serialisation import serialisation_entry

from openods import constants
from openods import log_utils


def get_ord_organisations_changed_since(request_args, format, app_hostname, request_id):
    log_utils.log_layer_entry(constants.SERVICE, request_id )

    request_args = ImmutableMultiDict.copy(request_args)

    ods_codes = model_entry.get_ord_ods_codes_last_changed_since(request_args, request_id)

    total_record_count = len(ods_codes)

    structured_last_changed_since_summary = translation_entry.build_ord_last_changed_summary(ods_codes, format,
                                                                                             app_hostname)

    response_body = serialisation_entry.create_response_body(structured_last_changed_since_summary, format, request_id,
                                                             is_fhir=False)

    log_utils.log_layer_exit(constants.SERVICE, request_id)

    return response_body, total_record_count
