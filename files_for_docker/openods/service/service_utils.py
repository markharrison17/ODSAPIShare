from openods import constants


def build_org(org, address, role, contact, relationship, successor, is_fhir):

    org_dict = {}
    org_dict[constants.ORGANISATION] = org
    org_dict[constants.ADDRESS] = address
    org_dict[constants.ROLES] = role
    org_dict[constants.CONTACTS] = contact
    if not is_fhir:
        org_dict[constants.RELATIONSHIP] = relationship
        org_dict[constants.SUCCESSORS] = successor

    return org_dict


