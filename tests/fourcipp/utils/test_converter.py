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
"""Test Converter class."""

import numpy as np
import pytest

from fourcipp.utils.converter import Converter


def test_basic_python_types():
    """Test identity conversion for basic Python types."""
    converter = Converter()
    for value in [123, 12.5, "text", True]:
        assert converter(value) == value


def test_list_and_dict_conversion():
    """Test identity conversion of nested lists and dictionaries."""
    converter = Converter()
    input_data = {"a": [1, 2, {"b": "text"}], "c": True}
    assert converter(input_data) == input_data


def test_nested_numpy_structures():
    """Test nested structures with NumPy types."""
    converter = Converter().register_numpy_types()

    obj = {
        "arr": np.array([1, 2, 3]),
        "nested": {"scalar": np.int64(42), "float": np.float32(3.1)},
    }

    expected = {
        "arr": [1, 2, 3],
        "nested": {
            "scalar": 42,
            "float": pytest.approx(3.1),
        },
    }

    result = converter(obj)
    assert result["arr"] == expected["arr"]
    assert result["nested"]["scalar"] == expected["nested"]["scalar"]
    assert result["nested"]["float"] == expected["nested"]["float"]


def test_register_custom_type():
    """Test custom type registration and conversion."""

    class Custom:
        """Custom class for testing."""

        def __init__(self, value):
            self.value = value

    def convert_custom(converter, obj):
        """Custom conversion function for the Custom class."""
        return {"custom_value": obj.value}

    converter = Converter().register_type(Custom, convert_custom)

    custom_obj = Custom("abc")
    result = converter(custom_obj)
    assert result == {"custom_value": "abc"}


def test_not_convertible_type():
    """Test conversion of a non-convertible type."""

    # register a type to enable conversion
    converter = Converter().register_numpy_types()

    class UnknownType:
        """Unknown type for testing."""

        pass

    with pytest.raises(TypeError, match=r"can not be converted"):
        converter(UnknownType())
