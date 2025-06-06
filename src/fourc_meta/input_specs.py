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
from __future__ import annotations

import abc
import dataclasses
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Callable, Literal, TypeAlias

from fourcipp.utils.not_set import _NotSet
from fourcipp.utils.validation import ValidationError

NOTSET = _NotSet()


@dataclass(kw_only=True)
class InputSpec:
    spec_type: str
    name: str | None = None
    description: str | _NotSet = NOTSET
    required: bool = False
    noneable: bool = False
    defaultable: bool = False
    validator: Callable[[object], bool] | None = None

    def short_description(self):
        type_definition = self.spec_type

        if self.noneable:
            type_definition += " or null"

        if self.name:
            return self.name + f" ({type_definition})"
        else:
            type_definition

    @abc.abstractmethod
    def _validate(self, obj):
        pass

    def validate(self, obj):
        self._validate(obj)
        self.validator(obj)


@dataclass
class SpecsOperator:
    """Operates only on objects in the backend."""

    options: Sequence[SpecsContainer]  # branches are always objects


class All_Of(SpecsOperator):
    def validate(self, obj):
        for option in self.options:
            option.validate(obj)


class One_Of(SpecsOperator):
    def validate(self, obj):
        valid_options: list[int] = []
        for i, option in enumerate(self.options):
            try:
                option.validate(obj)
                valid_options.append(i)
            except ValidationError:
                pass
        if len(valid_options) == 0:
            raise ValidationError("Could not match any one")
        elif len(valid_options) > 1:
            raise ValidationError("Multiple validation at once!")


@dataclass(kw_only=True)
class SpecsContainer:
    description: str | _NotSet = NOTSET  # description for this object
    specs: (
        Sequence[InputSpec] | All_Of | One_Of
    )  # either a sequence of input specs or a single operator

    def validate(self, obj):
        for spec in self.specs:
            spec.validate(obj)


@dataclass(kw_only=True)
class Primitive(InputSpec):
    PRIMITIVE_TYPES = ["double", "int", "bool", "string", "path"]

    spec_type: Literal["double", "int", "bool", "string", "path"]
    default: object | _NotSet = NOTSET
    constant: object | _NotSet = NOTSET

    def _validate(self, obj):
        FOURC_BASE_TYPES_TO_PYTHON = {
            "double": float,
            "int": int,
            "bool": bool,
            "string": str,
            "path": str,
        }
        if not isinstance(obj, FOURC_BASE_TYPES_TO_PYTHON[self.spec_type]):
            raise ValidationError("A good text message")

        if self.validator is not None:
            self.validator(obj)


@dataclass
class Enum(InputSpec):
    spec_type = "enum"
    validator = None
    choices: Sequence[str]

    def _validate(self, obj):
        if obj not in self.choices:
            raise ValidationError("A good text message")


@dataclass
class Vector(InputSpec):
    spec_type = "vector"
    value_type: NATIVE_CPP_ALIAS
    size: int | None = None

    def _validate(self, obj):
        for entry in obj:
            self.value_type.validate(entry)

        if self.validator is not None:
            self.validator(obj)


@dataclass
class Map(InputSpec):
    spec_type = "map"
    value_type: NATIVE_CPP_ALIAS
    size: int | None = None

    def _validate(self, obj):
        for entry_name, entry_value in obj.items:
            if not isinstance(entry_name, str):
                raise ValidationError("Nice message")
            self.value_type.validate(entry_value)

        if self.validator is not None:
            self.validator(obj)


NATIVE_CPP_ALIAS: TypeAlias = Primitive | Enum | Vector | Map
NATIVE_CPP_TYPES = [Primitive, Enum, Vector, Map]


@dataclass
class Selection(InputSpec):
    spec_type = "selection"
    choices: dict[str, SpecsContainer]
    selector: str

    def _validate(self, obj: dict):
        if not obj.get(self.selector) in self.choices:
            raise ValidationError("Selector not found!")

        self.choices[obj.get(self.selector)].validate(obj)

        if self.validator is not None:
            self.validator(obj)


@dataclass
class Group(InputSpec):
    spec_type = "group"
    object: SpecsContainer

    def _validate(self, obj: dict):
        self.object.validate(obj)

        if self.validator is not None:
            self.validator(obj)


@dataclass
class List(InputSpec):
    spec_type = "list"
    object: SpecsContainer
    size: int | None = None

    def _validate(self, obj):
        for entry in obj:
            self.object.validate(entry)

        if self.validator is not None:
            self.validator(obj)
