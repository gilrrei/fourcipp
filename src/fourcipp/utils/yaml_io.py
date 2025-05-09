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
"""YAML io."""

import io
import json
import pathlib

import ruamel.yaml
import ruamel.yaml.representer
import ryml


def load_yaml(path_to_yaml_file):
    """Load yaml files.

    rapidyaml is the fastest yaml parsing library we could find. Since it returns custom objects we
    use the library to emit the objects to json and subsequently read it in using the json library.
    This is still two orders of magnitude faster compared to other yaml libraries.

    Args:
        path_to_yaml_file (str): Path to yaml file

    Returns:
        dict: Loaded data
    """

    data = json.loads(
        ryml.emit_json(
            ryml.parse_in_arena(pathlib.Path(path_to_yaml_file).read_bytes())
        )
    )
    return data


def _use_square_braces(data):
    """Check if sequence should use '-' or '[ ]'."""
    if isinstance(data, list):
        return_val = True
        for entry in data:
            return_val = return_val and _use_square_braces(entry)
            if not return_val:
                break
        return return_val

    elif (
        isinstance(data, (int, float)) and not isinstance(data, bool)
    ) or data is None:
        return True
    else:
        return False


class FourCYamlRepresenter(ruamel.yaml.RoundTripRepresenter):

    def represent_sequence(self, tag, data, flow_style=None):
        if _use_square_braces(data):
            return super().represent_sequence(tag, data, flow_style=True)
        else:
            return super().represent_sequence(tag, data, flow_style=False)


def get_4C_yaml(data, sort_keys=False):
    # Ignore alias or anchors in dumps
    ruamel.yaml.representer.RoundTripRepresenter.ignore_aliases = lambda x, y: True

    # Set the desired sequence dump type
    ruamel.yaml.representer.RoundTripRepresenter = FourCYamlRepresenter

    # Currently using ruamel.yaml, will probably change in the future
    YAML = ruamel.yaml.YAML()

    # Some nice settings
    YAML.indent(offset=2, sequence=4, mapping=2)

    # Avoid wrapping of long lines
    YAML.width = 4096

    # Sort keys
    if sort_keys:
        data = {key: data[key] for key in sorted(data.keys())}

    buffer = io.StringIO()
    YAML.dump(data, buffer)
    return buffer.getvalue()


def dump_yaml(data, path_to_yaml_file, sort_keys=False):
    """Dump yaml to file.

    Args:
        data (dict): Data to dump.
        path_to_yaml_file (str): Yaml file path
        sort_keys (bool): If true sort the sections by section name
    """
    pathlib.Path(path_to_yaml_file).write_text(
        get_4C_yaml(data, sort_keys=sort_keys), encoding="utf-8"
    )


data_examples = {
    "a": [1, 2, 0.3, None],
    "b": [1, 2, "xxxx", "aa"],
    "c": ["a", "b"],
    "cd": "b",
    "cdc": {"b": 35, "l": 451},
    "d": [[[1, 2], [3, None]], [True, False]],
}

print(get_4C_yaml(data_examples))
