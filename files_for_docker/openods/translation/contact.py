from openods.translation import translation_utils
from openods import exception
import openods.constants as constants


def build_contacts(contacts_rows, data):

    if len(contacts_rows) == 0:
        return data

    contact_dict = dict()
    contacts = list()

    for contact in contacts_rows:
        contact = translation_utils.remove_none_values_from_dictionary(contact)
        contacts.append(contact)
    contact_dict['Contact'] = contacts
    data[constants.CONTACTS] = contact_dict

    return data


def build_contacts_for_fhir(contacts_rows, data):

    if len(contacts_rows) == 0:
        return data

    telecom_list = []

    try:
        for contact in contacts_rows:
            telecom_dict = {}
            type = contact["type"]
            if (type == constants.CONTACT_TEL):
                type = constants.FHIR_CONTACT_PHONE
            elif (type == constants.CONTACT_FAX):
                type = constants.FHIR_CONTACT_FAX
            elif (type == constants.CONTACT_HTTP):
                type = constants.FHIR_CONTACT_URL
            elif (type == constants.CONTACT_MAIL):
                type = constants.FHIR_CONTACT_EMAIL
            value = contact["value"]

            telecom_dict['system'] = type
            telecom_dict['value'] = value

            telecom_list.append(telecom_dict)
    except KeyError:
        raise exception.InvalidDataError

    data['telecom'] = telecom_list
    return data