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
"""Configuration utils."""

import pathlib

from loguru import logger

from fourcipp.utils.yaml_io import load_yaml

CONFIG_FILE = pathlib.Path(__file__).parents[1] / "config.yaml"


def set_profile(profile="default"):
    """Set config profile.

    Args:
        profile (str, optional): Default is used if nothing is provided.

    Returns:
        dict: user config.
    """
    logger.debug(f"Reading config profile {profile}")

    CONFIG = load_yaml(CONFIG_FILE)

    if profile == "default" and CONFIG["profiles"][profile] is None:
        profile = "testing"
        logger.debug("Setting testing config as a default config was not provided.")

    metadata = CONFIG["profiles"][profile]["4C_metadata_path"]
    if metadata is not None:
        metadata = load_yaml(pathlib.Path(metadata))

    CONFIG["4C_metadata"] = metadata

    schema = CONFIG["profiles"][profile]["json_schema_path"]
    if schema is not None:
        schema = load_yaml(pathlib.Path(schema))

    CONFIG["json_schema"] = schema

    return CONFIG
