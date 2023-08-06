
# The API in first_stab is deprecated. Please use the API in this file instead
from nestedrecord.internal import encode_data, decode_data, decode_data_one_level, encode_error, encode_partially_encoded_data

def encode(
    data,
    partial=False, 
    dict_type=dict, 
    start_list_part='[', 
    end_list_part=']', 
    strict=False
):
    """\
    Encodes a data structure of nested records to a flat structure.
    """
    if partial == False:
        if dict_type==dict and strict==False:
            return encode_data(data, dict_type, start_list_part, end_list_part)
    else:
        return encode_partially_encoded_data(
            data, 
            dict_type=dict_type, 
            start_list_part=start_list_part, 
            end_list_part=end_list_part
        )
    raise NotImplementedError()

def decode(
    data,
    depth=None, 
    dict_type=dict,
    list_type=list, 
    start_list_part='[',
    end_list_part=']', 
    strict=False
):
    """\  
    Takes a flat dictionary with appropriately encoded keys and decodes it to a
    Python data structure of dictionaries and lists (not records and and lists
    of records).
    """
    if depth is None:
        if dict_type==dict and list_type==list and strict==False:
            return decode_data(data, list_type, dict_type, start_list_part, end_list_part)
        else:
            raise NotImplementedError()
    else:
        if dict_type==dict and list_type==list and strict==False:
            for x in range(depth):
                data = decode_data_one_level(data, list_type, dict_type, start_list_part, end_list_part)
            return data
        else:
            raise NotImplementedError()

def encodeNestedRecord(raise_on_error=True, *k, **p):
    def encodeNestedRecord_converter(conversion, state=None):
        if raise_on_error:
            conversion.result = encode(conversion.value, *k, **p)
        else:
            try:
                conversion.result = encode(conversion.value, *k, **p)
            except Exception(e):
                conversion.error = str(e) 
    return encodeNestedRecord_converter

def decodeNestedRecord(raise_on_error=True, *k, **p):
    def decodeNestedRecord_converter(conversion, state=None):
        if raise_on_error:
            conversion.result = decode(conversion.value, *k, **p)
        else:
            try:
                conversion.result = decode(conversion.value, *k, **p)
            except Exception(e):
                conversion.error = str(e) 
    return decodeNestedRecord_converter

