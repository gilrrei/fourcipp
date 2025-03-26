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
"""Test domain io."""

import pytest

from fourcipp.legacy_io.domain import read_domain, write_domain


@pytest.fixture(name="reference_domain_lines")
def fixture_reference_domain_lines():
    """Reference lines."""
    return [
        "LOWER_BOUND 0.1 0.1  0.1",
        "UPPER_BOUND 0.1 0.1  0.1",
        "INTERVALS 10 12 13",
        "ROTATION 0.1 0.2 0.3",
        "PARTITION auto",
        "ELEMENTS some  string ",
    ]


def test_domains_read_and_write(reference_domain_lines):
    """Test read and write domain."""
    lines = write_domain(read_domain(reference_domain_lines))
    for k in range(len(reference_domain_lines)):
        assert reference_domain_lines[k].split() == lines[k].split()
