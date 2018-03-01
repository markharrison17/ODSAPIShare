from openods import log_utils
from openods import connection


def get_for_odscode(odscode, request_id, cursor):

    try:
        sql = "SELECT type, " \
              "value " \
              "FROM contacts c " \
              "WHERE c.org_odscode = UPPER(%s);"

        data = (odscode,)

        log_utils.log_database_query_statement(request_id, str.format(sql, data))

        cursor.execute(sql, data)
        contacts = cursor.fetchall()

        log_utils.log_database_return(request_id, contacts)

    except Exception:
        raise

    return contacts