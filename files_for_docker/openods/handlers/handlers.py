import logging

from flask import jsonify, request, g, render_template

import openods.handlers.handler_utils
import openods.log_utils
from openods import app

#
# HTTP error handling
@app.errorhandler(404)
def not_found(error):

    try:
        g.request_id
    except AttributeError:
        openods.log_utils.get_request_id(request)

    try:
        g.source_ip
    except AttributeError:
        openods.log_utils.get_source_ip(request)

    logger = logging.getLogger(__name__)
    logger.info('logType=Request|requestId="{request_id}"|statusCode={status_code}|'
                'errorText="{error_text}"|path="{path}"|'
                'sourceIp={source_ip}|url="{url}"|'.format(
                    request_id=g.request_id,
                    source_ip=g.source_ip,
                    path=request.path,
                    url=request.url,
                    status_code=error.code,
                    error_text=error.description)
                )

    return jsonify(
        {
            'errorCode': 404,
            'errorText': 'Not found'
        }
    ), 404

@app.errorhandler(406)
def not_found(error):
    try:
        g.request_id
    except AttributeError:
        openods.log_utils.get_request_id(request)

    try:
        g.source_ip
    except AttributeError:
        openods.log_utils.get_source_ip(request)

    logger = logging.getLogger(__name__)
    logger.info('logType=Request|requestId="{request_id}"|statusCode={status_code}|'
                'errorText="{error_text}"|path="{path}"|'
                'sourceIp={source_ip}|url="{url}"|'.format(
        request_id=g.request_id,
        source_ip=g.source_ip,
        path=request.path,
        url=request.url,
        status_code=error.code,
        error_text=error.description)
    )

    return jsonify(
        {
            'errorCode': 406,
            'errorText': error.description
        }
    ), 406


@app.route('/')
def root():
    return "The art of accurate observation is often called cynicism by those who do not possess it."



@app.route('/api/')
def api():

    return render_template('landing_page.html')





