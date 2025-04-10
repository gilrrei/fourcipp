from fourcipp.utils.not_set import NotSet, pop_arguments
from loguru import logger


def iter_nested_dict(nested_dict, keys):

    # Start with the original data
    sub_data = nested_dict

    # Get from dict
    if isinstance(nested_dict, dict):
        # Loop over all keys
        for i, key in enumerate(keys):
            # Jump into the dict
            if isinstance(sub_data, dict):
                if key in sub_data:
                    # Jump into the entry key
                    sub_data = sub_data[key]
                else:
                    # Unknown key
                    raise KeyError(f"Key '{key}' not found in dictionary {sub_data}.")
            else:
                # Jump into the sub_data with the remaining keys
                yield from get_data_from_nested_dict(sub_data, keys[i:])

                # Exit function afterwards
                return

    # Check the last entry type
    # Dict: nothing to do
    if isinstance(sub_data, dict):
        yield sub_data
    # List: jump in an do it all over
    elif isinstance(sub_data, list):
        # Loop through every entry
        for item in sub_data:
            pprint(item)
            yield from get_data_from_nested_dict(item, keys[i + 1 :])

    else:
        # Unsupported type
        raise KeyError(
            f"The current data {sub_data} for type {type(sub_data)} for keys {keys} is neither a dict nor a list."
        )
    # Exit function afterwards
    return


def get_data_from_nested_dict(nested_dict, keys):
    """Get data from a nested dictionary using a series of keys.

    This method is implemented as a generator.

    Args:
        nested_dict (dict): The nested dictionary to retrive data from

    Yields:
        obj: data in the dictionary
    """

    # Start with the original data
    sub_data = nested_dict

    # Get from dict
    if isinstance(nested_dict, dict):
        # Loop over all keys
        for i, key in enumerate(keys):
            # Jump into the dict
            if isinstance(sub_data, dict):
                if key in sub_data:
                    # Jump into the entry key
                    sub_data = sub_data[key]
                else:
                    # Unknown key
                    raise KeyError(f"Key '{key}' not found in dictionary {sub_data}.")
            else:
                # Jump into the sub_data with the remaining keys
                yield from get_data_from_nested_dict(sub_data, keys[i:])

                # End function here
                return
    # Jump into the list
    elif isinstance(sub_data, list):
        # Loop through every entry
        for item in sub_data:
            yield from get_data_from_nested_dict(item, keys)

        # End function here
        return

    # Unknown type
    else:
        raise KeyError(
            f"The current data {sub_data} for keys {keys} is neither a dict nor a list."
        )

    # Yield the sub data
    yield sub_data


def keys_in_dict(nested_dict, keys):
    last_key = keys[-1]

    # Check if keys are in all subdicts
    return all(
        [
            last_key in entry
            for entry in get_data_from_nested_dict(nested_dict, keys[:-1])
        ]
    )


def remove_from_nested_dict(nested_dict, keys, default=NotSet):
    last_key = keys[-1]
    pop_args = pop_arguments(last_key, default)

    for entry in get_data_from_nested_dict(nested_dict, keys[:-1]):
        pprint(entry)
        yield entry.pop(*pop_args), entry


def replace_value(nested_dict, keys, new_value):
    last_key = keys[-1]
    for old_value, entry in remove_from_nested_dict(nested_dict, keys):
        logger.debug(f"Replacing {last_key}: from {old_value} to {new_value}")
        entry[last_key] = new_value


def make_default_explicit(nested_dict, keys, value):
    last_key = keys[-1]
    for entry in iter_nested_dict(nested_dict, keys[:-1]):
        for e in iter_nested_dict(entry, [last_key]):
            # if not last_key in entry:
            #    entry[last_key] = value
            print("e")
            pprint(e)


def make_default_implicit(nested_dict, keys, value):
    last_key = keys[-1]
    for entry in iter_nested_dict(nested_dict, keys[:-1]):
        print(entry[last_key])
        if isinstance(entry[last_key], list):
            idx = []
            for i, e in enumerate(iter_nested_dict(nested_dict, [last_key])):
                if e == value:
                    idx.append(i)
            entry.pop(idx[::-1])
        if entry == value:
            entry.pop(last_key)


# Example usage:
nested_dict = {
    "a": {
        "b": [
            {"c": 1, "d": {"e": [5, 1], "h": [5], "f": 2}},
            {"c": 2, "d": {"e": [6, 2], "h": [6], "f": 2}},
            {"c": 1, "d": {"e": [7, 3], "h": [7], "f": 2}},
        ],
        "f": 3,
    }
}


from pprint import pprint

if False:
    # Accessing and modifying values in the nested dictionary
    for entry in get_data_from_nested_dict(nested_dict, ("a", "b", "d", "e")):
        pprint(entry)  # Output: {'e': 5}, {'e': 6}, {'e': 7}
        entry[1] += 10  # Modify the value directly

    # Check the modified values
    for entry in get_data_from_nested_dict(nested_dict, ("a", "b", "d")):
        pprint(entry)  # Output: {'e': 15}, {'e': 16}, {'e': 17}

    result = get_data_from_nested_dict(nested_dict, ("a", "f"))
    pprint(list(result))  # Output: 3
    pprint(nested_dict)

    # This will raise a KeyError
    # result = get_data_from_nested_dict(nested_dict, ("a", "x"))
    # pprint(list(result))

    pprint(keys_in_dict(nested_dict, ("a", "b")))
    # pprint(keys_in_dict(nested_dict, ("a", "b", "g")))
    # pprint(keys_in_dict(nested_dict, ("a", "g", "d")))
    pprint(keys_in_dict(nested_dict, ("a", "b", "d", "e")))

    pprint("-" * 50)
    pprint(list(remove_from_nested_dict(nested_dict, ("a", "b", "d", "e"))))
    pprint(nested_dict)
    pprint("-" * 50)
    replace_value(nested_dict, ("a", "b", "d", "f"), "new_value")
    pprint(nested_dict)
    pprint("- -" * 25)
    make_default_explicit(nested_dict, ("a", "b", "d", "g"), 8)
    pprint(nested_dict)
    pprint("- -" * 25)
    # make_default_implicit(nested_dict, ("a", "b", "d", "h"), 6)
pprint(nested_dict)
pprint("- *" * 25)
make_default_implicit(
    nested_dict, ("a", "b"), {"c": 1, "d": {"e": [5, 1], "f": 2, "h": [5]}}
)
# make_default_implicit(nested_dict, ("a", "f"), 3)
print()
pprint(nested_dict)
