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
"""Validation utils."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import jsonschema_rs

from fourcipp.utils.yaml_io import dict_to_yaml_string


class ValidationError(Exception):
    """FourCIPP validation error."""

    @classmethod
    def from_errors(
        cls, errors: Iterable[jsonschema_rs.ValidationError]
    ) -> ValidationError:
        """Create error from multiple errors.

        Args:
            errors: Errors to raise

        Returns:
            New error for this case
        """
        message = "\nValidation failed, due to the following parameters:"

        def indent(text: str, n_spaces: int = 4):
            """Indent the text."""
            indent_with_newline = "\n" + " " * n_spaces
            return indent_with_newline + text.replace("\n", indent_with_newline)

        def path_indexer(path: Sequence[str | int]) -> str:
            """Create a path representation to walk the dict."""
            path_for_data = ""
            for p in path:
                if isinstance(p, str):
                    p = '"' + p + '"'
                path_for_data += "[" + str(p) + "]"
            return path_for_data

        for error in errors:
            message += "\n\n- Parameter in " + path_indexer(error.instance_path)
            message += indent(indent(dict_to_yaml_string(error.instance), 4))
            message += indent("Error: " + error.message, 2)

        return cls(message)


def validate_using_json_schema(data: dict, json_schema: dict) -> bool:
    """Validate data using a JSON schema.

    Args:
        data: Data to validate
        json_schema: Schema for validation

    Returns:
        True if successful
    """
    validator = jsonschema_rs.validator_for(json_schema)
    try:
        validator.validate(data)
    except jsonschema_rs.ValidationError as exception:
        # Validation failed, look for all errors
        raise ValidationError.from_errors(validator.iter_errors(data)) from exception
    return True
