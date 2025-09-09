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
import pathlib

from fourcipp import CONFIG
from fourcipp.utils.metadata import (
    All_Of,
    Primitive,
    Vector,
    Map,
    Group,
    List,
    Enum,
    Selection,
    One_Of,
    Tuple,
    NATIVE_CPP_TYPES,
)
from fourcipp.utils.not_set import check_if_set
from fourcipp.fourc_input import sort_by_section_names


def make_collapsible(content, summary=None):
    documentation = ["<details>"]
    if summary is not None:
        documentation.append("")
        documentation.extend(["<summary>", summary, "</summary>"])
    documentation.append("")
    documentation.append(content)
    documentation.append("")
    documentation.append("</details>")
    documentation.append("")
    return "\n".join(documentation)


import textwrap


def none_to_null(obj):
    if obj is None:
        return "null"
    return obj


def primitive_to_md(primitive: Primitive):
    string = ""
    if check_if_set(primitive.name):
        string += f"**{primitive.name}** "
    string += f"(*{primitive.spec_type}*"

    if primitive.noneable:
        string += f" or null"
    if not primitive.required:
        string += f", *default*: {none_to_null(primitive.default)}"

    string += f")"

    return string, set_missing_description(primitive.description)


def value_type_flatter(entry):
    def is_primitive(obj):
        if isinstance(obj, Primitive):
            return obj.spec_type

        return value_type_flatter(obj)

    if isinstance(entry, Vector):
        return "vector\\<" + is_primitive(entry.value_type) + ">"
    elif isinstance(entry, Map):
        return "map\\<str," + is_primitive(entry.value_type) + ">"
    elif isinstance(entry, Tuple):
        return (
            "tuple\\<" + ", ".join([is_primitive(v) for v in entry.value_types]) + ">"
        )
    else:
        raise ValueError(f"{entry.spec_type}, {entry}")


def flatten_size_vector(vector):

    text = str(vector.size)
    if vector.size is None:
        text = "n"

    if isinstance(vector.value_type, Primitive):
        return text

    elif isinstance(vector.value_type, Vector):
        return text + " x " + flatten_size_vector(vector.value_type)
    elif isinstance(vector.value_type, Tuple):
        return text
    else:
        raise ValueError(f"{vector}")

    return text


def vector_to_md(vector: Vector):

    string = ""
    if check_if_set(vector.name):
        string += f"**{vector.name}** "
    string += f"({value_type_flatter(vector)}"

    string += f", *size*: {flatten_size_vector(vector)}"
    if vector.noneable:
        string += f" or null"
    if not vector.required:
        string += f", *default*: {none_to_null(vector.default)}"

    string += f")"

    return string, set_missing_description(vector.description)


def map_to_md(map_entry: Map):

    string = ""
    if check_if_set(map_entry.name):
        string += f"**{map_entry.name}** "
    string += f"({value_type_flatter(map_entry)}"

    string += f", *size*: {flatten_size_vector(map_entry)}"
    if map_entry.noneable:
        string += f" or null"
    if not map_entry.required:
        string += f", *default*: {none_to_null(map_entry.default)}"

    string += f")"

    return string, set_missing_description(map_entry.description)


def tuple_to_md(tuple_entry: Tuple):

    string = ""
    if check_if_set(tuple_entry.name):
        string += f"**{tuple_entry.name}** "

    if tuple_entry.noneable:
        string += f" or null"
    if not tuple_entry.required:
        string += f", *default*: {none_to_null(tuple_entry.default)}"

    string += f")"

    description = set_missing_description(tuple_entry.description)
    description += "\n\n*Entries*:"
    description += all_of_to_md(All_Of(tuple_entry.value_types, indent=1))

    return string, description


def enum_to_md(enum: Enum):
    string = ""
    if check_if_set(enum.name):
        string += f"**{enum.name}** "
    string += f"(*{enum.spec_type}*"

    if enum.noneable:
        string += f" or null"
    if enum.required:
        string += f", *required*"
    else:
        string += f", *optional*"

    if not enum.required:
        string += f", *default*: {none_to_null(enum.default)}"

    string += f")"

    description = set_missing_description(enum.description)
    choices = ""
    for choice, choice_description in zip(enum.choices, enum.choices_description):
        choices += f"\n - **{choice}**"
        if choice_description is not None:
            choices += " : " + choice_description

    if len(enum.choices) < 11:
        description += "\n\nChoices:" + choices
    else:
        description += "\n\n" + make_collapsible(choices, "Choices:")
    return string, description


def group_to_md(group: Group, indent=0):
    string = ""
    if check_if_set(group.name):
        string += f"**{group.name}** "
    string += f"(*{group.spec_type}*"

    if group.noneable:
        string += f" or null"

    string += f")"

    description = set_missing_description(group.description) + "\n\n*Contains*:"
    description += all_of_to_md(group.spec, indent=indent + 1)
    return string, description


def list_to_md(list_entry: List, indent=0):
    string = ""
    if check_if_set(list_entry.name):
        string += f"**{list_entry.name}** "
    string += f"(*{list_entry.spec_type}*"

    if list_entry.noneable:
        string += f" or null"

    if list_entry.size is not None:
        string += f"*size*: {list_entry.size}"

    string += f")"

    description = (
        set_missing_description(list_entry.description) + "\n\n*Each element contains*:"
    )
    description += all_of_to_md(list_entry.spec, indent=indent + 1)
    return string, description


def selection_to_md(selection: Selection, indent=0):
    string = ""
    if check_if_set(selection.name):
        string += f"**{selection.name}** "
    string += f"(*{selection.spec_type}*"

    if selection.noneable:
        string += f" or null"

    string += f")"

    description = set_missing_description(selection.description) + "\n\n*Choices*:"
    for choice, choice_spec in selection.choices.items():
        description += "\n\n" + indent * " " + f"- **{choice}**:\n\n"
        description += all_of_to_md(choice_spec, indent=indent + 2)
    return string, description


def one_of_to_md(one_of: One_Of, indent=0):
    string = "*One of*"

    description = ""
    if check_if_set(one_of.description):
        description += one_of.description

    options = ""
    for spec in one_of.specs:
        options += "\n\n" + indent * " " + f"- *Option*:\n\n"
        options += all_of_to_md(spec, indent=indent + 2)

    if len(one_of) > 5:
        description += indent * " " + make_collapsible(options, "Options")
    else:
        description += indent * " " + "Options" + options

    return string, description


def set_missing_description(description):
    if check_if_set(description):
        return description
    else:
        return DESCRIPTION_MISSING


def all_of_to_md(all_of: All_Of, indent=0):
    entries = ""
    for entry in all_of:
        match entry:
            case Primitive():
                string_entry, description_entry = primitive_to_md(entry)
                entries += (
                    "\n\n"
                    + indent * " "
                    + "- "
                    + string_entry
                    + "\n"
                    + textwrap.indent(
                        description_entry.strip(), prefix=(indent + 2) * " "
                    )
                )
            case Vector():
                string_entry, description_entry = vector_to_md(entry)
                entries += (
                    "\n\n"
                    + indent * " "
                    + "- "
                    + string_entry
                    + "\n"
                    + textwrap.indent(
                        description_entry.strip(), prefix=(indent + 2) * " "
                    )
                )
            case Map():
                string_entry, description_entry = map_to_md(entry)
                entries += (
                    "\n\n"
                    + indent * " "
                    + "- "
                    + string_entry
                    + "\n"
                    + textwrap.indent(
                        description_entry.strip(), prefix=(indent + 2) * " "
                    )
                )
            case Enum():
                string_entry, description_entry = enum_to_md(entry)
                entries += (
                    "\n\n"
                    + indent * " "
                    + "- "
                    + string_entry
                    + "\n"
                    + textwrap.indent(
                        description_entry.strip(), prefix=(indent + 2) * " "
                    )
                )
            case Group():
                string_entry, description_entry = group_to_md(entry)
                entries += (
                    "\n\n"
                    + indent * " "
                    + "- "
                    + string_entry
                    + "\n"
                    + textwrap.indent(
                        description_entry.strip(), prefix=(indent + 2) * " "
                    )
                )
            case List():
                string_entry, description_entry = list_to_md(entry)
                entries += (
                    "\n\n"
                    + indent * " "
                    + "- "
                    + string_entry
                    + "\n"
                    + textwrap.indent(
                        description_entry.strip(), prefix=(indent + 2) * " "
                    )
                )
            case Selection():
                string_entry, description_entry = selection_to_md(entry)
                entries += (
                    "\n\n"
                    + indent * " "
                    + "- "
                    + string_entry
                    + "\n"
                    + textwrap.indent(
                        description_entry.strip(), prefix=(indent + 2) * " "
                    )
                )
            case One_Of():
                string_entry, description_entry = one_of_to_md(entry)
                entries += (
                    "\n\n"
                    + indent * " "
                    + "- "
                    + string_entry
                    + "\n"
                    + textwrap.indent(
                        description_entry.strip(), prefix=(indent + 2) * " "
                    )
                )

            case _:
                print(type(entry))

    if len(all_of) > 10:
        return textwrap.indent(
            make_collapsible(content=entries, summary="Click to extend"), indent * " "
        )
    return entries


def create_section_markdown(section):
    documentation = ["# " + section.name + " (" + type(section).__name__ + ")"]
    if check_if_set(section.description):
        documentation.append("\n" + section.description)
    else:
        documentation.append("\n" + DESCRIPTION_MISSING)

    if isinstance(section, NATIVE_CPP_TYPES):
        documentation.extend(all_of_to_md(All_Of([section])).split("\n"))
    else:
        documentation.extend(all_of_to_md(section.spec).split("\n"))
    documentation.append("")
    documentation.append("")
    return documentation


obj = All_Of.from_4C_metadata(CONFIG.fourc_metadata["sections"])

d = sort_by_section_names({o.name: o for o in obj})

obj = All_Of(specs=d.values())

DESCRIPTION_MISSING = "No description yet."
documentation = []
for section in obj:
    documentation.extend(create_section_markdown(section))
pathlib.Path("documentation.md").write_text("\n".join(documentation))
