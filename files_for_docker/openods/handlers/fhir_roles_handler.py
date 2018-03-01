from flask import request, Response

import openods.handlers.handler_utils
from openods.handlers import handler_utils
from openods.service import fhir_roles_service

from openods import app
from openods import log_utils
from openods import constants
from openods import exception


@app.route(app.config['API_PATH'] + "/" + constants.FHIR_ROLES_ENDPOINT, methods=['GET'])
def get_fhir_role_codes():

    request_id = log_utils.get_request_id(request)
    log_utils.log_handler_entry(request_id, request)

    format, error_description = handler_utils.determine_format(request, is_fhir=True)

    if error_description:
        code = constants.INVALID_VALUE_ERROR
        return handler_utils.create_fhir_error_response(format, [code], request_id, [error_description], 406)

    valid, descriptions, codes = openods.handlers.handler_utils.isValidFHIRCapabilitiesOrRolesRequest(request)
    if not valid:
        return handler_utils.create_fhir_error_response(format, codes, request_id, descriptions, 406)

    try:
        response = fhir_roles_service.get_fhir_roles(request_id, format, request.base_url)
    except (exception.ServiceError, exception.InvalidDataError):
        description = "Service Unavailable"
        code = constants.ACCESS_DENIED
        return handler_utils.create_fhir_error_response(format, [code], request_id, [description], 500)
    except:
        code = constants.ACCESS_DENIED
        return handler_utils.create_fhir_error_response(format, [code], request_id, ["Unknown Error"], 404)

    response = Response(response)
    handler_utils.add_content_type_header_to_response(format, response)
    log_utils.log_handler_exit(request_id, response.status, constants.SUCCESS)

    return response

