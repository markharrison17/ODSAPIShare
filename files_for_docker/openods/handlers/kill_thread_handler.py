import os

from flask import abort, request, Response


from openods import app
from openods import log_utils
from openods import constants



@app.route(app.config['API_PATH'] + "/" + "kill_upload", methods=['POST'])
def post_kill_upload_file():

    request_id = log_utils.get_request_id(request)
    log_utils.log_handler_entry(request_id, request)

    thread_name_to_kill = get_param_from_request_form(request, 'thread_name')

    file = open(constants.FILE_LOCATION_PATH + constants.THREADS_TO_RUN, 'r')
    line = file.readline()
    file.close()

    thread_name = line.split(':')[0]

    if thread_name == thread_name_to_kill:
        os.remove(constants.FILE_LOCATION_PATH + constants.THREADS_TO_RUN)
        return Response("Scheduled thread named " + thread_name_to_kill + " will not be run.")
    else:
        return Response("Scheduled thread named " + thread_name_to_kill + " was not scheduled.")



def get_param_from_request_form(request, param):
    if param in request.form:
        return request.form[param]
    else:
        return None

