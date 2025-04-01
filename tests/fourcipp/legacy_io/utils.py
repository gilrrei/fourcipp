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
"""Utils for legacy io testing."""

from fourcipp.legacy_io.element import to_dat_string

# This map is used to generate elements from the metadata file
_TESTING_MAP = {"int": 4, "double": 2.11, "string": "text", "bool": True}


def reference_value_from_group(group):
    """Generate line from group.

    Args:
        group (dict): Metadata dict for the group

    Returns:
        str: inline
    """

    keyword_parameters = {}
    positional_parameters = {}

    for parameter in group["specs"]:
        entry = None
        if parameter["type"] in _TESTING_MAP:
            entry = _TESTING_MAP[parameter["type"]]
        elif parameter["type"] == "vector":
            entry = [_TESTING_MAP[parameter["value_type"]["type"]]] * parameter["size"]
        elif parameter["type"] == "enum":
            entry = parameter["choices"][0]["name"]
        else:
            raise ValueError(f"Could not create testing line from {parameter['type']}")

        if parameter["name"].startswith("_positional"):
            _, _, position, _ = parameter["name"].split("_", 3)
            positional_parameters[int(position)] = entry
        else:
            keyword_parameters[parameter["name"]] = to_dat_string(entry)

    line_list = [
        to_dat_string(positional_parameters[e])
        for e in sorted(positional_parameters.keys())
    ]
    for e in keyword_parameters.items():
        line_list.extend(e)
    return "  ".join(line_list)
