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
import textwrap

from fourcipp import CONFIG
from fourcipp.fourc_input import sort_by_section_names
from fourcipp.utils.metadata import (
    NATIVE_CPP_TYPES,
    All_Of,
    AllEmementsValidator,
    Enum,
    Group,
    List,
    Map,
    One_Of,
    PatternValidator,
    Primitive,
    RangeValidator,
    Selection,
    Tuple,
    Vector,
)
from fourcipp.utils.not_set import check_if_set


def make_collapsible(content, summary=None, open_content=None):
    documentation = []
    if open_content is None:
        open_content = len(content.split("\n")) < 100

    if open_content:
        documentation.append("<details open>")
    else:
        documentation.append("<details>")

    if summary is not None:
        documentation.append("")
        documentation.extend(["<summary>", summary, "</summary>"])
    documentation.append("")
    documentation.append(content)
    documentation.append("")
    documentation.append("</details>")
    documentation.append("")
    return "\n".join(documentation)


def make_spec_description(
    name,
    spec_type,
    header_properties: dict,
    description: str,
    collapsible_properties: dict = None,
):
    header = ""
    if check_if_set(name):
        header += f"**{name}** "
    header += (
        f"(*{spec_type}*"
        + ", ".join([""] + [f"*{k}*: {v}" for k, v in header_properties.items()])
        + ")\\"
    )

    description = set_missing_description(description) + "\n"

    if collapsible_properties is not None:
        for k, v in collapsible_properties.items():
            description += "\n" + make_collapsible(textwrap.indent(v, ""), k)

    return header, description


def make_section_description(
    name,
    spec_type,
    header_properties: dict,
    description: str,
    collapsible_properties: dict = None,
):
    string = "## " + name
    string += (
        f"\n\n*Type*: {spec_type}"
        + ", ".join([""] + [f"*{k}*: {v}" for k, v in header_properties.items()])
        + ""
    )

    string += "\n\n" + set_missing_description(description) + "\n"

    if name in section_in_tests:
        content = "\n - " + "\n - ".join(
            [f"[{n.split('/')[-1]}]({n})" for n in sorted(section_in_tests[name])]
        )

        n_files = len(section_in_tests[name])

        summary = f"Used in {n_files} test"

        if n_files > 1:
            summary += "s"

        string += make_collapsible(content, summary, open_content=False)
    else:
        string += "\n Not used in any test."

    if name in section_in_tutorials:
        content = "\n - " + "\n - ".join(
            [f"[{n.split('/')[-1]}]({n})" for n in sorted(section_in_tutorials[name])]
        )

        n_files = len(section_in_tutorials[name])

        summary = f"Used in {n_files} tutorial"
        if n_files > 1:
            summary += "s"

        string += make_collapsible(content, summary, open_content=False)

    string += "\n"
    if collapsible_properties is not None:
        for k, v in collapsible_properties.items():
            string += "\n" + make_collapsible(textwrap.indent(v, " "), k)

    string + "\n"
    return string


def none_to_null(obj):
    if obj is None:
        return "null"
    return obj


def type_or_none(type_description, entry):
    if entry.noneable:
        return type_description + " or null"
    return type_description


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


def primitive_to_md(primitive: Primitive, make_description=make_spec_description):
    type_description = type_or_none(primitive.spec_type, primitive)

    header_properties = {"required": primitive.required}
    header_properties.update(validator_to_header_argument(primitive.validator))
    if not primitive.required:
        header_properties["default"] = none_to_null(primitive.default)

    return make_description(
        primitive.name, type_description, header_properties, primitive.description
    )


def vector_or_map_to_md(entry: Vector | Map, make_description=make_spec_description):
    type_description = type_or_none(value_type_flatter(entry), entry)

    header_properties = {"size": flatten_size_vector(entry), "required": entry.required}
    if entry.validator is not None:
        header_properties.update(validator_to_header_argument(entry.validator))

    if not entry.required:
        header_properties["default"] = none_to_null(entry.default)

    collapsible_properties = None
    if not isinstance(entry.value_type, Primitive):
        collapsible_properties = {
            "Value type": all_of_to_md(All_Of([entry.value_type]))
        }

    return make_description(
        entry.name,
        type_description,
        header_properties,
        entry.description,
        collapsible_properties,
    )


def tuple_to_md(tuple_entry: Tuple, make_description=make_spec_description):
    type_description = type_or_none(value_type_flatter(tuple_entry), tuple_entry)

    header_properties = {"required": tuple_entry.required}
    header_properties.update(validator_to_header_argument(tuple_entry.validator))

    if not tuple_entry.required:
        header_properties["default"] = none_to_null(tuple_entry.default)

    collapsible_properties = {
        "Entries": all_of_to_md(All_Of(tuple_entry.value_types), indent=1)
    }

    return make_description(
        tuple_entry.name,
        type_description,
        header_properties,
        tuple_entry.description,
        collapsible_properties,
    )


def enum_to_md(enum: Enum, make_description=make_spec_description):
    type_description = type_or_none(enum.spec_type, enum)

    header_properties = {"required": enum.required}
    header_properties.update(validator_to_header_argument(enum.validator))

    if not enum.required:
        header_properties["default"] = none_to_null(enum.default)

    choices = ""
    for choice, choice_description in zip(enum.choices, enum.choices_description):
        choices += f"\n - **{choice}**"
        if choice_description is not None:
            choices += " : " + choice_description

    collapsible_properties = {"Choices": choices}

    return make_description(
        enum.name,
        type_description,
        header_properties,
        enum.description,
        collapsible_properties,
    )


def group_to_md(group: Group, make_description=make_spec_description):
    type_description = type_or_none(group.spec_type, group)

    collapsible_properties = {}
    if len(group.spec) > 0:
        collapsible_properties = {"Contains": all_of_to_md(group.spec, indent=1)}

    header_properties = validator_to_header_argument(group.validator)
    return make_description(
        group.name,
        type_description,
        header_properties,
        group.description,
        collapsible_properties,
    )


def list_to_md(list_entry: List, make_description=make_spec_description):
    type_description = type_or_none(list_entry.spec_type, list_entry)

    header_properties = {}
    if list_entry.size is not None:
        header_properties = {"size": list_entry.size}
    header_properties.update(validator_to_header_argument(list_entry.validator))

    return make_description(
        list_entry.name,
        type_description,
        header_properties,
        list_entry.description,
        collapsible_properties={
            "Each element contains": all_of_to_md(list_entry.spec, indent=1)
        },
    )


def selection_to_md(selection: Selection, make_description=make_spec_description):
    type_description = type_or_none(selection.spec_type, selection)

    choices = ""
    for choice, choice_spec in selection.choices.items():
        choices += "\n\n" + " " + f"- *{choice}*:\n\n"
        choices += all_of_to_md(choice_spec, indent=3)

    return make_description(
        selection.name,
        type_description,
        validator_to_header_argument(selection.validator),
        selection.description,
        collapsible_properties={"Choices": choices},
    )


def sort_one_of_option_names(one_of: One_Of) -> list:
    options = [[s.name for s in spec] for spec in one_of]

    common_names = set(options[0])
    for l in options:
        common_names = common_names.intersection(set(l))

    if common_names:
        common_names_list = [
            f'<span style="color:grey">{name}</span>' for name in sorted(common_names)
        ]
        for i, l in enumerate(options):
            o = [name for name in l if name not in common_names]
            options[i] = o + common_names_list

    return [", ".join(l) for l in options]


def one_of_to_md(one_of: One_Of):
    header = "*One of*"

    description = ""
    if check_if_set(one_of.description):
        description += "\n" + description + "\n"

    open_content = len(one_of.specs) < 11

    names = sort_one_of_option_names(one_of)
    print(names)
    for i, spec in enumerate(one_of.specs):
        key = "Option (" + names[i] + ")"
        description += "\n" + make_collapsible(
            textwrap.indent(all_of_to_md(spec, 1), " "), key, open_content
        )

    return header, description


def set_missing_description(description):
    if check_if_set(description):
        return "*" + description + "*"
    else:
        return DESCRIPTION_MISSING


def validator_to_header_argument(validator):
    if validator is None:
        return {}
    match validator:
        case RangeValidator():
            range_text = ""
            if validator.minimum_exclusive:
                range_text += "("
            else:
                range_text += "["

            range_text += f"{validator.minimum}, {validator.maximum}"

            if validator.maximum_exclusive:
                range_text += ")"
            else:
                range_text += "]"
            return {"range": range_text}
        case AllEmementsValidator():
            element_validator_name, element_validator_value = tuple(
                *validator_to_header_argument(validator.element_validator).items()
            )
            return {
                "each element must validate": f"{element_validator_name} {element_validator_value}",
            }

        case PatternValidator():
            return {"must match pattern": validator.pattern}
        case _:
            raise ValueError(f"Unknown validator {validator}")


def all_of_to_md(all_of: All_Of, indent=0):
    entries = ""
    for entry in all_of:
        string_entry = None
        description_entry = None
        match entry:
            case Primitive():
                string_entry, description_entry = primitive_to_md(entry)
            case Vector() | Map():
                string_entry, description_entry = vector_or_map_to_md(entry)
            case Tuple():
                string_entry, description_entry = tuple_to_md(entry)
            case Enum():
                string_entry, description_entry = enum_to_md(entry)
            case Group():
                string_entry, description_entry = group_to_md(entry)
            case List():
                string_entry, description_entry = list_to_md(entry)
            case Selection():
                string_entry, description_entry = selection_to_md(entry)
            case One_Of():
                string_entry, description_entry = one_of_to_md(entry)
            case _:
                raise ValueError(type(entry))

        entries += (
            "\n\n"
            + indent * " "
            + "- "
            + string_entry
            + "\n"
            + textwrap.indent(description_entry, prefix=(indent + 2) * " ")
        )
    return entries


def create_section_markdown(section):
    string_entry = ""
    match section:
        case Primitive():
            string_entry = primitive_to_md(section, make_section_description)
        case Vector() | Map():
            string_entry = vector_or_map_to_md(section, make_section_description)
        case Tuple():
            string_entry = tuple_to_md(section, make_section_description)
        case Enum():
            string_entry = enum_to_md(section, make_section_description)
        case Group():
            string_entry = group_to_md(section, make_section_description)
        case List():
            string_entry = list_to_md(section, make_section_description)
        case Selection():
            string_entry = selection_to_md(section, make_section_description)
        case One_Of():
            string_entry = one_of_to_md(section, make_section_description)
        case _:
            raise ValueError(type(section))
    return string_entry + "\n\n"


def has_entity(section):
    def iterate(obj):
        if isinstance(obj, NATIVE_CPP_TYPES):
            yield obj
        else:
            for o in obj:
                yield from iterate(o)

    for o in iterate(section):
        if o.name == "ENTITY_TYPE":
            return True

    return False


from pathlib import Path

from tqdm import tqdm

from fourcipp.utils.yaml_io import load_yaml


def get_sections_in_files(directory):
    sections = {}
    for file in tqdm(Path(directory).glob("*.4C.yaml")):
        sections_names = [k.strip() for k in load_yaml(file).keys()]
        for s in sections_names:
            file_name = str(file).split("tests/")[-1]
            file_name = (
                f"https://github.com/4C-multiphysics/4C/blob/main/tests/{file_name}"
            )
            if s in sections:
                sections[s].append(file_name)
            else:
                sections[s] = [file_name]
    return sections


section_in_tests = get_sections_in_files(
    "/home/ccxi/Desktop/4C/code/4C/tests/input_files/"
)
section_in_tutorials = get_sections_in_files(
    "/home/ccxi/Desktop/4C/code/4C/tests/tutorials/"
)

obj = All_Of.from_4C_metadata(CONFIG.fourc_metadata["sections"])

d = sort_by_section_names({o.name: o for o in obj})

geometry = []
conditions = []
others = []
materials = []
funct = []
for section in d.values():
    if (
        section.name.endswith("DOMAIN")
        or section.name.endswith("ELEMENTS")
        or section.name.endswith("GEOMETRY")
        or section.name.endswith("KNOTVECTORS")
    ):
        geometry.append(section)
    elif section.name == "MATERIALS":
        materials.append(section)
    elif section.name == "FUNCT<n>":
        funct.append(section)
    elif has_entity(section):
        conditions.append(section)
    else:
        others.append(section)


def create_category_file(section_list, name):
    documentation = []

    documentation.append(f"# {name}")
    documentation.append("")
    documentation.append("")
    for section in section_list:
        documentation.append(create_section_markdown(section))
    pathlib.Path(name.lower().replace(" ", "_") + ".md").write_text(
        "\n".join(documentation)
    )


obj = All_Of(specs=d.values())

DESCRIPTION_MISSING = '<span style="color:grey">*no description yet*</span>'
documentation = []


create_category_file(others, "Parameter sections")
create_category_file(funct, "Functions")
create_category_file(materials, "Materials")
create_category_file(conditions, name="Conditions sections")
create_category_file(geometry, "Geometry sections")

names = set([s.name for s in obj])
print(
    "unknown sections",
    set(section_in_tests.keys()) - names - set(CONFIG.sections.legacy_sections),
)
untested_sections = [
    s
    for s in sorted(
        (names - set(section_in_tests.keys())) - set(CONFIG.sections.legacy_sections)
    )
    if not (
        s.endswith("GEOMETRY")
        or s.endswith("DOMAIN")
        or s.endswith("KNOTVECTORS")
        or s == "FUNCT<n>"
    )
]
print("unknown sections", len(untested_sections), "\n", "\n -".join(untested_sections))

all_files = set(
    (
        l.name
        for l in Path("/home/ccxi/Desktop/4C/code/4C/tests/input_files/").glob(
            "*.4C.yaml"
        )
    )
)

rs_files = set((l.split("/")[-1] for l in section_in_tests["RESULT DESCRIPTION"]))

print("\n".join(sorted(all_files - rs_files)))
