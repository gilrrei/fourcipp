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
"""Test element reader and writer."""

import pytest

from fourcipp import CONFIG
from fourcipp.legacy_io.element import (
    read_element,
    to_dat_string,
    write_element,
)

# This map is used to generate elements from the metadata file
_TESTING_MAP = {"int": 4, "double": 2.11, "string": "text", "bool": True}


def inline_element_from_spec(group, element_type):
    """Generate element line from specs.

    Args:
        group (dict): Metadata dict for the element group
        element_type (str): Element type

    Returns:
        str: inline element
    """
    element_id = 42

    # Add additional whitespaces to check the reader
    line = f"{element_id}   {element_type} "

    for parameter in group["specs"]:
        line += " " + parameter["name"]
        entry = None
        if parameter["type"] in _TESTING_MAP:
            entry = _TESTING_MAP[parameter["type"]]
        elif parameter["type"] == "vector":
            entry = [_TESTING_MAP[parameter["value_type"]["type"]]] * parameter["size"]
        elif parameter["type"] == "enum":
            entry = parameter["choices"][0]["name"]
        else:
            raise ValueError(
                f"Could not create testing element from {parameter['type']}"
            )

        line += " " + to_dat_string(entry)

    return line


def generate_elements_from_metadatafile():
    """Generate all possible elements from metadata.

    Returns:
        list: list of inline elements
    """
    data = CONFIG["4C_metadata"]["legacy_element_specs"]["specs"]

    elements = []
    for element in data:
        element_type = element["name"]
        if element["specs"][0]["type"] == "one_of":
            for cell in element["specs"][0]["specs"]:
                elements.append(inline_element_from_spec(cell, element_type))
        else:
            elements.append(inline_element_from_spec(element["specs"][0], element_type))

    return elements


_REFERENCE_ELEMENTS = generate_elements_from_metadatafile()


@pytest.mark.parametrize("element", _REFERENCE_ELEMENTS)
def test_elements_read_and_write(element):
    """Test elements read and write."""
    element_dict = read_element(element)
    element_line = write_element(element_dict)

    # Split into a list to account for additional whitespaces
    assert element.split() == element_line.split()
