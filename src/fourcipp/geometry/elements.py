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

from fourcipp import CONFIG
from fourcipp.reader import load_yaml


from fourcipp.legacy_io.inline_dat import (
    inline_dat_read,
    casting_factory,
    get_line_list,
)


DEFAULT_METADATA = CONFIG["profiles"]["default"]["4C_metadata_path"]
if DEFAULT_METADATA is not None:
    _ELEMENT_CASTING = casting_factory(
        load_yaml(DEFAULT_METADATA)["legacy_element_specs"]
    )
else:
    _ELEMENT_CASTING = None

positional_casting = {
    0: {"name": "id", "function": int},
    1: {"name": "type", "function": str},
    2: {"name": "cell_type", "function": str},
}


def read_element(line, elements_casting=_ELEMENT_CASTING):
    line_list = get_line_list(line)

    # First entry is always the element id starting from 1
    element_id = int(line_list.pop(0))

    # Second entry is always the element type
    element_type = line_list.pop(0)

    # Third entry is the cell type
    cell_type = line_list.pop(0)

    element_parameter_casting = elements_casting[element_type][cell_type]

    element = {
        "id": element_id,
        "type": element_type,
        "cell_type": cell_type,
        "connectivity": element_parameter_casting[cell_type](line_list),
    } | inline_dat_read(line_list, element_parameter_casting)

    return element
