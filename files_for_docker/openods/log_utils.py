import logging
import uuid

from flask import g


def log_handler_entry(request_id, request):
    source_ip = get_source_ip(request)
    logger = logging.getLogger(__name__)
    logger.info(' requestId="{request_id}"| logType=ENDPOINT ENTRY| path="{path}"| sourceIp="{source_ip}"|'
                'url="{url}"|{parameters}'.format(
        source_ip=source_ip,
        request_id=request_id,
        path=request.path,
        url=request.url,
        parameters=dict_to_piped_kv_pairs(request.args),
    )
    )

def log_handler_exit(request_id, response_code, message):
    logger = logging.getLogger(__name__)
    logger.info(' requestId="{request_id}"| logType=ENDPOINT EXIT| responseCode="{response_code}" | {message}'.format(
        request_id = request_id,
        response_code = response_code,
        message= message
    )
    )


def log_layer_entry(layer, request_id):
    logger = logging.getLogger(__name__)
    logger.debug('requestId="{request_id}"| logType={layer} ENTRY|'.format(
        request_id = request_id,
        layer= layer,
    )
    )

def log_layer_exit(layer, request_id):
    logger = logging.getLogger(__name__)
    logger.debug('requestId="{request_id}"| logType={layer} EXIT|'.format(
        request_id = request_id,
        layer= layer
    )
    )


def log_database_connection_from_pool(request_id, database_url, status):
    logger = logging.getLogger(__name__)
    logger.debug('requestId="{request_id}"| logType=DATABASE CONNECTION TAKEN FROM POOL| status="{status}"|  "'
                 'databaseUrl={database_url}'.format(
        status = status,
        database_url = database_url,
        request_id =   request_id
    )
    )

def log_database_connection_back_to_pool(request_id, database_url, status):
    logger = logging.getLogger(__name__)
    logger.debug('requestId="{request_id}"| logType=DATABASE CONNECTION BACK TO POOL| status="{status}"|  "'
                 'databaseUrl={database_url}'.format(
        status=status,
        database_url=database_url,
        request_id=request_id
    )
    )


def log_database_query_statement(request_id, query):
    logger = logging.getLogger(__name__)
    logger.debug('requestId="{request_id}"| logType=DATABASE QUERY| query={query}'.format(
        request_id= request_id,
        query= query
    )
    )

def log_database_return(request_id, returned_data):
    logger = logging.getLogger(__name__)
    logger.debug('requestId="{request_id}"| logType=DATABASE RESPONSE| returnedData={returned_data}'.format(
        returned_data= returned_data,
        request_id= request_id,
    )
    )

def log_init_connection_pool(status, size):
    logger = logging.getLogger(__name__)
    logger.debug('logType=DATABASE CONNECTION POOL INITIATION| size={size}| status={status}'.format(
        status=status,
        size= size,
    )
    )



def get_source_ip(my_request):
    try:
        source_ip = my_request.headers['X-Forwarded-For']
    except KeyError:
        try:
            source_ip = my_request.headers['X-Client-IP']
        except KeyError:
            source_ip = my_request.remote_addr

    g.source_ip = source_ip

    return source_ip


def get_request_id(my_request):
    try:
        request_id = my_request.headers['X-Request-Id']
    except KeyError:
        request_id = str(uuid.uuid4())

    g.request_id = request_id

    return request_id


def dict_to_piped_kv_pairs(dict_for_conversion):
    output_string = ""
    for key, value in sorted(dict_for_conversion.items()):
        output_string += "{0}={1}|".format(key, value)
    return output_string