from flask import abort, request, Response
from werkzeug.datastructures import ImmutableMultiDict

from openods.handlers import handler_utils
from openods.service import ord_organisations_service

from openods import log_utils
from openods import app
from openods import constants
from openods import exception


@app.route(app.config['API_PATH'] + "/" + constants.ORGANISATIONS_ENDPOINT, methods=['GET'])
def get_organisations():
    """
    Endpoint returning a list of ODS organisations
    ---
    parameters:
      - name: Name
        description: Filters results by names which contain the specified string
        in: query
        type: string
        required: false
      - name: primaryRoleCode
        description: Filters results to only those with one of the specified role codes assigned as a Primary role.
          Ignored if used alongside roleCode parameter.
        in: query
        type: array
        collectionFormat: csv
        required: false
      - name: lastUpdatedSince
        description: Filters results to only those with a lastChangeDate after the specified date.
        in: query
        type: string
        format: date
        required: false
    responses:
      200:
        description: A filtered list of organisation resources
    """
    request_id = log_utils.get_request_id(request)
    log_utils.log_handler_entry(request_id, request)

    format, error_description = handler_utils.determine_format(request, is_fhir=False)
    if error_description:
        handler_utils.ord_error_log_and_abort(406, error_description, request_id)

    valid, description = handler_utils.isValidOrganisationAPIRequest(request)
    if not valid:
        handler_utils.ord_error_log_and_abort(406, description, request_id)

    request_args = ImmutableMultiDict.copy(request.args)
    route = request.base_url

    try:
        resp_data, returned_record_count, total_record_count = \
            ord_organisations_service.get_ord_organisations_summary(request, format, route, request_id)
    except (exception.ServiceError, exception.InvalidDataError):
        handler_utils.ord_error_log_and_abort(500, "Service Unavailable", request_id)
    except:
        handler_utils.ord_error_log_and_abort(404, "Unknown Error", request_id)


    response = Response(resp_data)

    handler_utils.add_content_type_header_to_response(format, response)


    response.headers['X-Total-Count'] = total_record_count
    response.headers['Access-Control-Expose-Headers'] = 'X-Total-Count'

    if returned_record_count != total_record_count:
        response = create_pagination_headers(request_args, response, returned_record_count, route, total_record_count)

    log_utils.log_handler_exit(request_id, response.status, constants.SUCCESS)

    return response


def create_pagination_headers(request_args, resp, returned_record_count, route, total_record_count):


    limit, offset = get_limit_and_offset(request_args)

    next_link, previous_link = create_pagination_links(limit, offset, request_args, route)

    return add_pagination_headers(limit, next_link, offset, previous_link, resp, returned_record_count,
                           total_record_count)


def create_pagination_links(limit, offset, request_args, route):
    link_params = "?"
    for arg in request_args:
        if arg != constants.LIMIT and arg != constants.OFFSET:
            # link_params += arg + "=" + request_args[arg] + "&"
            link_params += str.format("{0}={1}&", arg, request_args[arg])

    link = str.format(route + link_params + "Limit={0}", limit)

    previous_offset = offset - limit
    next_offset = offset + limit
    if previous_offset < 1:
        previous_link = link
    else:
        previous_link = str.format(link + "&Offset={0}", previous_offset)
    next_link = str.format(link + "&Offset={0}", next_offset)

    return next_link, previous_link


def add_pagination_headers(limit, next_link, offset, previous_link, resp, returned_record_count,
                           total_record_count):
    resp.headers[constants.RETURNED_RECORDS] = returned_record_count
    if offset > 0:
        resp.headers[constants.PREVIOUS_PAGE_LINK] = previous_link
    if offset + limit < total_record_count:
        resp.headers[constants.NEXT_PAGE_LINK] = next_link

    return resp


def get_limit_and_offset(request_args):
    limit = request_args.get(constants.LIMIT)
    if limit is None:
        limit = constants.LIMIT_DEFAULT
    else:
        limit = int(float(limit))

    offset = request_args.get(constants.OFFSET)
    if offset is None:
        offset = constants.OFFSET_DEFAULT
    else:
        offset = int(float(offset))

    return limit, offset
