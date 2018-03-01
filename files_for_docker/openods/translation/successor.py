import collections
from openods.translation import translation_utils
from openods import exception
from openods import constants


def build_successors(successors_rows, data):

    if len(successors_rows) == 0:
        return data

    succ_dict = dict()
    successors = list()

    try:
        for successor in successors_rows:
            successor_dict = collections.OrderedDict()

            successor_dict['uniqueSuccId'] = successor.pop('uniqueid')
            successor_dict[constants.DATES] = translation_utils.get_dates_for_org(successor)
            successor_dict['Type'] = successor.pop('type')
            successor_dict['Target'] = translation_utils.get_target_for_org(successor)

            successors.append(successor_dict)

        succ_dict['Succ'] = successors
        data[constants.SUCCS] = succ_dict
    except KeyError:
        raise exception.InvalidDataError

    return data
