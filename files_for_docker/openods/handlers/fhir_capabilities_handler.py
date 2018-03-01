from flask import request, Response

from openods.handlers import handler_utils
from openods.service import fhir_capabilities_service

from openods import app
from openods import log_utils
from openods import constants


@app.route(app.config['API_PATH'] + "/" + constants.FHIR_CAPABILITIES_ENDPOINT, methods=['GET'])
def get_capabilities_statement():

    request_id = log_utils.get_request_id(request)
    log_utils.log_handler_entry(request_id, request)

    format, error_description = handler_utils.determine_format(request, is_fhir=True)
    if error_description:
        code = constants.INVALID_VALUE_ERROR
        return handler_utils.create_fhir_error_response(format, [code], request_id, [error_description], 406)

    valid, descriptions, codes = handler_utils.isValidFHIRCapabilitiesOrRolesRequest(request)
    if not valid:
        return handler_utils.create_fhir_error_response(format, codes, request_id, descriptions, 406)

    response = fhir_capabilities_service.get_fhir_capabilities(format, request.base_url, request_id)
    response = Response(response)

    handler_utils.add_content_type_header_to_response(format, response)
    log_utils.log_handler_exit(request_id, response.status, constants.SUCCESS)

    return response

