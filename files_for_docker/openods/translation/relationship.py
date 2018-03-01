import collections

from openods.translation import translation_utils
from openods import exception
from openods import constants


def build_relationships(relationship_rows, data):

    if len(relationship_rows) == 0:
        return data

    try:
        rels = collections.OrderedDict()
        relationships = list()

        for relationship in relationship_rows:

            relationship = translation_utils.remove_none_values_from_dictionary(relationship)

            target = translation_utils.get_target_for_org(relationship)
            relationship[constants.DATES] = translation_utils.get_dates_for_org(relationship)
            relationship['Status'] = relationship.pop('status')
            relationship['Target'] = target
            relationship['id'] = relationship.pop('code')
            relationship['uniqueRelId'] = int(relationship.pop('unique_id'))

            relationships.append(relationship)

        rels['Rel'] = relationships
        data[constants.RELS] = rels
    except:
        raise exception.InvalidDataError

    return data
