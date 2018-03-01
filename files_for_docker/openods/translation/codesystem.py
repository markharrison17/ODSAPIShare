import collections

from openods import constants
from openods import exception



def create_contact_list():
    contactList = []
    contactDict = collections.OrderedDict()
    contactDict["name"] = constants.FHIR_ROLES_ENDPOINT_CONTACT_NAME
    telecomList = []

    telecomDict = collections.OrderedDict()

    telecomDict["system"] = "email"
    telecomDict["value"] = constants.FHIR_ROLES_ENDPOINT_TELECOM_EMAIL
    telecomDict["use"] = constants.FHIR_ROLES_ENDPOINT_TELECOM_USE

    telecomList.append(telecomDict)

    telecomDict = collections.OrderedDict()

    telecomDict["system"] = "phone"
    telecomDict["value"] = constants.FHIR_ROLES_ENDPOINT_TELECOM_PHONE_NO
    telecomDict["use"] = constants.FHIR_ROLES_ENDPOINT_TELECOM_USE

    telecomList.append(telecomDict)

    contactDict["telecom"] = telecomList
    contactList.append(contactDict)

    return contactList


def create_rolecodes_list_for_response_dictionary(rolecode_dicts_list):
    list_of_role_dicts_with_correct_key = []
    for role_dict in rolecode_dicts_list:
        individual_role_code_dict = {}

        if role_dict["id"].startswith("RO"):
            individual_role_code_dict["code"] = role_dict["id"][2:]  # removes RO from rolecode
        else:
            raise exception.RoleCodeError

        individual_role_code_dict["display"] = role_dict["displayname"]

        list_of_role_dicts_with_correct_key.append(individual_role_code_dict)

    return list_of_role_dicts_with_correct_key









