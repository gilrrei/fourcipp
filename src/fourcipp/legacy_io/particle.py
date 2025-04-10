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
"""Particle io.

Once this section is implemented in 4C using InputSpec, this file can be
simplified.
"""

from fourcipp import CONFIG
from fourcipp.legacy_io.inline_dat import (
    casting_factory,
    inline_dat_read,
    to_dat_string,
)

_PARTICLE_CASTING = None
if CONFIG["4C_metadata"] is not None:
    _PARTICLE_CASTING = casting_factory(CONFIG["4C_metadata"]["legacy_particle_specs"])


def read_particle(line, particle_casting=_PARTICLE_CASTING):
    """Read particle.

    Args:
        line (str): Inline dat description of the particle
        particle_casting (dict): Particle casting dict.

    Returns:
        dict: Domain section as dict
    """
    return inline_dat_read(line.split(), particle_casting)


def write_particle(particle):
    """Write domain section.

    Args:
        particle (dict): Particle as dict

    Returns:
        list: Particle line
    """
    line = ""

    for k, v in particle.items():
        if line:
            line += " "

        line += k + " " + to_dat_string(v)

    return line
