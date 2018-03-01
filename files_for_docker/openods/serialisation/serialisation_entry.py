import json

from openods import constants
from openods import log_utils


def create_response_body(org_dict, format, request_id, is_fhir):
    log_utils.log_layer_entry(constants.SERIALISATION, request_id)


    if is_fhir:
        response_body =  fhir_format(org_dict, request_id, format)

    else:
        response_body = ord_format(org_dict, request_id, format) if org_dict else None

    log_utils.log_layer_exit(constants.SERIALISATION, request_id)

    return response_body

# ORD


def ord_format(data, request_id, format=constants.JSON):
    try:
        del data['org_lastchanged']
    except KeyError:
        pass
    if format == constants.JSON:
        result = json.dumps(data)
    elif format == constants.XML:
        result = ord_dict_to_xml(data, None, request_id)
        result = constants.XML_TAG + result
    else:
        raise Exception('requestId="{request_id}"|Unexpected format requested for Summary'.format(
            request_id=request_id))

    return result


def ord_dict_to_xml(data, root_element, request_id):
    xml = ''
    attribute_xml = ''
    children = []
    child_element_xml = []

    if isinstance(data, dict):
        for key, value in dict.items(data):
            if isinstance(value, dict):
                if key == constants.RELS or key == constants.SUCCS or key == constants.ROLES or\
                                key == constants.CONTACTS:
                    # children.append("<" + key + ">")
                    child_element_xml.append("<" + key + ">")
                    for obj in value[key[:-1]]:
                        # children.append(ord_dict_to_xml(obj, key[:-1], request_id))
                    # children.append("</" + key + ">")
                        child_element_xml.append(ord_dict_to_xml(obj, key[:-1], request_id))
                    child_element_xml.append("</" + key + ">")
                else:
                    # children.append(ord_dict_to_xml(value, key, request_id))
                    child_element_xml.append(ord_dict_to_xml(value, key, request_id))
            elif isinstance(value, list):
                if key == constants.DATES:
                    # children.append(dates_list_to_xml(value))
                    child_element_xml.append(dates_list_to_xml(value))
                elif key == "Organisations":
                    children.append("<" + key + ">")
                    children.append(orgs_list_to_xml(value))
                    children.append("</" + key + ">")
                else:
                    raise Exception('requestId="{request_id}"|Non date, not organisation '
                                    'list'.format(request_id=request_id))
            elif isinstance(value, bool):
                if (key[0].isupper()):
                    child_element_xml.append( '<' + key + '>' + str(value).lower() + '</' + key + '>')
                else:
                    attribute_xml = attribute_xml + ' ' + key + '="' + str(value).lower() + '"'
            else:
                if (key[0].isupper()):
                    if (key == constants.LAST_CHANGED_SINCE or key == constants.STATUS):
                        child_element_xml.append('<' + key + ' ' + 'value="' + encode_html_characters(value) + '"/>')
                    else:
                        child_element_xml.append('<' + key + '>' + encode_html_characters(value) + '</' + key + '>')
                else:
                    attribute_xml = attribute_xml + ' ' + key + '="' + str(value) + '"'

    else:
        raise Exception('requestId="{request_id}"|Data element of unexpected instance'.format(
            request_id=request_id))

    xml = create_xml(attribute_xml, child_element_xml, children, root_element, xml)

    return xml


def orgs_list_to_xml(data):
    xml = ''
    child_element_xml = []

    if isinstance(data, list):
        for value in data:
            xml = xml + orgs_list_to_xml(value)
    if isinstance(data, dict):
        for key, value in dict.items(data):
            child_element_xml.append('<' + key + '>' + encode_html_characters(value) + '</' + key + '>')

        xml = xml + '<Organisation>'
        for child_element in child_element_xml:
            xml = xml + child_element
        xml = xml + '</Organisation>'

    return xml


def dates_list_to_xml(data):
    xml = ''
    child_element_xml = []

    if isinstance(data, list):
        for value in data:
            xml = xml + dates_list_to_xml(value)
    if isinstance(data, dict):
        for key, value in dict.items(data):
            child_element_xml.append('<' + key + ' ' + 'value="' + value + '"/>')

        xml = xml + '<Date>'
        for child_element in child_element_xml:
            xml = xml + child_element
        xml = xml + '</Date>'

    return xml


# FHIR

def fhir_format(data, request_id, format):
    if format == constants.JSON:
        return json.dumps(data) if data else None
    elif format == constants.XML:
        if data.get('name') == 'ODS API Organization Role':
            namespace = 'xmlns:n1="http://hl7.org/fhir"'
            resource_type = "CodeSystem"
        else:
            namespace = constants.FHIR_NAMESPACE
            resource_type = "Organization"

        xml = fhir_dict_to_xml(data, resource_type, request_id, ' ' + namespace)
        xml = constants.XML_TAG + xml
        result = xml

    return result


def fhir_dict_to_xml(data, root_element, request_id, attribute_xml):
    xml = ''
    children = []
    child_element_xml = []
    if isinstance(data, dict):
        for key, value in dict.items(data):
            if isinstance(value, dict):
                if key == "resource":
                    child_element_xml.append('<' + key + '>' + fhir_dict_to_xml(value, "", request_id, "") + '</' + key + '>')
                else:
                    child_element_xml.append(fhir_dict_to_xml(value, key, request_id, ""))
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, dict):
                        if key == 'extension':
                            attributes = ' url="' + v.pop('url') + '"'
                        else:
                            attributes = ""
                        child_element_xml.append(fhir_dict_to_xml(v, key, request_id, attributes))
                    elif isinstance(v, str):
                        child_element_xml.append('<' + key + ' value="' + encode_xml(v) + '"/>')
                    else:
                        raise Exception("List does not contain dictionaries or strings")
            elif isinstance(value, bool):
                if value == True:
                    child_element_xml.append('<' + key + ' value="' + 'true' + '"/>')
                else:
                    child_element_xml.append('<' + key + ' value="' + 'false' + '"/>')
            else:
                if key == "resource":
                    child_element_xml.append('<' + key + '>' + fhir_dict_to_xml(value, "", request_id, "") + '</' + key + '>')
                elif key == "resourceType":
                    root_element = value
                else:
                    child_element_xml.append('<' + key + ' value="' + encode_xml(value) + '"/>')
    else:
        raise Exception('requestId="{request_id}"|Data element of unexpected instance'.format(
            request_id=request_id))
    xml = create_xml(attribute_xml, child_element_xml, children, root_element, xml)
    return xml


# Utils

def create_xml(attribute_xml, child_element_xml, children, root_element, xml):
    if root_element is not None:
        # add in attributes
        close_element = '>'
        if (len(children) + len(child_element_xml)) < 1:
            close_element = '/>'
        xml = '<' + root_element + attribute_xml + close_element + xml
    for child_element in child_element_xml:
        xml = xml + child_element
    for child in children:
        xml = xml + child
    if root_element is not None:
        end_xml = '</' + root_element + '>'
        if len(children) + len(child_element_xml) < 1:
            end_xml = ''
        xml = xml + end_xml
    return xml


def encode_xml(string):
    string = string.replace("&","&amp;")
    string = string.replace("<","&lt;")
    string = string.replace(">","&gt;")
    string = string.replace("'","&apos;")
    string = string.replace('"',"&quot;")
    return string


def encode_html_characters(s):
    s = s.replace("&", "&amp;")
    return s
