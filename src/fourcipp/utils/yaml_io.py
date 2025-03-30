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

import json
import pathlib

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
