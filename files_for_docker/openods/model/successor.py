from openods import log_utils

def get_for_odscode(odscode, request_id, cursor):
    try:
        sql = "SELECT type, target_odscode, " \
              "unique_id as uniqueId, legal_start_date, target_primary_role_code, " \
              "target_unique_role_id " \
              "FROM successors s " \
              "WHERE s.org_odscode = UPPER(%s);"

        data = (odscode,)

        log_utils.log_database_query_statement(request_id, str.format(sql, data))

        cursor.execute(sql, data)
        successors = cursor.fetchall()

        log_utils.log_database_return(request_id, successors)

    except Exception:
        raise

    return successors
