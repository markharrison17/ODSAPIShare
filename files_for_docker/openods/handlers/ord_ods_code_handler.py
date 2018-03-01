from flask import abort, request, Response

from openods.handlers import handler_utils
from openods.service import ods_code_service

from openods import app
from openods import log_utils
from openods import exception
from openods import constants


@app.route(app.config['API_PATH'] + "/" + constants.ORGANISATIONS_ENDPOINT + "/<ods_code>", methods=['GET'])
def get_organisation(ods_code):
    """
    Endpoint returns a single ODS organisation
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

    url_root = request.url_root

    format, error_description = handler_utils.determine_format(request, is_fhir=False)
    if error_description:
        handler_utils.ord_error_log_and_abort(406, error_description, request_id)

    valid, description = handler_utils.isValidOdsCodeAPIRequest(request)
    if not valid:
        handler_utils.ord_error_log_and_abort(406, description, request_id)

    ods_code = str.upper(ods_code)

    try:
        response = ods_code_service.get_single_organisation(ods_code, format, url_root, request_id, is_fhir=False)

    except (exception.ServiceError, exception.InvalidDataError):
        handler_utils.ord_error_log_and_abort(500, "Service Unavailable", request_id)
    except:
        handler_utils.ord_error_log_and_abort(404, "Unknown Error", request_id)

    response = Response(response)

    handler_utils.add_content_type_header_to_response(format, response)
    log_utils.log_handler_exit(request_id, response.status, constants.SUCCESS)

    return response






