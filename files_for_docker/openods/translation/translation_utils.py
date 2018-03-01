import math
import collections

from openods import constants
from openods import exception


def get_dates_for_org(table):
    dates = []
    op_start_date = None
    op_end_date = None
    try:
        op_start_date = table.pop('operational_start_date').isoformat()
    except:
        pass
    try:
        op_end_date = table.pop('operational_end_date').isoformat()
    except:
        pass
    if (op_start_date != None or op_end_date != None):
        op_date = {}
        op_date['Type'] = 'Operational'
        if (op_start_date != None):
            op_date['Start'] = op_start_date
        if (op_end_date != None):
            op_date['End'] = op_end_date
        dates.append(op_date)
    legal_start_date = None
    legal_end_date = None
    try:
        legal_end_date = table.pop('legal_end_date').isoformat()
    except:
        pass
    try:
        legal_start_date = table.pop('legal_start_date').isoformat()
    except:
        pass
    if (legal_start_date != None or legal_end_date != None):
        legal_date = {}
        legal_date['Type'] = 'Legal'
        if (legal_start_date != None):
            legal_date['Start'] = legal_start_date
        if (legal_end_date != None):
            legal_date['End'] = legal_end_date
        dates.append(legal_date)

    return dates


def get_id_for_org(table, column_name):
    try:
        org_id = dict(root='2.16.840.1.113883.2.1.3.2.4.18.48',
                      assigningAuthorityName='HSCIC',
                      extension=table.pop(column_name))
    except KeyError:
        raise exception.InvalidDataError

    return org_id


def get_target_for_org(table):
    try:
        primary_role = dict(id=table.pop('target_primary_role_code'),
                            uniqueRoleId=table.pop('target_unique_role_id'))

        # target = dict(PrimaryRoleId=primary_role,
        #               OrgId=get_id_for_org(table, 'target_odscode'))
        target = collections.OrderedDict(OrgId=get_id_for_org(table, 'target_odscode'),
                                         PrimaryRoleId=primary_role)
    except KeyError:
        raise exception.InvalidDataError

    return target


def remove_none_values_from_dictionary(dirty_dict):
    clean_dict = dict((k, v) for k, v in dirty_dict.items() if v is not None)
    return clean_dict


def create_active_period(date_type, organisation, isRoleExtension):
    start_date_string = date_type.lower() + "_start_date"
    end_date_string = date_type.lower() + "_end_date"
    if start_date_string in organisation:
        start_date = organisation.pop(start_date_string)
    else:
        return None
    if end_date_string in organisation:
        end_date = organisation.pop(end_date_string)
    else:
        end_date = None
    period_dict = {}
    status_dict = {}
    status_dict['url'] = constants.FHIR_DATE_TYPE_URI
    status_dict['valueString'] = date_type
    value_period_extension = []
    value_period_extension.append(status_dict)
    period_dict['extension'] = value_period_extension
    period_dict['start'] = start_date.isoformat()
    if end_date is not None:
        period_dict['end'] = end_date.isoformat()
    active_period_dict = {}

    if isRoleExtension:
        active_period_dict['url'] = constants.FHIR_ROLE_ACTIVE_PERIOD_URI
    else:
        active_period_dict['url'] = constants.FHIR_ACTIVE_PERIOD_URI

    active_period_dict['valuePeriod'] = period_dict
    return active_period_dict


def create_link_list(request, count, page, limit):

    link_params = "?"
    for arg in request.args:
        if arg != constants.FHIR_LIMIT and arg != constants.FHIR_PAGE:
            link_params += str.format("{0}={1}&", arg, request.args[arg])

    link = str.format(request.base_url + link_params + constants.FHIR_LIMIT + "={0}", limit)

    link_list = []
    self_link_dict = {}
    self_link_dict['relation'] = constants.LINK_RELATION_SELF
    self_link_dict['url'] = str.format(link + "&" + constants.FHIR_PAGE + "={0}", page)
    link_list.append(self_link_dict)

    if count > int(float(limit)):


        first_link_dict = {}
        first_link_dict['relation'] = constants.LINK_RELATION_FIRST
        first_link_dict['url'] = str.format(link + "&" + constants.FHIR_PAGE + "={0}", "1")
        link_list.append(first_link_dict)

        last_page = math.ceil(count/int(float(limit)))

        last_link_dict = {}
        last_link_dict['relation'] = constants.LINK_RELATION_LAST
        last_link_dict['url'] = str.format(link + "&" + constants.FHIR_PAGE + "={0}", str(last_page))
        link_list.append(last_link_dict)

        if int(float(page)) < last_page:
            next_link_dict = {}
            next_link_dict['relation'] = constants.LINK_RELATION_NEXT
            next_link_dict['url'] = str.format(link + "&" + constants.FHIR_PAGE + "={0}", str(int(float(page)) + 1))
            link_list.append(next_link_dict)
        if (int(float(page)) - 1) > 0 and (int(float(page)) - 1) < last_page:
            prev_link_dict = {}
            prev_link_dict['relation'] = constants.LINK_RELATION_PREVIOUS
            prev_link_dict['url'] = str.format(link + "&" + constants.FHIR_PAGE + "={0}", str(int(float(page)) - 1))
            link_list.append(prev_link_dict)

    return link_list





