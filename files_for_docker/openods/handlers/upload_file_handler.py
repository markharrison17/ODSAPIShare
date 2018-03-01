import datetime
import os.path
import uuid
import requests
import re

from lxml import etree

from flask import request, Response

from openods.model import version

from openods import app
from openods import log_utils
from openods.delta_tool import delta_utils
from openods import constants
from openods.service import upload_file_service

from threading import Timer
from pathlib import Path


@app.route(app.config['API_PATH'] + "/" + "upload", methods=['POST'])
def post_upload_file():

    if not constants.ALLOW_DELTA_CHANGES:
        return create_response("Upload tool not enabled")

    threads_to_run_file = Path(constants.FILE_LOCATION_PATH + 'threads_to_run.txt')
    if threads_to_run_file.is_file():
        return create_response("Delta upload already scheduled.")

    request_id = log_utils.get_request_id(request)
    log_utils.log_handler_entry(request_id, request)

    filename = get_param_from_request_form(request, 'filename')
    sequence_number = get_param_from_request_form(request, 'sequence_number')
    publication_date = get_param_from_request_form(request, 'publication_date')
    type = get_param_from_request_form(request, 'type')
    record_count = get_param_from_request_form(request, 'record_count')
    time_to_run = get_param_from_request_form(request, 'time')
    date_to_run = get_param_from_request_form(request, 'date')

    valid, description = validate_delta_upload_params(request_id, filename, sequence_number, type,
                                                      publication_date, record_count, time_to_run, date_to_run)
    if not valid:
        return create_response(description)

    response = upload_file_service.create_file_upload_thread(filename, time_to_run, date_to_run, thread_name=None)

    # schema_valid = delta_utils.validate_xml_against_schema(filename)
    # if not schema_valid:
    #     return create_response("Supplied XML not schema valid.")
    #
    # hour = None
    # minutes = None
    # if time_to_run is not None:
    #     hour, minutes = get_time_to_run(time_to_run)
    #     if hour is None or minutes is None:
    #         return create_response("Invalid time specified.")
    #
    # dToRun = None
    # if date_to_run is not None:
    #     valid, description = validate_date_format(date_to_run)
    #     if not valid:
    #         return valid, description
    #
    #     try:
    #         dToRun = datetime.date(*(int(s) for s in date_to_run.split('-')))
    #     except:
    #         return create_response("Invalid date specified")
    #
    #     if time_to_run is None:
    #         return create_response("If a date is supplied a time must also be specified")
    #
    # response = apply_changes(dToRun, filename, hour, minutes, thread_name=None)

    return create_response(response)

def create_response(response):
    return Response(response)

# def apply_changes(dToRun, filename, hour, minutes, thread_name):
#     response = "Delta upload scheduled"
#     tname = None
#
#     dNow = datetime.date.today()
#
#     if hour is not None and minutes is not None:
#         dtNow = datetime.datetime.today()
#
#
#         dtRun = dtNow.replace(day=dtNow.day, hour=hour, minute=minutes, second=0, microsecond=0)
#
#         if dtRun < dtNow and dToRun is None:
#             dtRun = dtRun + datetime.timedelta(days=1)
#         elif dToRun is not None:
#             if dToRun < dNow:
#                 return "Date to run update must be in the future."
#             dtRun = dtRun.replace(day=dToRun.day, month=dToRun.month, year=dToRun.year)
#
#         delta_t = dtRun - dtNow
#
#         secs = (delta_t.days * constants.DAY_IN_SECONDS) + delta_t.seconds + 1
#
#         if secs > 5 and secs < (5 * constants.DAY_IN_SECONDS):
#             print("Scheduling a delta upload to take place in " + str(secs) + " seconds.")
#
#             tname = create_delta_thread(secs, filename, thread_name, dToRun, dNow, hour, minutes)
#
#         elif secs >= (constants.MAX_DAYS_FUTURE_UPLOAD * constants.DAY_IN_SECONDS):
#             return "Scheduled update can not be more than " + str(constants.MAX_DAYS_FUTURE_UPLOAD) + " days in the future."
#         else:
#             print("Setting off a delta upload.")
#             return "Scheduled update time must be in the future."
#     else:
#         print("Scheduling a delta upload to take place right away.")
#         tname = create_delta_thread(5, filename, thread_name, dToRun, dNow, hour, minutes)
#
#     if tname is not None:
#         response = "Delta upload scheduled in thread name = " + tname
#     return response


def create_delta_thread(secs, filename, thread_name, dToRun, dNow, hour, minutes):
    t = Timer(secs, delta_utils.perform_database_update, args=(filename,))
    t.start()
    if thread_name == None:
        thread_name = uuid.uuid4()
    t.setName(thread_name)
    tname = t.getName()
    print("Thread name of scheduled thread is " + str(tname))

    if dToRun is None:
        dToRun = dNow

    file = open(constants.FILE_LOCATION_PATH + constants.THREADS_TO_RUN, 'w')
    file.write(tname + ":" + filename + ":" + str(dToRun) + ":" + str(hour) + ":" + str(minutes))
    file.close()
    return tname


def get_time_to_run(time):
    hour = None
    minutes = None
    time = time.split(':')
    if time[0].isnumeric:
        hour = int(float(time[0]))
        if 0 > hour or hour > 23:
            hour = None
    if time[1].isnumeric:
        minutes = int(float(time[1]))
        if 0 > minutes or minutes > 59:
            minutes = None
    return hour, minutes


def validate_delta_upload_params(request_id, filename, sequence_number, type, publication_date, record_count, time_to_run, date_to_run):
    valid, description = validate_filename(filename)
    if not valid:
        return valid, description

    version_dict = version.get_latest_version(request_id)

    xml_file_path = constants.FILE_LOCATION_PATH + filename
    # data = xml_tree_parser.parse(xml_file_path)
    data = get_xml_data(filename)
    # data = ET.fromstring(data.text)
    # print(data)

    valid, description = validate_sequence_number(version_dict, sequence_number, data)
    if not valid:
        return valid, description

    valid, description = validate_publication_date(version_dict, publication_date, data)
    if not valid:
        return valid, description

    valid, description = validate_type(type, data)
    if not valid:
        return valid, description

    valid, description = validate_record_count(record_count, data)
    if not valid:
        return valid, description

    valid, description = validate_time_to_run(time_to_run)
    if not valid:
        return valid, description

    valid, description = validate_date_to_run(date_to_run, time_to_run)
    if not valid:
        return valid, description

    valid, desription = validate_xml_against_schema(filename)
    if not valid:
        return valid, description

    return True, ""

def validate_xml_against_schema(filename):
    schema_valid = delta_utils.validate_xml_against_schema(filename)
    if not schema_valid:
        return False, "Supplied XML not schema valid."
    return True, ""

def validate_date_to_run(date_to_run, time_to_run):
    if date_to_run is not None:
        valid, description = validate_date_format(date_to_run)
        if not valid:
            return False, description

        try:
            dToRun = datetime.date(*(int(s) for s in date_to_run.split('-')))
        except:
            return False, "Invalid date specified"

        dNow = datetime.date.today()
        if dToRun < dNow:
            return False, "Date to run update must be in the future."

        delta_t = dToRun - dNow
        if delta_t.days > constants.MAX_DAYS_FUTURE_UPLOAD:
            return False, "Scheduled update can not be more than " + \
                   str(constants.MAX_DAYS_FUTURE_UPLOAD) + " days in the future."

        if time_to_run is None:
            return False, "If a date is supplied a time must also be specified"

    return True, ""

def validate_time_to_run(time_to_run):
    if time_to_run is not None:
        hour, minutes = get_time_to_run(time_to_run)
        if hour is None or minutes is None:
            return False, "Invalid time specified."

    return True, ""

def validate_record_count(record_count, data):
    if record_count is None:
        return False, "No record count supplied"

    record_count_xml = data.find('./Manifest/RecordCount').attrib.get('value')

    if record_count_xml != record_count:
        return False, "Record count supplied differs from records count in file."

    organisations_xml = data.findall('.Organisations/Organisation')

    if int(record_count) != len(organisations_xml):
        return False, "Record count supplied differs from the number of records in the file."

    return True, ""

def validate_type(type, data):
    if type is None:
        return False, "No type supplied"
    if type != 'Partial':
        return False, "Unsupported file type"

    type_xml = data.find('./Manifest/PublicationType').attrib.get('value')

    if type_xml != type:
        return False, "Supplied type does not match the one in the file provided."

    return True, ""


def validate_filename(filename):
    if not os.path.isfile(constants.FILE_LOCATION_PATH + filename):
        return False, "No file matching " + filename + " found to upload."

    return True, ""

def validate_publication_date(version_dict, publication_date, data):
    if publication_date is not None:
        valid, description = validate_date_format(publication_date)
        if not valid:
            return valid, description

        try:
            dPublication = datetime.date(*(int(s) for s in publication_date.split('-')))
        except:
            return False, "Invalid date"
    else:
        return False, "No publication date supplied"

    publication_date_xml = data.find('./Manifest/PublicationDate').attrib.get('value')
    dPublicationXml = datetime.date(*(int(s) for s in publication_date_xml.split('-')))

    if dPublication != dPublicationXml:
        return False, "Supplied publication date does not match the one in the file provided"

    current_publication_date = version_dict['publication_date']
    dCurrentPublication = datetime.date(*(int(s) for s in current_publication_date.split('-')))

    if dCurrentPublication >= dPublication:
        return False, "File publication date is before the publication date of the current dataset"

    return True, ""


def validate_sequence_number(version_dict, sequence_number, data):
    sequence_number_xml = data.find('./Manifest/PublicationSeqNum').attrib.get('value')

    print("SEQ NUM XML", sequence_number_xml)

    if int(sequence_number) != int(sequence_number_xml):
        return False, "Specified sequence number does not match the one in the file provided."

    current_sequence_number = version_dict['publication_seqno']

    if int(sequence_number) != int(current_sequence_number) + 1:
        return False, "Specified sequence number is not the next in the expected sequence."

    return True, ""

def validate_date_format(date):
    match = re.match('(\d{4}-\d{2}-\d{2})', date)
    if not match:
        return False, "Invalid date format"
    if len(date) != 10:
        return False, "Invalid date format"

    return True, ""


def get_param_from_request_form(request, param):
    if param in request.form:
        return request.form[param]
    else:
        return None

def get_xml_data(xml_file_name):
    xml = requests.get(constants.GIT_HUB + xml_file_name)
    root = etree.XML(str.encode(xml.text))
    tree = etree.ElementTree(root)
    return tree

def get_xml_schema(xml_file_name):
    xml = requests.get(constants.GIT_HUB + xml_file_name)
    root = etree.XML(str.encode(xml.text))
    tree = etree.ElementTree(root)
    return tree







