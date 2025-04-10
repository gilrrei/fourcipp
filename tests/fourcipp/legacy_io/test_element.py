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
    write_element,
)

from .utils import reference_value_from_group


def inline_element_from_spec(group, element_type):
    """Generate element line from specs.

    Args:
        group (dict): Metadata dict for the element group
        element_type (str): Element type

    Returns:
        str: inline element
    """

    # Add additional whitespaces to check the reader
    return f"42  {element_type} " + reference_value_from_group(group)


def inline_element_from_cell(cell_spec, element_type):
    """Generate inline element cell example.

    Args:
        spec (dict): Spec of the cell element combo
        element_type (str): Name of element

    Returns:
        list: List of example elements
    """
    cells = []

    if cell_spec["type"] == "one_of":
        for one_of_branch in cell_spec["specs"]:
            cells.append(inline_element_from_spec(one_of_branch, element_type))
    else:
        cells.append(inline_element_from_spec(cell_spec, element_type))

    return cells


def generate_elements_from_metadatafile():
    """Generate all possible elements from metadata.

    Returns:
        list: list of inline elements
    """
    data = CONFIG["4C_metadata"]["legacy_element_specs"]["specs"]

    elements = []
    for element_groups in data:
        for element in element_groups["specs"]:
            element_type = element.get("name", "")

            # Positional parameters are handled differently
            if element_type.startswith("_positional_"):
                continue

            # Loop over all elements
            for ele in element["specs"]:
                elements.extend(inline_element_from_cell(ele, element["name"]))
    return elements


_REFERENCE_ELEMENTS = generate_elements_from_metadatafile()


@pytest.mark.parametrize("element", _REFERENCE_ELEMENTS)
def test_elements_read_and_write(element):
    """Test elements read and write."""
    element_dict = read_element(element)
    element_line = write_element(element_dict)

    # Split into a list to account for additional whitespaces
    assert element.split() == element_line.split()
