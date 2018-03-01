import pprint
import datetime
import threading
from pathlib import Path
from openods import schema_check
from openods import app
from openods.service import upload_file_service
from openods import connection
from openods import constants
from urllib.parse import urlparse



pp = pprint.PrettyPrinter(indent=4)

if __name__ == "__main__":
    print(str.format("Database URL: {0}", app.config["DATABASE_URL"]))
    print(str.format("Cache Timeout: {0}", app.config["CACHE_TIMEOUT"]))
    print(str.format("APP Hostname: {0}", app.config["APP_HOSTNAME"]))
    print(str.format("API Path: {0}", app.config["API_PATH"]))
    print(str.format("DEBUG: {0}", app.config["DEBUG"]))

    schema_check.check_schema_version()

    # Lists all routing rules registered on the Flask app
    rules_list = []
    for rule in app.url_map.iter_rules():
        rules_list.append(rule)
    print("Rules List:")
    pp.pprint(rules_list)

    url = urlparse(app.config['DATABASE_URL'])
    connection.init_connection_pool(url, constants.CONNECTION_POOL_SIZE)

    for thread in threading.enumerate():
        print(thread.name)

    threads_to_run_file = Path(constants.FILE_LOCATION_PATH + constants.THREADS_TO_RUN)
    if threads_to_run_file.is_file():
        file = open(constants.FILE_LOCATION_PATH + constants.THREADS_TO_RUN, 'r')
        line = file.readline()
        file.close()
        thread_info = line.split(':')
        dToRun = datetime.date(*(int(s) for s in thread_info[2].split('-')))
        doUpload = True
        for thread in threading.enumerate():
            if thread.name == thread_info[0]:
                doUpload = False
                print("do upload false")

        if doUpload:
            time_to_run = thread_info[3] + ":" + thread_info[4]
            upload_file_service.create_file_upload_thread(thread_info[1], time_to_run, thread_info[2],
                                                          thread_name=thread_info[0])


    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG'],
        threaded=True
    )
