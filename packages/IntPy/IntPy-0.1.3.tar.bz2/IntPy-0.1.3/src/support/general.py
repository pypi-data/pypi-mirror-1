# support/general.py
#
# Copyright 2008 Rafael Menezes Barreto <rmb3@cin.ufpe.br,
# rafaelbarreto87@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License version 2
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.


"""General support module

All punctual pieces of support software used in the IntPy package are
agglomerated here.

It was developed in CIn/UFPE (Brazil) by Rafael Menezes Barreto
<rmb3@cin.ufpe.br, rafaelbarreto87@gmail.com> as part of the IntPy package and
it's free software.
"""


import re

from intpy.errors import InvalidRationalNumberError


__all__ = [
    "isnan",
    "rational2fraction"
]

# prefered instead of isNaN from fpconst because of performance
isnan = lambda number: number != number

_rational_number_pattern = re.compile(r"""
    ^
    (?P<frac_sign>[-+])?
    (?P<frac_before_point>\d+)
    (?:[\.,]
        (?P<frac_after_point>\d*)
    )?
    (?:[eE]
        (?P<exponent_sign>[-+])?
        (?P<exponent>\d+)
    )?
    (?:/
        (?P<denominator>.+)
    )?
    $
    """, re.VERBOSE
)


def _mdc(a, b):
    while a % b != 0:
        a, b = b, a % b
    return b

def rational2fraction(rational):
    """Transforms a string representing a rational number in a fraction

    It takes a string representing a rational number and returns the respective
    fraction as a 2-tuple where the first element is the numerator and the
    second is the denominator. Below follow some examples of use:

    >>> rational2fraction("0.1")
    (1, 10)
    >>> rational2fraction("+3e-1")
    (3, 10)
    >>> rational2fraction("5/25")
    (1, 5)
    >>> rational2fraction("0,2e1/1.E-8")
    (200000000, 1)
    >>> rational2fraction("1/2/4")
    (2, 1)
    >>> rational2fraction("1/0") # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ZeroDivisionError: there's some 0 in the denominators
    >>> rational2fraction("1/") # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    InvalidRationalNumberError:...
    """
    if rational is None:
        return (1, 1)
    rational_match = _rational_number_pattern.match(rational)
    if rational_match is None:
        raise InvalidRationalNumberError()
    rational_parts = rational_match.groupdict()
    frac_sign = 1 if rational_parts["frac_sign"] == "-" else 0
    frac_before_point = rational_parts["frac_before_point"]
    frac_after_point = "" if rational_parts["frac_after_point"] is None else \
        rational_parts["frac_after_point"]
    exponent_sign = 1 if rational_parts["exponent_sign"] == "-" else 0
    exponent = "0" if rational_parts["exponent"] is None else \
        rational_parts["exponent"]
    denominator = rational2fraction(rational_parts["denominator"])
    if denominator[0] == 0:
        raise ZeroDivisionError("there's some 0 in the denominators")
    new_frac = (-1) ** frac_sign * int(frac_before_point+frac_after_point)
    new_exponent = (-1) ** exponent_sign * int(exponent) - \
        len(frac_after_point)
    if new_exponent < 0:
        ret = (new_frac * denominator[1],
            10 ** (-new_exponent) * denominator[0])
    else:
        ret = (new_frac * 10 ** new_exponent * denominator[1], denominator[0])
    mdc_numerator_denominator = _mdc(ret[0], ret[1])
    return (ret[0] / mdc_numerator_denominator,
        ret[1] / mdc_numerator_denominator)
