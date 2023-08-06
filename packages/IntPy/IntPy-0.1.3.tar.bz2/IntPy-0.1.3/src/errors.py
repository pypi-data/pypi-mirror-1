# errors.py
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


"""Error classes module

All error classes used in the IntPy package are centralized here.

It was developed in CIn/UFPE (Brazil) by Rafael Menezes Barreto
<rmb3@cin.ufpe.br, rafaelbarreto87@gmail.com> as part of the IntPy package and
it's free software.
"""


class InvalidRationalNumberError(ValueError):
    """An input string representing a rational number is malformed

    This occurs when the input of anything expecting a string representing a
    rational number doesn't match the rational number pattern.
    """

    def __init__(self, msg=None):
        if msg is None:
            ValueError.__init__(self,
                "the input string is not a valid rational number")
        else:
            ValueError.__init__(self, msg)


class IntervalError(ValueError):
    """Generic error involving intervals

    This can be raised in a context involving intervals where there's no other
    more specialized error class to describe the problem.
    """
    pass


class EmptyIntervalError(IntervalError):
    """Operation not defined for empty intervals

    This occurs when an empty interval is involved in an operation not defined
    for it. For example, the sum of two empty intervals.
    """

    def __init__(self, msg=None):
        if msg is None:
            IntervalError.__init__(self,
                "operation not defined for empty intervals")
        else:
            IntervalError.__init__(self, msg)


class UndefinedIntervalError(IntervalError):
    """Operation not defined for undefined intervals

    This occurs when an undefined interval is involved in an operation not
    defined for it. For example, to get the diameter of an undefined interval.
    """

    def __init__(self, msg=None):
        if msg is None:
            IntervalError.__init__(self,
                "operation not defined for undefined intervals")
        else:
            IntervalError.__init__(self, msg)
