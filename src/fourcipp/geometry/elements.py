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
from functools import partial

from fourcipp import CONFIG
from fourcipp.reader import load_4C_yaml
from fourcipp.utils.metadata import METADATA_TO_PYTHON

SUPPORTED_TYPES_ELEMENTS = list(METADATA_TO_PYTHON.keys()) + ["vector"]


def _left_pop(line_list, n_entries):
    entries = line_list[:n_entries]
    del line_list[:n_entries]
    return entries


def _extract_entry(line_list, entry_type):
    return entry_type(_left_pop(line_list, 1)[0])


def _extract_vector(line_list, entry_type, size):
    return [entry_type(e) for e in _left_pop(line_list, size)]


def _entry_casting_factory(spec):
    if spec["type"] in METADATA_TO_PYTHON:
        return partial(_extract_entry, entry_type=METADATA_TO_PYTHON[spec["type"]])
    elif spec["type"] == "vector":
        value_type = METADATA_TO_PYTHON[spec["value_type"]["type"]]
        return partial(_extract_vector, entry_type=value_type, size=spec["size"])
    else:
        raise NotImplementedError(f"Entry type {spec['type']} not supported.")


def _elements_casting_factory(fourc_metadata):
    if fourc_metadata["type"] in SUPPORTED_TYPES_ELEMENTS:
        return {fourc_metadata["name"]: _entry_casting_factory(fourc_metadata)}

    # Supported collections
    if fourc_metadata["type"] in ["all_of", "group", "one_of"]:
        specs = {}
        for spec_i in fourc_metadata["specs"]:
            specs.update(_elements_casting_factory(spec_i))

        if fourc_metadata["type"] == "group":
            return {fourc_metadata["name"]: specs}
        else:
            return specs
    else:
        raise NotImplementedError(f"Entry type {fourc_metadata['type']} not supported.")


DEFAULT_METADATA = CONFIG["profiles"]["default"]["4C_metadata_path"]
if DEFAULT_METADATA is not None:
    _ELEMENTS = _elements_casting_factory(
        load_4C_yaml(DEFAULT_METADATA)["legacy_element_specs"]
    )
else:
    _ELEMENTS = None


def read_element(line, elements_data=_ELEMENTS):
    line_list = [l.strip() for l in line.split("#")[0].split() if l.strip()]
    element_id = int(line_list.pop(0))
    element_type = line_list.pop(0)
    cell_type = line_list.pop(0)
    data = elements_data[element_type][cell_type]

    element = {
        "id": element_id,
        "type": element_type,
        "cell": {"type": cell_type, "nodes": data[cell_type](line_list)},
    }

    while line_list:
        key = line_list.pop(0)
        element[key] = data[key](line_list)

    return element
