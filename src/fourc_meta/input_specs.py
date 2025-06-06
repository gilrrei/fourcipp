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
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Callable, Literal, Protocol, TypeAlias

from fourcipp.utils.not_set import _NotSet
from fourcipp.utils.validation import ValidationError

NOTSET = _NotSet()


def markdown_list_entry(key, val, indent=1):
    return f"\n{' ' * indent}- {key}: {val}"


def indent(string, indent=2):
    return string.replace("\n", "\n" + indent * " ")


class InputSpec:
    def __init__(
        self,
        spec_type: str,
        name: str | None = None,
        description: str | _NotSet = NOTSET,
        required: bool = False,
        noneable: bool = False,
        defaultable: bool = False,
        validator: Callable[[object], bool] | None = None,
    ):
        self.spec_type = spec_type
        self.name = name
        self.description = description
        self.required = required
        self.noneable = noneable
        self.defaultable = defaultable
        self.validator = validator

    def short_description(self):
        type_definition = self.spec_type

        if self.noneable:
            type_definition += " or null"

        if self.name:
            return self.name + f" ({type_definition})"
        else:
            return type_definition

    def __str__(self):
        return self.short_description()

    @classmethod
    def from_4C_metadata(cls, data_dict):
        data_dict.pop("type", None)
        return cls(**data_dict)


class All_Of:
    def __init__(
        self,
        specs: Sequence[InputSpec | All_Of | One_of],
        description: str | _NotSet = NOTSET,
    ):
        self._specs = All_Of.condense(specs)
        self.description = description

    @property
    def specs(self):
        return self._specs

    @specs.setter
    def specs(self, value):
        self._specs = All_Of.condense(value)

    @staticmethod
    def condense(specs):
        new_specs = []
        one_ofs = []
        for spec in specs:
            match spec:
                case InputSpec():
                    new_specs.append(spec)
                case All_Of():
                    if spec.is_one_of():
                        one_ofs.append(spec.specs[0])
                    else:
                        new_specs.extend(All_Of.condense(spec.specs))
                case One_Of():
                    one_ofs.append(spec)
                case _:
                    raise TypeError(f"Invalid type")

        if len(one_ofs) > 1:
            breakpoint()
            raise ValueError(
                f"More than one_of is not allowed {'\n'.join([str(oo) for oo in one_ofs])}"
            )

        if one_ofs:
            new_specs = [one_ofs[0].add_input_specs(new_specs)]

        return new_specs

    def __str__(self):
        string = f"All_of"
        string += self.specs_str()
        return string

    def specs_str(self):
        string = ""

        for spec in self.specs:
            string += "\n    - " + indent(str(spec), indent=4)

        return string

    def add_input_specs(self, input_specs):
        self._specs.extend(All_Of.condense(input_specs))
        self.specs = self._specs
        return self

    def is_one_of(self):
        # Am I a one of in disguise
        return len(self.specs) == 1 and isinstance(self.specs[0], One_Of)

    def gather_required(self):
        if not self.is_one_of():
            required_specs: Sequence[InputSpec] = []
            for spec in self.specs:
                if spec.required:
                    required_specs.append(spec.name)
                return required_specs

    @classmethod
    def from_4C_metadata(cls, data):
        if isinstance(data, dict):
            data.pop("type", None)
            specs = data.pop("specs", [])
            specs = [metadata_from_dict(spec) for spec in specs]
            return cls(specs=specs, **data)
        else:
            specs = [metadata_from_dict(spec) for spec in data]
            return cls(specs=specs)


class One_Of:
    def __init__(
        self,
        specs: Sequence[InputSpec | One_of],
        description: str | _NotSet = NOTSET,
    ):
        self.specs = specs
        self.description = description
        self.condense()

    @staticmethod
    def _condense_specs(specs):
        objects = []

        for spec in specs:
            match spec:
                case InputSpec():
                    objects.append(All_Of([spec]))
                case All_Of():
                    if spec.is_one_of():
                        objects.extend(spec.specs[0].condense().specs)
                    else:
                        objects.append(All_Of(spec.specs))
                case One_Of():
                    # One_of in one_of
                    objects.extend(spec.condense().specs)
                case _:
                    raise TypeError(f"Not supported type {type(spec)} for {spec}")

        return objects

    def condense(self):
        self.specs = self._condense_specs(self.specs)
        if any([isinstance(spec, One_Of) for spec in self.specs]):
            raise TypeError(f"One_of in one of is not possible: {self}")

        return self

    def add_input_specs(self, input_specs: Sequence[InputSpec]):
        for i in range(len(self.specs)):
            self.specs[i].add_input_specs(input_specs)
        return self.condense()

    def __str__(self):
        string = f"One_of"
        if self.description:
            string += f"\n  - Description: {self.description}"
        for spec in self.specs:
            string += "\n\n    - " + indent(str(spec), indent=4)  # str(spec)
        return string

    @classmethod
    def from_4C_metadata(cls, data_dict):
        data_dict.pop("type", None)
        specs = data_dict.pop("specs", [])
        specs = [metadata_from_dict(spec) for spec in specs]
        return cls(specs=specs, **data_dict)


class Primitive(InputSpec):
    PRIMITIVE_TYPES = ["double", "int", "bool", "string", "path"]

    def __init__(
        self,
        spec_type: Literal["double", "int", "bool", "string", "path"],
        name: str = None,
        description=NOTSET,
        required=False,
        noneable=False,
        defaultable=False,
        validator=None,
        default: object | _NotSet = NOTSET,
    ):
        super().__init__(
            spec_type, name, description, required, noneable, defaultable, validator
        )
        self.default = default

    @classmethod
    def from_4C_metadata(cls, data_dict):
        spec_type = data_dict.pop("type")
        return cls(spec_type=spec_type, **data_dict)

    def to_markdown(self, heading_level=0):
        type_definition = self.spec_type

        if self.noneable:
            type_definition += " or null"

        string = ""
        if self.name:
            string += "#" * (heading_level + 1) + " " + self.name

        string += f" ({type_definition}): *{self.description}*"

        string += "\n - <details>"
        string += "\n\n   <summary>More details</summary>\n"

        string += markdown_list_entry("optional", not self.required, 4)
        if not self.required:
            string += markdown_list_entry("default", self.default, 4)
        if self.validator is not None:
            string += markdown_list_entry("validator", self.validator, 4)

        string += "\n\n   </details>"

        return string


class Enum(InputSpec):
    def __init__(
        self,
        choices: Sequence[str],
        name=None,
        description=NOTSET,
        required=False,
        noneable=False,
        defaultable=False,
        validator=None,
        default: str | _NotSet = _NotSet,
    ):
        super().__init__(
            "enum", name, description, required, noneable, defaultable, validator
        )
        self.default = default
        self.choices = choices

    @classmethod
    def from_4C_metadata(cls, data_dict):
        data_dict.pop("type", None)
        choices = [c["name"] for c in data_dict.pop("choices")]
        return cls(choices=choices, **data_dict)

    def to_markdown(self, heading_level=0):
        type_definition = self.spec_type

        if self.noneable:
            type_definition += " or null"

        string = ""
        if self.name:
            string += "#" * (heading_level + 1) + " " + self.name

        string += f" ({type_definition}): *{self.description}*"

        string += "\n - <details>"
        string += "\n\n   <summary>More details</summary>\n"

        string += markdown_list_entry("choices", ",".join(self.choices), 4)
        string += markdown_list_entry("optional", not self.required, 4)
        if not self.required:
            string += markdown_list_entry("default", self.default, 4)
        if self.validator is not None:
            string += markdown_list_entry("validator", self.validator, 4)

        string += "\n\n   </details>"

        return string


class Vector(InputSpec):
    def __init__(
        self,
        value_type: NATIVE_CPP_ALIAS,
        size: int | None = None,
        name=None,
        description=NOTSET,
        required=False,
        noneable=False,
        defaultable=False,
        validator=None,
        default: str | _NotSet = _NotSet,
    ):
        super().__init__(
            "vector", name, description, required, noneable, defaultable, validator
        )
        if not isinstance(value_type, NATIVE_CPP_TYPES):
            raise TypeError(
                f"value type {value_type} has to be in {Primitive.PRIMITIVE_TYPES}"
            )
        self.value_type = value_type
        self.size = size
        self.default = default

    @classmethod
    def from_4C_metadata(cls, data_dict):
        data_dict.pop("type", None)
        value_type = metadata_from_dict(data_dict.pop("value_type"))
        return cls(value_type=value_type, **data_dict)


class Map(InputSpec):
    def __init__(
        self,
        value_type: NATIVE_CPP_ALIAS,
        size: int | None = None,
        name=None,
        description=NOTSET,
        required=False,
        noneable=False,
        defaultable=False,
        validator=None,
        default: str | _NotSet = _NotSet,
    ):
        super().__init__(
            "map", name, description, required, noneable, defaultable, validator
        )
        self.value_type = value_type
        self.size = size
        self.default = default

    @classmethod
    def from_4C_metadata(cls, data_dict):
        data_dict.pop("type", None)
        value_type = metadata_from_dict(data_dict.pop("value_type"))
        return cls(value_type=value_type, **data_dict)


NATIVE_CPP_ALIAS: TypeAlias = Primitive | Enum | Vector | Map
NATIVE_CPP_TYPES = (Primitive, Enum, Vector, Map)


class Selection(InputSpec):
    def __init__(
        self,
        name,
        choices: dict[str, One_of],
        description=NOTSET,
        required=False,
        noneable=False,
        defaultable=False,
        validator=None,
    ):
        super().__init__(
            "selection", name, description, required, noneable, defaultable, validator
        )
        self.choices = choices

    @classmethod
    def from_4C_metadata(cls, data_dict):
        data_dict.pop("type", None)
        data_dict.pop("selector", None)
        choices_list = data_dict.pop("choices")
        choices = {}
        for c in choices_list:
            choices[c.pop("name")] = All_Of.from_4C_metadata([c.pop("spec")])
        return cls(choices=choices, **data_dict)


class Group(InputSpec):
    def __init__(
        self,
        name: str,
        spec: One_of,
        description=NOTSET,
        required=False,
        noneable=False,
        defaultable=False,
        validator=None,
    ):
        super().__init__(
            "group", name, description, required, noneable, defaultable, validator
        )
        self.spec = spec

    def __str__(self):
        string = super().__str__()
        string += "\n - With spec:\n    "
        string += indent(str(self.spec), 4)
        return string

    @classmethod
    def from_4C_metadata(cls, data_dict):
        data_dict.pop("type", None)
        spec = All_Of.from_4C_metadata(data_dict.pop("specs", {}))
        return cls(spec=spec, **data_dict)


class List(InputSpec):
    def __init__(
        self,
        spec: One_of,
        name: str,
        size: int | None = None,
        description=NOTSET,
        required=False,
        noneable=False,
        defaultable=False,
        validator=None,
    ):
        super().__init__(
            "list", name, description, required, noneable, defaultable, validator
        )
        self.spec: All_Of = All_Of([spec])
        self.size = size

    def __str__(self):
        string = super().__str__()
        string += "\n - With spec:\n    "
        string += indent(str(self.spec), 4)
        return string

    @classmethod
    def from_4C_metadata(cls, data_dict):
        data_dict.pop("type", None)
        spec = metadata_from_dict(data_dict.pop("spec", {}))
        return cls(spec=spec, **data_dict)


metadata_type_to_class = {
    i.__name__.lower(): i
    for i in [Enum, Vector, Map, Selection, Group, List, All_Of, One_Of]
} | {i: Primitive for i in Primitive.PRIMITIVE_TYPES}


def metadata_from_dict(data_dict):
    entry_type = data_dict.get("type")
    match entry_type:
        case _ if entry_type in metadata_type_to_class:
            return metadata_type_to_class[entry_type].from_4C_metadata(data_dict)
        case _:
            raise TypeError(f"Unknown type {entry_type} for {data_dict}")


from fourcipp import CONFIG

obj = All_Of(
    [metadata_from_dict(section) for section in CONFIG["4C_metadata"]["sections"]]
)
breakpoint()
