from flask import request, Response

from openods.handlers import handler_utils
from openods.service import ord_sync_service

from openods import app
from openods import  log_utils
from openods import constants
from openods import exception


@app.route(app.config['API_PATH'] + "/" + constants.SYNC_ENDPOINT, methods=['GET'])
def get_changed_organisations_list():
    request_id = log_utils.get_request_id(request)
    log_utils.log_handler_entry(request_id, request)
    route = request.url_root


    format, error_description = handler_utils.determine_format(request, is_fhir=False)
    if error_description:
        handler_utils.ord_error_log_and_abort(406, error_description, request_id)

    valid, description = handler_utils.isValidSyncAPIRequest(request)
    if not valid:
        handler_utils.ord_error_log_and_abort(406, description, request_id)


    try:
        resp_data, total_record_count = ord_sync_service.get_ord_organisations_changed_since(request.args, format, route,
                                                                                             request_id)
    except (exception.ServiceError, exception.InvalidDataError):
        handler_utils.ord_error_log_and_abort(500, "Service Unavailable", request_id)

    response = Response(resp_data)

    handler_utils.add_content_type_header_to_response(format, response)

    response.headers['X-Total-Count'] = total_record_count
    response.headers['Access-Control-Expose-Headers'] = 'X-Total-Count'

    log_utils.log_handler_exit(request_id, response.status, constants.SUCCESS)
    return response
