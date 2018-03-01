from openods.model import model_entry
from openods.translation import translation_entry
from openods.serialisation import serialisation_entry

from openods import constants
from openods import log_utils


def get_fhir_roles(request_id, format, request_url):
    log_utils.log_layer_entry(constants.SERVICE, request_id )

    organisation_roles_dict = model_entry.get_fhir_roles_codesystem(request_id)

    structred_organisation_roles_dict = translation_entry.structure_fhir_rolesystem(organisation_roles_dict, format,
                                                                                    request_url, request_id)

    response_body = serialisation_entry.create_response_body(structred_organisation_roles_dict, format, request_id, is_fhir=True)

    log_utils.log_layer_exit(constants.SERVICE, request_id)

    return response_body

