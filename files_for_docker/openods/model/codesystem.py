from openods import log_utils
from openods import connection


def get_organisation_roles(request_id):
    try:
        sql = "SELECT id, displayname " \
               "FROM codesystems c " \
               "WHERE c.name = 'OrganisationRole'"


        with connection.get_db_cursor(request_id) as cursor:
            log_utils.log_database_query_statement(request_id, sql)

            cursor.execute(sql)
            organisation_roles = cursor.fetchall()

            log_utils.log_database_return(request_id, organisation_roles)



    except Exception:
        raise

    return organisation_roles

