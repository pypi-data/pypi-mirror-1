"""\
This version of the API is deprecated and will likely be slowly changed/removed
over time. Please use the ``nestedrecord.encode()`` and 
``nestedrecord.decode()`` functions instead.
"""

from conversionkit.exception import ConversionKitError

#
# ConversionKit code
#

def encode_error(
    conversion,
    list_type=list, 
    dict_type=dict, 
    start_list_part='[', 
    end_list_part=']',
):
    """\
    Takes a nested conversion and unnests the errors associated with it.
    """
    keys = dict_type()
    if isinstance(conversion.children, dict):
        for name, child in conversion.children.items():
            if not child.successful:
                # It could be a single value, a list or a dictionary
                keys[name] = child.error
                if isinstance(child.children, list):
                    # For each item in the list, recurse
                    for i, sub_child in enumerate(child.children):
                        if not sub_child.successful:
                            keys[name+start_list_part+str(i)+end_list_part] = sub_child.error
                            for k, v in encode_error(sub_child).items():
                                keys[name+start_list_part+str(i)+end_list_part+'.'+k] = v
                elif isinstance(child.children, dict):
                    # For each item in the dictionary, recurse
                    for key, sub_child in child.children.items():
                        if not sub_child.successful:
                            keys[name+'.'+key] = sub_child.error
                            for k, v in encode_error(sub_child).items():
                                keys[name+'.'+key+'.'+k] = v
                else:
                    keys[name] = child.error
            else:
                # Do some error checking to help avoid problems but don't go down the whole tree?
                if isinstance(child.children, list):
                    # For each item in the list, recurse
                    for i, sub_child in enumerate(child.children):
                        if not sub_child.successful:
                            raise ConversionKitError("The child %r has an error %r but the parent %r does not. This must be due to a faulty converter."%(sub_child, sub_child.error, child))
                elif isinstance(child.children, dict):
                    # For each item in the dictionary, recurse
                    for key, sub_child in child.children.items():
                        if not sub_child.successful:
                            raise ConversionKitError("The child %r has an error %r but the parent %r does not. This must be due to a fault converter."%(sub_child, sub_child.error, child))
    elif isinstance(conversion.children, list):
        raise ConversionKitError('Standalone lists are not supported by kerns format')
    else:
        pass
    return keys

def encode_partially_encoded_data(
    data,  
    dict_type=dict,
    start_list_part='[', 
    end_list_part=']', 
    list_item_mapping=None, 
):
    """\
    Takes a nested conversion and encodes it.

    Note: If a key is a string it treats it as already having been encoded 
    and just continues 

    This means you can do:

    ::

        encode_partially_encoded_data(
            {
                'work': {
                    'contact.phone': '01234 567890',    
                    'contact.mobile': '07574 123456',    
                    'project.name': 'Test Project',    
                }
            }
        )

    If you specify the ``list_item_mapping`` argument you can also map any keys
    which contain a list of single strings to the correct encoding for a list of
    dictionaries but you need to specify the key that will be used to turn the
    items in the list of strings into a dictionary. This is best demonstrated by an
    example:

    ::

        >>> encode_partially_encoded_data(
        ...     dict(members = ['james', 'paul', 'daniel']),
        ...     list_item_mapping(dict(members='person_id'),
        ... )
        >>> {'members-0.person_id': 'james', 'members-1.person_id': 'paul', 'members-1.person_id': 'daniel'}

    This technique is particularly useful for converting values submitted in
    multi-value HTML select fields or HTML check box groups to the correct data
    structures you need to work with in your applicaiton.
    """
    if list_item_mapping is None:
        list_item_mapping = {}
    keys = {}
    if isinstance(data, dict):
        for name, child in data.items():
            # It could be a single value, a list or a dictionary
            if isinstance(child, list):
                # For each item in the list, recurse
                for i, sub_child in enumerate(child):
                    if isinstance(sub_child, (unicode, str)):
                        if list_item_mapping.has_key(name):
                            keys[name+start_list_part+str(i)+end_list_part+'.'+list_item_mapping[name]] = sub_child
                        else:
                            keys[name+start_list_part+str(i)+end_list_part] = sub_child
                    else:
                        for k, v in encode_partially_encoded_data(
                            sub_child, 
                            dict_type=dict_type,
                            start_list_part=start_list_part, 
                            end_list_part=end_list_part, 
                            list_item_mapping=list_item_mapping,
                        ).items():
                            if k.startswith(start_list_part):
                                raise ConversionKitError(k)
                            keys[name+start_list_part+str(i)+end_list_part+'.'+k] = v
            elif isinstance(child, dict):
                # For each item in the dictionary, recurse
                for key, sub_child in child.items():
                    for k, v in  encode_partially_encoded_data(
                        sub_child,
                        dict_type=dict_type,
                        start_list_part=start_list_part, 
                        end_list_part=end_list_part, 
                        list_item_mapping=list_item_mapping,
                    ).items():
                        if k.startswith(start_list_part):
                            keys[name+'.'+key+k] = v
                        elif not k:
                            keys[name+'.'+key] = v
                        else:
                            keys[name+'.'+key+'.'+k] = v
            elif list_item_mapping.has_key(name):
                # XXX Is this safe to not catch things conflicting with the rule below?
                keys[name+start_list_part+'0'+end_list_part+'.'+list_item_mapping[name]] = child
            else:
                keys[name] = child
    elif isinstance(data, list):
        child = data
        name = ''
        for i, sub_child in enumerate(child):
            for k, v in encode_partially_encoded_data(
                sub_child,
                dict_type=dict_type,
                start_list_part=start_list_part, 
                end_list_part=end_list_part, 
                list_item_mapping=list_item_mapping,
            ).items():
                if k.startswith('-'):
                    raise ConversionKitError(k)
                keys[name+start_list_part+str(i)+end_list_part+'.'+k] = v
    elif isinstance(data, (unicode, str)):
        keys[''] = data
    else:
        raise ConversionKitError(
            'Objects of type %r are not supported' % type(data)
        )
    return keys

def encode_data(data, dict_type=dict, start_list_part='[', end_list_part=']'):
    """\
    Takes a nested conversion and encodes it.
    """
    keys = dict_type()
    if isinstance(data, dict):
        for name, child in data.items():
            # It could be a single value, a list or a dictionary
            if isinstance(child, list):
                # For each item in the list, recurse
                for i, sub_child in enumerate(child):
                    for k, v in encode_data(sub_child).items():
                        if k.startswith(start_list_part):
                            raise ConversionKitError(k)
                        keys[name+start_list_part+str(i)+end_list_part+'.'+k] = v
            elif isinstance(child, dict):
                raise Exception(
                    "The %r key couldn't be converted - you can't have "
                    "objects of %s nested within objects of %s"%(
                        name, 
                        type(child), 
                        type(data)
                    )
                )                
                # For each item in the dictionary, recurse
                for key, sub_child in child.items():
                    for k, v in encode_data(sub_child).items():
                        if k.startswith(start_list_part):
                            keys[name+'.'+key+k] = v
                        else:
                            keys[name+'.'+key+'.'+k] = v
            else:
                keys[name] = child
    elif isinstance(data, list):
        child = data
        name = ''
        for i, sub_child in enumerate(child):
            for k, v in encode_data(sub_child).items():
                if k.startswith(start_list_part):
                    raise ConversionKitError(k)
                keys[name+start_list_part+str(i)+end_list_part+'.'+k] = v
    else:
        raise ConversionKitError(
            'Objects of type %r are not supported' % type(data)
        )
    return keys

def _dict_split_next_level(
    data,
    dict_type=dict, 
):
    """
    Takes a dictionary of keys and values and splits the first part of the 
    key before a . character.
    """
    if not isinstance(data, dict):
        raise ConversionKitError('This is only supposed to be called on a dict')
    final = dict_type()
    for k, v in data.items():
        if '.' in k:
            parts = k.split('.')
            new_key = parts[0]
            rest = '.'.join(parts[1:])
            if not final.has_key(new_key):
                final[new_key] = {}
            if final[new_key].has_key(rest):
                raise ConversionKitError('Duplicate key found %r'%rest)
            final[new_key][rest] = v
        else:
            # We are already at a leaf node
            final[k] = v
    return final

def _dict_merge_next_level(
    data,
    list_type=list, 
    dict_type=dict, 
    start_list_part='-', 
    end_list_part='',
    strict=False,
):
    """
    Takes a dictionary where each of the keys have been expanded one level and
    merges those which represent a list of items
    """
    list_keys = {}
    dict_keys = dict_type()
    for k, v in data.items():
        if start_list_part in k or end_list_part in k:
            # It is a list so we need to know how many items there are
            parts = k.split(start_list_part)
            if not len(parts) == 2:
                raise ConversionKitError(
                    "The key %r contained too many %r characters"%(k, start_list_part)
                )
            name, index = parts
            try:
                index = index[:len(end_list_part)]
                index=int(index)
            except:
                raise ConversionKitError(
                    (
                        "The key %r has an invalid index (the part after the "
                        "%r character)"%start_list_part
                    ) % (name)
                )
            if k in dict_keys.keys():
                raise ConversionKitError(
                    'There is already a dictionary key with the key %r'%k
                )
            if not list_keys.has_key(name):
                list_keys[name] = {index: v}
            else:
                if list_keys[name].has_key(index):
                    raise ConversionKitError('The key %r exists twice'%k)
                list_keys[name][index] = v
        else:
            if k in list_keys.keys():
                raise ConversionKitError(
                    'There is already a list key with the key %r'%k
                )
            if k in dict_keys.keys():
                raise ConversionKitError(
                    'There is already a dictionary key with the key %r'%k
                )
            dict_keys[k] = v 
    for k, v in list_keys.items():
        counter = 0
        values = list_type()
        for index, value in v.items():
            if strict and index != counter:
                raise ConversionKitError(
                    'The items in the %r key are not numbered consecutively, item %s is labelled %s'%(k, counter, index)
                )
            values.append(value)
            counter += 1
        dict_keys[k] = values
    return dict_keys

def decode_data(
    data, 
    list_type=list, 
    dict_type=dict, 
    start_list_part='-', 
    end_list_part=''
):

    stripped_data = _dict_split_next_level(
        data,
        dict_type=dict_type,
    )
    merged_data = _dict_merge_next_level(
        stripped_data,
        list_type=list_type, 
        dict_type=dict_type,
        start_list_part=start_list_part,
        end_list_part=end_list_part,
    )

    final = dict_type()
    for k, v in merged_data.items():
        # The value could be a value, list or a dictionary. If it is a list 
        # you need to decode each one and append the results to a list
        if isinstance(v, list):
            new_list = list_type()
            for item in v:
                new_list.append(
                    decode_data(
                        item,
                        list_type=list_type, 
                        dict_type=dict_type,
                        start_list_part=start_list_part,
                        end_list_part=end_list_part
                    )
                )
            final[k] = new_list
        elif isinstance(v, dict):
            final[k] = decode_data(
                v, 
                list_type=list_type, 
                dict_type=dict_type,
                start_list_part=start_list_part,
                end_list_part=end_list_part
            )      
        else:      
            final[ k] = v
    return final

def decode_data_one_level(
    data,
    list_type=list,
    dict_type=dict, 
    start_list_part='[',
    end_list_part=']'
):
    stripped_data = _dict_split_next_level(data, dict_type=dict_type)
    merged_data = _dict_merge_next_level(
        stripped_data,
        list_type=list_type, 
        dict_type=dict_type,
        start_list_part=start_list_part,
        end_list_part=end_list_part,
    )
    return merged_data

def one_depth_variable_decode(conversion, state):
    conversion.result = decode_data_one_level(conversion.value)

def all_depths_variable_decode(conversion, state):
    conversion.result = decode_data(conversion.value)

def PartialEncode(list_item_mapping=None):
    def partial_encode_converter(conversion, state):
        conversion.result = encode_partially_encoded_data(conversion.value, list_item_mapping)
        # Best handled with an if_missing
        #for k in list_item_mapping.keys():
        #    if not conversion.result.has_key(k):
        #        conversion.result[k] = []
    return partial_encode_converter
    
