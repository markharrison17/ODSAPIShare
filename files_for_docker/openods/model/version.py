from  openods import log_utils
from openods import  connection


def get_latest_file_creation_date(request_id):
    try:
        sql = "SELECT v.file_creation_date " \
              "FROM versions v " \
              "ORDER BY v.file_creation_date DESC " \
              "LIMIT 1"

        with connection.get_db_cursor(request_id) as cursor:
            log_utils.log_database_query_statement(request_id, sql)

            cursor.execute(sql)
            version = cursor.fetchone()

            log_utils.log_database_return(request_id, version)

    except Exception as e:
        raise

    return version

def get_latest_version(request_id):
    try:
        sql = "SELECT * " \
              "FROM versions v " \
              "ORDER BY v.file_creation_date DESC " \
              "LIMIT 1"

        with connection.get_db_cursor(request_id) as cursor:
            log_utils.log_database_query_statement(request_id, sql)
            cursor.execute(sql)
            version = cursor.fetchone()
            log_utils.log_database_return(request_id, version)

    except Exception as e:
        raise

    return version