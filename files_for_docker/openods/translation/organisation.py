import openods.constants as constants

from openods import exception
from openods.translation import translation_utils

def build_organisation(organisation, data):

    try:
        data['Name'] = organisation.pop('name')
        data[constants.DATES] = translation_utils.get_dates_for_org(organisation)
        data['OrgId'] = translation_utils.get_id_for_org(organisation, 'odscode')
        data['Status'] = organisation.pop('status')
        data['LastChangeDate'] = organisation.pop('last_changed')
        data['orgRecordClass'] = organisation.pop('record_class')
        ref_only = organisation.pop('ref_only')
        if ref_only:
            data['refOnly'] = ref_only

    except KeyError:
        raise exception.InvalidDataError

    return data


def build_organisation_for_fhir(organisation, data):
    organisation = translation_utils.remove_none_values_from_dictionary(organisation)

    add_identifier_to_dict(data, organisation)

    add_status_to_dict(data, organisation)

    add_type_to_dict(data, organisation)

    add_name_to_dict(data, organisation)

    add_dates_to_dict(data, organisation, constants.DATE_TYPE_OPERATIONAL)

    add_dates_to_dict(data, organisation, constants.DATE_TYPE_LEGAL)

    return data


def add_type_to_dict(data, organisation):
    try:
        record_class = organisation.pop('record_class')
        record_class = record_class[2:]
        display_name = organisation.pop('displayname')
        coding_dict = {}
        coding_dict['system'] = constants.FHIR_RECORD_CLASS_URI
        coding_dict['code'] = record_class
        coding_dict['display'] = display_name
        type_dict = {'coding': coding_dict}
        data['type'] = type_dict
    except KeyError:
        raise exception.InvalidDataError


def add_identifier_to_dict(data, organisation):
    try:
        odscode = organisation.pop('odscode')
        id_dict = {}
        id_dict['system'] = constants.FHIR_ODSCODE_SYSTEM_URI
        id_dict['value'] = odscode
        data['identifier'] = id_dict
    except KeyError:
        raise exception.InvalidDataError


def add_dates_to_dict(data, organisation, date_type):
    active_period_dict = translation_utils.create_active_period(date_type, organisation, isRoleExtension=False)
    if active_period_dict is not None:
        data['extension'].append(active_period_dict)


def add_status_to_dict(data, organisation):
    try:
        status = organisation.pop('status')
        if status == constants.STATUS_ACTIVE:
            active = True
        elif status == constants.STATUS_INACTIVE:
            active = False
        else:
            raise Exception('Unknown status in xml')
        data['active'] = active
    except KeyError:
        raise exception.InvalidDataError


def add_name_to_dict(data, organisation):
    try:
        data['name'] = organisation.pop('name')
    except KeyError:
        raise exception.InvalidDataError



