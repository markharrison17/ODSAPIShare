import collections
from openods.translation import translation_utils
from openods import exception
import openods.constants as constants


def build_roles(roles_rows, data):

    if len(roles_rows) == 0:
        return data

    role_dict = {}
    roles = []

    try:
        for role in roles_rows:

            roles_dict = collections.OrderedDict()

            roles_dict['id'] = role.pop('code')
            roles_dict['uniqueRoleId'] = int(role.pop('unique_id'))
            primary_role = role.pop('primary_role')
            if primary_role:
                roles_dict['primaryRole'] = primary_role
            roles_dict[constants.DATES] = translation_utils.get_dates_for_org(role)
            roles_dict['Status'] = role.pop('status')

            roles.append(roles_dict)

        role_dict['Role'] = roles
        data[constants.ROLES] = role_dict
    except KeyError:
        raise exception.InvalidDataError

    return data


def build_roles_for_fhir(roles_rows, data, url_root):

    if len(roles_rows) == 0:
        return data

    roles = []

    try:
        for role in roles_rows:
            extension_role = {}
            extension_list = []

            role = translation_utils.remove_none_values_from_dictionary(role)

            add_coding_extension(extension_list, role, url_root)

            add_primary_role_extension(extension_list, role)

            add_date_extension(extension_list, role, constants.DATE_TYPE_OPERATIONAL)

            add_date_extension(extension_list, role, constants.DATE_TYPE_LEGAL)

            add_status_extension(extension_list, role)

            extension_role['url'] = constants.FHIR_ORGANIZATION_ROLE_URI
            extension_role['extension'] = extension_list

            roles.append(extension_role)

        data['extension'] += roles
    except KeyError:
        exception.InvalidDataError

    return data

def add_date_extension(extension_list, role, date_type):
    active_period_dict = translation_utils.create_active_period(date_type, role, isRoleExtension=True)
    if active_period_dict is not None:
        extension_list.append(active_period_dict)

def add_status_extension(extension_list, role):
    status = role.pop('status')
    extension_status = {}
    extension_status['url'] = constants.FHIR_STATUS_URI
    extension_status['valueString'] = status
    extension_list.append(extension_status)


def add_primary_role_extension(extension_list, role):
    primary_role = role.pop('primary_role')
    extension_primary_role = {}
    extension_primary_role['url'] = constants.FHIR_PRIMARY_ROLE_URI
    extension_primary_role['valueBoolean'] = primary_role
    extension_list.append(extension_primary_role)


def add_coding_extension(extension_list, role, url_root):
    code = role.pop('code')
    code = code[2:] #Strip off the RO that is in the DB table for FHIR
    display_name = role.pop('displayname')
    coding = {}
    coding['system'] = url_root + "api/" + constants.FHIR_ROLES_ENDPOINT
    coding['code'] = code
    coding['display'] = display_name
    extension_role_role = {}
    extension_role_role['url'] = constants.FHIR_ROLE_URI
    extension_role_role['valueCoding'] = coding
    extension_list.append(extension_role_role)
