from openods.service import service_utils
from openods.model import model_entry
from openods.translation import translation_entry
from openods.serialisation import serialisation_entry

from openods import log_utils
from openods import constants


def get_single_organisation(ods_code, format, url_root, request_id, is_fhir):
    log_utils.log_layer_entry(constants.SERVICE, request_id)

    org, address, role, contact, relationship, successor = model_entry.get_org_data(ods_code, request_id, is_fhir)

    org_dict = service_utils.build_org(org, address, role, contact, relationship, successor, is_fhir)

    structured_org_dict = translation_entry.structure_org(org_dict, url_root, request_id, is_fhir)

    response_body = serialisation_entry.create_response_body(structured_org_dict, format, request_id, is_fhir)

    log_utils.log_layer_exit(constants.SERVICE, request_id)

    return response_body



