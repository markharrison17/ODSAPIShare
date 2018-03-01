import uuid
import datetime

from openods.delta_tool import delta_utils
from openods import constants
from threading import Timer

def create_file_upload_thread(filename, time_to_run, date_to_run, thread_name):

    hour = None
    minutes = None
    if time_to_run is not None:
        hour, minutes = get_time_to_run(time_to_run)

    dToRun = None
    if date_to_run is not None:
        dToRun = datetime.date(*(int(s) for s in date_to_run.split('-')))

    dNow = datetime.date.today()

    secs_to_run = 10

    if hour is not None and minutes is not None:
        dtNow = datetime.datetime.today()

        dtRun = dtNow.replace(day=dtNow.day, hour=hour, minute=minutes, second=0, microsecond=0)

        if dtRun < dtNow and dToRun is None:
            dtRun = dtRun + datetime.timedelta(days=1)
        elif dToRun is not None:
            dtRun = dtRun.replace(day=dToRun.day, month=dToRun.month, year=dToRun.year)

        delta_t = dtRun - dtNow
        secs_to_run = (delta_t.days * constants.DAY_IN_SECONDS) + delta_t.seconds + 1

        if secs_to_run < 10:
            secs_to_run = 10

    print("Scheduling a delta upload to take place in " + str(secs_to_run) + " seconds.")
    tname = create_delta_thread(secs_to_run, filename, dToRun, dNow, hour, minutes, thread_name)

    if tname is not None:
        response = "Delta upload scheduled in thread name = " + tname
    else:
        response = "No upload scheduled. The ODS team will need to look into why."
    return response


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

def create_delta_thread(secs, filename, dToRun, dNow, hour, minutes, thread_name):
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

