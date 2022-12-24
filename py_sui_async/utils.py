import logging

from pretty_utils.type_functions.strings import text_between

from py_sui_async.models import ObjectType, Coin


async def parse_type(raw_type: str) -> ObjectType:
    type_instance = ObjectType(raw_type=raw_type)
    try:
        type_list = raw_type.split('::')
        if '0x' not in type_list[0]:
            type_list = ['0x2'] + type_list

        type_instance.package_id = type_list[0]
        type_instance.module = type_list[1]
        if 'Coin' in type_list[2]:
            type_details = text_between(raw_type, '<', '>').split('::')
            type_instance.structure = Coin(package_id=type_details[0], name=type_details[1], symbol=type_details[2])

        else:
            type_instance.structure = '::'.join(type_list[2:])

    except:
        logging.exception('parse_type')

    finally:
        return type_instance
