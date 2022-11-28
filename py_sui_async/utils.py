import logging

from pretty_utils.type_functions.strings import text_between

from py_sui_async.models import ObjectType


async def parse_type(raw_type: str) -> ObjectType:
    type = ObjectType(raw_type=raw_type)
    try:
        type_list = raw_type.split('::')
        type.package_id = type_list[0]
        type.type = type_list[1]
        if type.type == 'coin':
            type_details = text_between(raw_type, '<', '>').split('::')
            type.package_id = type_details[0]
            type.name = type_details[1]
            type.symbol = type_details[2]

        else:
            type.package_id = None
            type.name = type_list[2]
            type.symbol = None

    except:
        logging.exception('parse_type')

    finally:
        return type
