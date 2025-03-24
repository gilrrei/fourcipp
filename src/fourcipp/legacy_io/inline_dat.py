from functools import partial

from fourcipp import CONFIG
from fourcipp.reader import load_yaml
from fourcipp.utils.metadata import METADATA_TO_PYTHON

SUPPORTED_METADATA_TYPES = list(METADATA_TO_PYTHON.keys()) + ["vector"]


def get_line_list(line):
    return [l.strip() for l in line.split("#")[0].split() if l.strip()]


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


def casting_factory(fourc_metadata):
    if fourc_metadata["type"] in SUPPORTED_METADATA_TYPES:
        return {fourc_metadata["name"]: _entry_casting_factory(fourc_metadata)}

    # Supported collections
    if fourc_metadata["type"] in ["all_of", "group", "one_of"]:
        specs = {}
        for spec_i in fourc_metadata["specs"]:
            specs.update(casting_factory(spec_i))

        if fourc_metadata["type"] == "group":
            return {fourc_metadata["name"]: specs}
        else:
            return specs
    else:
        raise NotImplementedError(f"Entry type {fourc_metadata['type']} not supported.")


def inline_dat_read(line_list, dat_casting):

    entry = {}
    while line_list:
        key = line_list.pop(0)
        entry[key] = dat_casting[key](line_list)

    return entry


def read_positional_arguments(line_list, positional_dat_casting):
    entry = {}
    for i in sorted(positional_dat_casting.keys(), reverse=True):
        entry[positional_dat_casting[i]["name"]] = positional_dat_casting[i]["casting"](
            line_list[i]
        )
    return entry
