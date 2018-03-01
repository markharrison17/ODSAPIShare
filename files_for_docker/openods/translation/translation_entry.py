import collections
import urllib.parse
import uuid
import datetime

from openods import constants, exception, log_utils, app
from openods.translation import organisation as org_translation
from openods.translation import contact as contact_translation
from openods.translation import address as addr_translation
from openods.translation import role as role_translation
from openods.translation import relationship as relation_translation
from openods.translation import successor as successor_translation
from openods.translation import codesystem as codesystem_translation
from openods.translation import translation_utils as utils_translation


def structure_org(org_dict, url_root, request_id, is_fhir):
    log_utils.log_layer_entry(constants.TRANSLATION, request_id)

    if is_fhir:
        org_result = restructure_fhir_org(org_dict, url_root)
    else:
        org_result = restructure_ord_org(org_dict)

    log_utils.log_layer_exit(constants.TRANSLATION, request_id)

    return org_result

# ORD
def restructure_ord_org(org_dict):
    result = collections.OrderedDict()
    result = org_translation.build_organisation(org_dict['Organisation'], result)
    result = addr_translation.build_address(org_dict['Address'], result)
    result = contact_translation.build_contacts(org_dict['Contacts'], result)
    result = role_translation.build_roles(org_dict['Roles'], result)
    result = relation_translation.build_relationships(org_dict['Relationships'], result)
    result = successor_translation.build_successors(org_dict['Successors'], result)

    result = {constants.ORGANISATION: result}

    return result


def structure_ord_org_summary(orgs, app_hostname, request_id):
    log_utils.log_layer_entry(constants.TRANSLATION,request_id)

    organisations = list()
    org_dict = {}

    try:
        for organisation in orgs:

            organisation = utils_translation.remove_none_values_from_dictionary(organisation)

            organisation['Name'] = organisation.pop('name')
            organisation['OrgId'] = organisation.pop('odscode')
            organisation['Status'] = organisation.pop('status')
            organisation['OrgRecordClass'] = organisation.pop('record_class')
            if 'post_code' in organisation: organisation['PostCode'] = organisation.pop(
                'post_code')
            organisation['LastChangeDate'] = organisation.pop('last_changed')
            organisation['PrimaryRoleId'] = organisation.pop('code')
            organisation['PrimaryRoleDescription'] = organisation.pop('displayname')

            link = str.format('{0}/{1}',
                                        app_hostname,
                                        organisation['OrgId'])

            organisation['OrgLink'] = link

            organisations.append(organisation)

        org_dict['Organisations'] = organisations
    except KeyError:
        raise exception.InvalidDataError

    log_utils.log_layer_exit(constants.TRANSLATION, request_id)
    return org_dict

def build_ord_last_changed_summary(ods_codes, format, app_hostname):
    try:
        for organisation in ods_codes:
            orglink_url = urllib.parse.urljoin(app_hostname, app.config['API_PATH'] + '/' + 'organisations' + '/'
                                                    + organisation.pop('odscode'))
            if format == constants.XML:
                orglink_url += "?" + constants.FORMAT + "=" + constants.XML

            organisation['OrgLink'] = orglink_url

        return {'Organisations': ods_codes }
    except KeyError:
        raise exception.InvalidDataError

# FHIR

def restructure_fhir_org(org_dict, url_root):
    result = collections.OrderedDict()
    result['resourceType'] = "Organization"
    result['id'] = org_dict['Organisation']['odscode']
    meta_dict = collections.OrderedDict()
    meta_dict['lastUpdated'] = org_dict['Organisation']['last_changed'] + "T00:00:00+00:00"
    meta_dict['profile'] = constants.FHIR_ORGANISATION_URI
    result['meta'] = meta_dict
    result['extension'] = []
    result = org_translation.build_organisation_for_fhir(org_dict['Organisation'], result)
    result = contact_translation.build_contacts_for_fhir(org_dict['Contacts'], result)
    result = addr_translation.build_address_for_fhir(org_dict['Address'], result)
    result = role_translation.build_roles_for_fhir(org_dict['Roles'], result, url_root)

    return result


def structure_fhir_organisations_bundle(orgs, count, limit, page, request, request_id):
    log_utils.log_layer_entry(constants.TRANSLATION, request_id)

    link_list = []

    if int(float(limit)) > 0:
        link_list = utils_translation.create_link_list(request, count, page, limit)
    bundle_dict = {}
    bundle_dict['resourceType'] = "Bundle"
    bundle_dict['id'] = str(uuid.uuid4())
    bundle_dict['meta'] = {"lastUpdated": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")+ "+00:00"}
    bundle_dict['type'] = constants.FHIR_BUNDLE_SEARCHSET
    bundle_dict['total'] = str(count)
    if int(float(limit)) > 0:
        bundle_dict['link'] = link_list
        bundle_dict['entry'] = create_entry_list(orgs, request.base_url, request.url_root)

    log_utils.log_layer_exit(constants.TRANSLATION, request_id)

    return bundle_dict


def create_entry_list(orgs, base_url, root_url):
    entry_list = []
    for org in orgs:
        entry_dict = {}
        entry_dict['fullUrl'] = base_url + "/" + org['Organisation']['odscode']

        entry_dict['resource'] = restructure_fhir_org(org, root_url)

        entry_list.append(entry_dict)

    return entry_list


def structure_fhir_rolesystem(rolecode_dicts_list, format, request_url, request_id):
    log_utils.log_layer_entry(constants.TRANSLATION, request_id)

    master_dict = collections.OrderedDict()

    if format == constants.JSON:
        master_dict["resourceType"] = "CodeSystem"

    master_dict["url"] = request_url
    master_dict["version"] = constants.FHIR_ROLES_VERSION
    master_dict["name"] = constants.FHIR_ROLES_ENDPOINT_NAME
    master_dict["status"] = constants.FHIR_ROLES_ENDPOINT_STATUS
    master_dict["date"] = "date_placeholder"
    master_dict["publisher"] = constants.FHIR_ROLES_ENDPOINT_PUBLISHER
    master_dict["contact"] = codesystem_translation.create_contact_list()
    master_dict["description"] = constants.FHIR_ROLES_ENDPOINT_DESCRIPTION
    master_dict["copyright"] = constants.FHIR_ROLES_ENDPOINT_COPYRIGHT
    master_dict["content"] = constants.FHIR_ROLES_ENDPOINT_CONTENT
    master_dict["concept"] = codesystem_translation.create_rolecodes_list_for_response_dictionary(rolecode_dicts_list)

    log_utils.log_layer_exit(constants.TRANSLATION, request_id)


    return master_dict


