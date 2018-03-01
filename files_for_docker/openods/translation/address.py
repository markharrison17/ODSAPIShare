import collections
from openods.translation import translation_utils
from openods import exception


def build_address(address, result_data):

    if len(address) == 0:
        return result_data

    address = translation_utils.remove_none_values_from_dictionary(address)
    location = collections.OrderedDict()
    try:
        location['AddrLn1'] = address.pop('address_line1')
    except KeyError:
        raise exception.InvalidDataError
    if 'address_line2' in address: location['AddrLn2'] = address.pop('address_line2')
    if 'address_line3' in address: location['AddrLn3'] = address.pop('address_line3')
    if 'town' in address: location['Town'] = address.pop('town')
    if 'county' in address: location['County'] = address.pop('county')
    if 'post_code' in address: location['PostCode'] = address.pop('post_code')
    if 'country' in address: location['Country'] = address.pop('country')

    result_data['GeoLoc'] = dict(Location=location)

    return result_data


def build_address_for_fhir(address, data):

    if len(address) == 0:
        return data

    address = translation_utils.remove_none_values_from_dictionary(address)
    address_dict = {}

    line_list = []
    try:
        addrLn1 = address.pop('address_line1')
        line_list.append(addrLn1)
    except KeyError:
        raise exception.InvalidDataError

    if 'address_line2' in address:
        addrLn2 = address.pop('address_line2')
        line_list.append(addrLn2)
    if 'address_line3' in address:
        addrLn3 = address.pop('address_line3')
        line_list.append(addrLn3)
    address_dict['line'] = line_list

    if 'town' in address:
        town = address.pop('town')
        address_dict['city'] = town
    if 'county' in address:
        county = address.pop('county')
        address_dict['district'] = county
    if 'post_code' in address:
        postcode = address.pop('post_code')
        address_dict['postalCode'] = postcode
    #  This line really shouldn't exist but somehow it solves the issue of everything blowing up
    #  if the post_code is the last key to be popped. This may be a pycharm/python3.6.1 issue
    #  but it seems worth leaving this until we 'solve' the issue. This ONLY seems to be an issue
    #  when debugging through pycharm.
    # nonsense = "nonsense"
    if 'country' in address:
        country = address.pop('country')
        address_dict['country'] = country


    data['address'] = address_dict

    return data