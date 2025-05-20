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
import numpy as np


class Converter:
    def __init__(self):
        self._custom_converters = {}

    def register_type(self, custom_type, converter_function):
        self._custom_converters[custom_type] = converter_function
        return self

    def register_types(self, types_dict):
        self._custom_converters.update(types_dict)
        return self

    def register_numpy_types(self):
        def convert_ndarray(converter, obj):
            return converter(obj.tolist())

        def convert_generic(converter, obj):
            return obj.item()

        self.register_type(np.generic, convert_generic)
        self.register_type(np.ndarray, convert_ndarray)
        return self

    def __call__(self, obj):
        # If no custom converters are present, no need to do a conversion
        if not self._custom_converters:
            return obj

        # Look if object is present in the custom converters
        for custom_type in self._custom_converters:
            if isinstance(obj, custom_type):
                # First match will be used.
                # Keep in mind for inheritance you have think about child classes!
                # Make sure if you have parent and child classes registerd separately, to first register the child classes!
                return self._custom_converters[custom_type](self, obj)

        # Lets convert
        match obj:
            # Convert the nested types
            case list():
                return [self(entry) for entry in obj]
            case set():
                return (self(entry) for entry in obj)
            case dict():
                return {k: self(v) for k, v in obj.items()}

            # Nothing to do here, since these are the accepted types
            case int() | float() | bool() | str():
                return obj

            # Type was not registered and is not one of the standards one
            case _:
                raise TypeError(
                    f"Object {obj} of type {type(obj)} can not be converted"
                )

    def __str__(self):
        string = "Converter with custom object (objects will be converted from top to bottom):"
        for k, v in self._custom_converters.items():
            string += f"\n\t{k}\t: {v}"

        return string
