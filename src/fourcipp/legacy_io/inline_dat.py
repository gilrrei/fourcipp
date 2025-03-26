# The MIT License (MIT)
#
# Copyright (c) 2025 FourCIPP Authors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""Read inline dat strings."""

from functools import partial

from fourcipp.utils.metadata import METADATA_TO_PYTHON

# Metadata types currently supported
SUPPORTED_METADATA_TYPES = list(METADATA_TO_PYTHON.keys()) + ["vector", "enum"]


def to_dat_string(object):
    """Convert object to dat style string.
    Args:
        data (object): Object to be casted

    Returns:
        str: Object as dict
    """
    if isinstance(object, list):
        return " ".join([str(d) for d in object])
    elif isinstance(object, bool):
        return str(object).lower()
    return str(object)


def _left_pop(line_list, n_entries):
    """Pop entries the beginning of a list.

    Args:
        line_list (list): List to extract the entries
        n_entries (int): Number of entries starting from the beginning of the list

    Returns:
        list: Extracted entries
    """
    entries = line_list[:n_entries]
    del line_list[:n_entries]
    return entries


def _extract_entry(line_list, entry_type):
    """Extract a single entry from a line list.

    Args:
        line_list (list): List to extract the entries
        entry_type (callable): Function to cast the string into the desired object

    Returns:
        object: Casted object
    """
    return entry_type(_left_pop(line_list, 1)[0])


def _extract_vector(line_list, entry_type, size):
    """Extract a vector entry from a line list.

    Args:
        line_list (list): List to extract the entries
        entry_type (callable): Function to cast the string into the desired object
        size (int): Vector size

    Returns:
        list: Casted vector object
    """
    return [entry_type(e) for e in _left_pop(line_list, size)]


def _extract_enum(line_list, choices):
    """Extract enum entry from a line list.

    Args:
        line_list (list): List to extract the entries
        choices (list): Choices for the enum

    Returns:
        str: Valid enum entry
    """
    entry = _left_pop(line_list, 1)[0]
    if not entry in choices:
        raise ValueError(f"Unknown entry {entry}, valid choices are {choices}")
    return entry


def _entry_casting_factory(spec):
    """Create the casting function for a spec.

    Args:
        spec (dict): 4C metadata style object description

    Returns:
        callable: Casting function for the spec
    """
    if spec["type"] in METADATA_TO_PYTHON:
        return partial(_extract_entry, entry_type=METADATA_TO_PYTHON[spec["type"]])
    elif spec["type"] == "vector":
        value_type = METADATA_TO_PYTHON[spec["value_type"]["type"]]
        return partial(_extract_vector, entry_type=value_type, size=spec["size"])
    elif spec["type"] == "enum":
        choices = [s["name"] for s in spec["choices"]]
        return partial(_extract_enum, choices=choices)
    else:
        raise NotImplementedError(f"Entry type {spec['type']} not supported.")


def casting_factory(fourc_metadata):
    """Create casting object for the specs.

    Args:
        fourc_metadata (dict): 4C metadata style object description

    Returns:
        dict: Casting object for the specs by name
    """
    if fourc_metadata["type"] in SUPPORTED_METADATA_TYPES:
        return {fourc_metadata["name"]: _entry_casting_factory(fourc_metadata)}

    # Supported collections
    if fourc_metadata["type"] in ["all_of", "group", "one_of"]:
        specs = {}
        for spec_i in fourc_metadata["specs"]:
            specs.update(casting_factory(spec_i))

        if fourc_metadata["type"] == "group":
            return {fourc_metadata["name"]: specs}
        else:
            return specs
    else:
        raise NotImplementedError(f"Entry type {fourc_metadata['type']} not supported.")


def inline_dat_read(line_list, dat_casting):
    """Read inline dat to dict.

    Args:
        line_list (list): List to extract the entries
        dat_casting (dict): Dict with the casting

    Returns:
        dict: Entry as dict
    """
    entry = {}
    while line_list:
        key = line_list.pop(0)
        entry[key] = dat_casting[key](line_list)

    return entry
