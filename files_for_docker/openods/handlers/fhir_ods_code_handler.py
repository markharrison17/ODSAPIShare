from flask import request, Response


from openods.handlers import handler_utils
from openods.service import ods_code_service

from openods import app
from openods import log_utils
from openods import constants
from openods import exception

@app.route(app.config['API_PATH'] + "/" + constants.FHIR_ORGANISATIONS_ENDPOINT + "/<ods_code>", methods=['GET'])
def get_fhir_organisation(ods_code):
    """
    Endpoint returns a single ODS FHIR organization 
    ---
    parameters:
      - name: ods_code
        in: path
        type: string
        required: true
    responses:
      200:
        description: An ODS organisation record was returned in JSON by default or XML if parameter _format = xml
      404 NOT FOUND:
        description: No ODS organisation record was found
      406 NOT ACCEPTABLE:
        description: An invalid _format was supplied.  Valid options are json or xml
    """
    request_id = log_utils.get_request_id(request)
    log_utils.log_handler_entry(request_id, request)

    format, error_description = handler_utils.determine_format(request, is_fhir=True)
    if error_description:
        code = constants.INVALID_VALUE_ERROR
        return handler_utils.create_fhir_error_response(format, [code], request_id, [error_description], 406)

    valid, descriptions, codes = handler_utils.isValidFHIROdsCodeAPIRequest(request)
    if not valid:
        return handler_utils.create_fhir_error_response(format, codes, request_id, descriptions, 406)

    ods_code = str.upper(ods_code)
    url_root = request.url_root

    try:
        response = ods_code_service.get_single_organisation(ods_code, format, url_root, request_id, is_fhir=True)
    except (exception.ServiceError, exception.InvalidDataError):
        description = "Service Unavailable"
        code = constants.ACCESS_DENIED
        return handler_utils.create_fhir_error_response(format, [code], request_id, [description], 500)
    except exception.UnfoundOrgError:
        description = "No record found for supplied ODS code"
        code = constants.NO_RECORD_FOUND_ERROR
        return handler_utils.create_fhir_error_response(format, [code], request_id, [description], 404)
    except:
        code = constants.ACCESS_DENIED
        return handler_utils.create_fhir_error_response(format, [code], request_id, ["Unknown Error"], 404)

    response = Response(response)

    handler_utils.add_content_type_header_to_response(format, response)
    log_utils.log_handler_exit(request_id, response.status, constants.SUCCESS)

    return response



