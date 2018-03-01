from openods import log_utils

def get_for_odscode(odscode, request_id, cursor):
    try:
        sql = "SELECT rs.code, rs.unique_id, rs.target_odscode, rs.status, " \
              "rs.operational_start_date, rs.operational_end_date, rs.legal_start_date, " \
              "rs.legal_end_date, rs.target_primary_role_code, rs.target_unique_role_id " \
              "FROM relationships rs " \
              "WHERE rs.org_odscode = UPPER(%s);"

        data = (odscode,)

        log_utils.log_database_query_statement(request_id, str.format(sql, data))

        cursor.execute(sql, data)
        relationships = cursor.fetchall()

        log_utils.log_database_return(request_id, relationships)

    except Exception as e:
        raise

    return relationships
