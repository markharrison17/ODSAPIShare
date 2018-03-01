from contextlib import contextmanager
from urllib.parse import urlparse as urlparse
from openods import exception

import psycopg2
import psycopg2.extras
import psycopg2.pool

from openods import app
from openods import log_utils


def init_connection_pool(url, size):
    try:
        global pool
        pool = psycopg2.pool.ThreadedConnectionPool(1, size,
                                database=url.path[1:],
                                user=url.username,
                                password=url.password,
                                host=url.hostname,
                                port=url.port)
        log_utils.log_init_connection_pool("SUCCESS", size)
        return pool

    except:
        log_utils.log_init_connection_pool("FAILURE", size)
        raise exception.ServiceError

def close_connection_pool():
    try:
        pool.closeall()
    except:
        raise

@contextmanager
def get_db_connection_from_pool(request_id):
    url = urlparse(app.config['DATABASE_URL'])
    try:
        log_utils.log_database_connection_from_pool(request_id, url, "SUCCESS")
        connection = pool.getconn()
        yield connection
    except exception.DatabaseConnectionError:
        log_utils.log_database_connection_from_pool(request_id, url, "FAILURE")
        raise exception.ServiceError
    finally:
        pool.putconn(connection)
        log_utils.log_database_connection_back_to_pool(request_id, url, "SUCCESS")


@contextmanager
def get_db_cursor(request_id):
    with get_db_connection_from_pool(request_id) as connection:
      cursor = connection.cursor(
                  cursor_factory=psycopg2.extras.RealDictCursor)
      try:
          yield cursor
      except exception.DatabaseConnectionError:
          raise exception.ServiceError
      finally:
          cursor.close()


def get_connection(db, username, password, hostname, port):
    try:
        conn = psycopg2.connect(
            database=db,
            user=username,
            password=password,
            host=hostname,
            port=port
        )

    except psycopg2.Error:
        raise exception.DatabaseConnectionError

    return conn










