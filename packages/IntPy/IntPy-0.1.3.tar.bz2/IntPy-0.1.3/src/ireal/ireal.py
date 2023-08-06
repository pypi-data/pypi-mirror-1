# ireal/ireal.py
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


"""IReal class module

This module contains an implementation of the Real Interval type with Maximum
Accuracy which is a part of the Interval Arithmetic. Please, refer the package
docstring for more information about Interval Arithmetic.

It was developed in CIn/UFPE (Brazil) by Rafael Menezes Barreto
<rmb3@cin.ufpe.br, rafaelbarreto87@gmail.com> as part of the IntPy package and
it's free software.
"""


from fpconst import NaN
from intpy.errors import EmptyIntervalError
from intpy.errors import UndefinedIntervalError
from intpy.support import isnan
from intpy.support import rational2fraction
from intpy.support import rounding


__all__ = [
    "IReal"
]


def _parse_limits(inf, sup):
    """Adjusts the entered limits applying directed rounding if possible

    Some examples of how it works are below:

    >>> rounding_mode_backup = rounding.get_mode()
    >>> x = _parse_limits(0.1, 0.1); x[0] == x[1]
    True
    >>> x = _parse_limits("0.1", "0.1"); x[0] < x[1] and str(x[0]) == str(x[1])
    True
    >>> x = _parse_limits("0.25", 0.25); x[0] == x[1]
    True
    >>> x = _parse_limits("0.1", "0.3")
    >>> x[0] < 0.1 and x[1] > 0.3 and str(x[0]) == "0.1" and str(x[1]) == "0.3"
    True
    >>> _parse_limits(1, "1e1000") # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    OverflowError: 'inf' or 'sup' fraction parts are too large...
    >>> _parse_limits("1e1000", 1) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    OverflowError: 'inf' or 'sup' fraction parts are too large...
    >>> rounding_mode_backup == rounding.get_mode()
    True
    """
    new_inf, new_sup = inf, sup
    try:
        rounding_mode_backup = rounding.get_mode()
        if type(inf) == type(str()):
            number_fraction = rational2fraction(inf)
            rounding.set_mode(0)
            fp_numerator = float(number_fraction[0])
            fp_denominator = float(number_fraction[1])
            rounding.set_mode(-1)
            new_inf = fp_numerator / fp_denominator
        if type(sup) == type(str()):
            if inf != sup:
                number_fraction = rational2fraction(sup)
                rounding.set_mode(0)
                fp_numerator = float(number_fraction[0])
                fp_denominator = float(number_fraction[1])
            rounding.set_mode(1)
            new_sup = fp_numerator / fp_denominator
    except OverflowError:
        raise OverflowError("'inf' or 'sup' fraction parts are too large to"
            " convert them to float")
    finally:
        rounding.set_mode(rounding_mode_backup)
    return (float(new_inf), float(new_sup))


class IReal(object):
    """An implementation of the Real Interval type with Maximum Accuracy

    Please, see the following references for more information about Real
    Intervals and Maximum Accuracy:

    [1] Moore, R. E., Interval Analysis. Prentice-Hall, Englewood Cliffs, New
        Jersey, 1966.
    [2] Moore, R. E., Methods and Applications of Interval Analysis. SIAM
        Studies in Applied Mathematics, Philadelphia, 1979.
    [3] Kulisch, U. W., Miranker, W. L., Computer Arithmetic in Theory and
        Practice. Academic Press, 1981.
    """

    def __init__(self, inf=None, sup=None):
        """Constructor of the IReal class

        For more information about the IReal class, see the class docstring.
        Some examples of how to use this constructor follow below:

        >>> IReal()
        empty interval
        >>> IReal("undefined"); IReal(NaN)
        undefined interval
        undefined interval
        >>> IReal("25/10", "1E1")
        [2.5, 10.0]
        >>> IReal(0.5, "0.25")
        [0.25, 0.5]
        >>> IReal(2)
        [2.0, 2.0]
        """
        self._inf = self._sup = NaN
        self._empty = False
        self._set_limits(inf, sup)

    def _set_limits(self, inf=None, sup=None):
        """Sets the interval limits

        The behavior of this method is expressed in the examples below:

        >>> x = IReal(); x.empty; x.undefined
        True
        False
        >>> x = IReal("undefined"); x.empty; x.undefined
        False
        True
        >>> x = IReal("0,25"); x.empty; x.undefined; print x
        False
        False
        [0.25, 0.25]
        >>> x = IReal(0.5, "0.25"); x.empty; x.undefined; print x
        False
        False
        [0.25, 0.5]
        >>> x = IReal(0.25, NaN); x.empty; x.undefined
        False
        True
        """
        if inf is None:
            self._empty = True
        elif inf != "undefined":
            if sup is None:
                sup = inf
            limits = _parse_limits(inf, sup)
            if not (isnan(limits[0]) or isnan(limits[1])):
                self._inf, self._sup = min(limits), max(limits)

    inf = property(fget=lambda self: self._inf)
    sup = property(fget=lambda self: self._sup)
    empty = property(fget=lambda self: self._empty)
    undefined = property(fget=lambda self: not self._empty and \
        (isnan(self._inf) or isnan(self._sup)))

    def __pos__(self):
        """Unary plus operator

        Some examples:

        >>> +IReal("25/100", 0.5)
        [0.25, 0.5]
        >>> +IReal("undefined")
        undefined interval
        >>> +IReal() # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        EmptyIntervalError:...
        """
        if self.empty:
            raise EmptyIntervalError()
        return self

    def __neg__(self):
        """Unary minus operator

        Some examples:

        >>> -IReal("-25/100", 0.5)
        [-0.5, 0.25]
        >>> -IReal("undefined")
        undefined interval
        >>> -IReal() # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        EmptyIntervalError:...
        """
        if self.empty:
            raise EmptyIntervalError()
        return IReal(-self.sup, -self.inf)

    def __invert__(self):
        """Inversion operator

        Some examples:

        >>> rounding_mode_backup = rounding.get_mode()
        >>> ~IReal(0.25, 0.5)
        [2.0, 4.0]
        >>> x = ~IReal(0.1); x.inf < x.sup and str(x.inf) == str(x.sup)
        True
        >>> ~IReal("undefined")
        undefined interval
        >>> ~IReal(-2, 2)
        undefined interval
        >>> ~IReal() # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        EmptyIntervalError:...
        >>> rounding_mode_backup == rounding.get_mode()
        True
        """
        if self.empty:
            raise EmptyIntervalError()
        if 0.0 in self:
            return IReal("undefined")
        rounding_mode_backup = rounding.get_mode()
        rounding.set_mode(-1)
        inf = 1.0 / self.sup
        rounding.set_mode(1)
        sup = 1.0 / self.inf
        rounding.set_mode(rounding_mode_backup)
        return IReal(inf, sup)

    def __add__(self, other):
        """Binary plus operator

        Some examples:

        >>> rounding_mode_backup = rounding.get_mode()
        >>> IReal(0.25, 0.5) + IReal(2)
        [2.25, 2.5]
        >>> IReal(-0.75, 0.75) + 2
        [1.25, 2.75]
        >>> x = IReal("0.1") + "0.1"
        >>> x.inf < x.sup and str(x.inf) == str(x.sup)
        True
        >>> IReal("undefined") + 2
        undefined interval
        >>> IReal(2) + IReal() # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        EmptyIntervalError:...
        >>> rounding_mode_backup == rounding.get_mode()
        True
        """
        if type(other) != type(self):
            other = IReal(other)
        if self.empty or other.empty:
            raise EmptyIntervalError()
        rounding_mode_backup = rounding.get_mode()
        rounding.set_mode(-1)
        inf = self.inf + other.inf
        rounding.set_mode(1)
        sup = self.sup + other.sup
        rounding.set_mode(rounding_mode_backup)
        return IReal(inf, sup)

    def __sub__(self, other):
        """Binary minus operator

        Some examples:

        >>> rounding_mode_backup = rounding.get_mode()
        >>> IReal(0.25, 0.5) - IReal(2)
        [-1.75, -1.5]
        >>> IReal(-0.75, 0.75) - 2
        [-2.75, -1.25]
        >>> x = IReal("0.1") - "0.1"
        >>> x.inf < x.sup and str(-x.inf) == str(x.sup)
        True
        >>> IReal("undefined") + 2
        undefined interval
        >>> IReal(2) + IReal() # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        EmptyIntervalError:...
        >>> rounding_mode_backup == rounding.get_mode()
        True
        """
        if type(other) != type(self):
            other = IReal(other)
        if self.empty or other.empty:
            raise EmptyIntervalError()
        rounding_mode_backup = rounding.get_mode()
        rounding.set_mode(-1)
        inf = self.inf - other.sup
        rounding.set_mode(1)
        sup = self.sup - other.inf
        rounding.set_mode(rounding_mode_backup)
        return IReal(inf, sup)

    def __mul__(self, other):
        """Multiplication operator

        Some examples:

        >>> rounding_mode_backup = rounding.get_mode()
        >>> IReal(0.25, 0.5) * IReal(2, 3)
        [0.5, 1.5]
        >>> IReal(-0.75, 0.75) * 2
        [-1.5, 1.5]
        >>> x = IReal("0.1") * "0.1"
        >>> x.inf < x.sup and str(x.inf) == str(x.sup)
        True
        >>> IReal("undefined") * 2
        undefined interval
        >>> IReal(2) * IReal() # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        EmptyIntervalError:...
        >>> rounding_mode_backup == rounding.get_mode()
        True
        """
        if type(other) != type(self):
            other = IReal(other)
        if self.empty or other.empty:
            raise EmptyIntervalError()
        x1, y1, x2, y2 = self.inf, self.sup, other.inf, other.sup
        rounding_mode_backup = rounding.get_mode()
        rounding.set_mode(-1)
        inf = min(x1*x2, x1*y2, y1*x2, y1*y2)
        rounding.set_mode(1)
        sup = max(x1*x2, x1*y2, y1*x2, y1*y2)
        rounding.set_mode(rounding_mode_backup)
        return IReal(inf, sup)

    def __div__(self, other):
        """Division operator

        Some examples:

        >>> rounding_mode_backup = rounding.get_mode()
        >>> IReal(0.25, 0.5) / IReal(2, 4)
        [0.0625, 0.25]
        >>> IReal(-0.75, 0.75) / 2
        [-0.375, 0.375]
        >>> x = IReal("0.1") / "0.1"
        >>> x.inf < x.sup and str(x.inf) == str(x.sup)
        True
        >>> IReal(1) / IReal(-2, 2)
        undefined interval
        >>> IReal("undefined") / 2
        undefined interval
        >>> IReal(2) / IReal() # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        EmptyIntervalError:...
        >>> rounding_mode_backup == rounding.get_mode()
        True
        """
        if type(other) != type(self):
            other = IReal(other)
        if self.empty or other.empty:
            raise EmptyIntervalError()
        if 0.0 in other:
            return IReal("undefined")
        x1, y1, x2, y2 = self.inf, self.sup, other.inf, other.sup
        rounding_mode_backup = rounding.get_mode()
        rounding.set_mode(-1)
        inf = min(x1/x2, x1/y2, y1/x2, y1/y2)
        rounding.set_mode(1)
        sup = max(x1/x2, x1/y2, y1/x2, y1/y2)
        rounding.set_mode(rounding_mode_backup)
        return IReal(inf, sup)

    def __and__(self, other):
        """Intersection operator

        Some examples:

        >>> IReal(2, 3) & IReal(2.5)
        [2.5, 2.5]
        >>> IReal(2) & IReal("undefined")
        undefined interval
        >>> IReal() & IReal("undefined")
        undefined interval
        >>> IReal() & IReal(-2, 2)
        empty interval
        >>> IReal(-1, 0) & IReal(0.25, 10)
        empty interval
        >>> IReal(-1, 1) & IReal(0.25, 2)
        [0.25, 1.0]
        """
        if self.undefined or other.undefined:
            return IReal("undefined")
        if self.empty or other.empty:
            return IReal()
        sup_min, inf_max = min(self.sup, other.sup), max(self.inf, other.inf)
        if inf_max <= sup_min:
            return IReal(inf_max, sup_min)
        return IReal()

    def __or__(self, other):
        """Union operator

        Some examples:

        >>> IReal(2, 3) | IReal(2.5)
        [2.0, 3.0]
        >>> IReal(2) | IReal("undefined")
        undefined interval
        >>> IReal() | IReal("undefined")
        undefined interval
        >>> IReal() | IReal(-2, 2)
        [-2.0, 2.0]
        >>> IReal(-1) | IReal()
        [-1.0, -1.0]
        >>> IReal() | IReal()
        empty interval
        >>> IReal(-1, 0) | IReal(0.25, 10)
        undefined interval
        >>> IReal(-1, 0.25) | IReal(0.25, 2)
        [-1.0, 2.0]
        """
        if self.undefined or other.undefined:
            return IReal("undefined")
        if self.empty:
            return other
        if other.empty:
            return self
        sup_min, inf_max = min(self.sup, other.sup), max(self.inf, other.inf)
        if inf_max > sup_min:
            return IReal("undefined")
        return IReal(min(self.inf, other.inf), max(self.sup, other.sup))

    def __eq__(self, other):
        """Equality operator

        Some examples:

        >>> IReal(2, 3) == IReal(2.5)
        False
        >>> IReal("undefined") == IReal("undefined")
        False
        >>> IReal() == IReal()
        True
        >>> IReal(-1, 1) == IReal(-1, 1)
        True
        """
        return (self.empty and other.empty) or \
            (self.inf == other.inf and self.sup == other.sup)

    __ne__ = lambda self, other: not self == other

    def __lt__(self, other):
        """Less Than relation order operator

        Some examples:

        >>> IReal(2, 3) < IReal(2.5)
        False
        >>> IReal(2, 3) < IReal(3.1)
        True
        >>> IReal("undefined") < IReal(3.1) # doctest: +ELLIPSIS
        False
        >>> IReal(3) < IReal() # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        EmptyIntervalError:...
        """
        if self.empty or other.empty:
            raise EmptyIntervalError()
        if self.undefined or other.undefined:
            return False
        return self.sup < other.inf

    def __le__(self, other):
        """Less Than Or Equal relation order operator

        Some examples:

        >>> IReal(2, 3) <= IReal(2.5)
        False
        >>> IReal(2, 3) <= IReal(3.1)
        True
        >>> IReal(3) <= IReal(3)
        True
        >>> IReal("undefined") <= IReal(3.1) # doctest: +ELLIPSIS
        False
        >>> IReal(3) <= IReal() # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        EmptyIntervalError: this order relation can't be applied...
        >>> IReal() <= IReal()
        True
        """
        if self.empty and other.empty:
            return True
        if self.empty or other.empty:
            raise EmptyIntervalError("this order relation can't be applied "
                "to an empty and a non-empty interval")
        if self.undefined or other.undefined:
            return False
        return self.inf <= other.inf and self.sup <= other.sup

    __gt__ = lambda self, other: other.__lt__(self)

    __ge__ = lambda self, other: other.__le__(self)

    def __contains__(self, other):
        """Tests if "other" is an element or a subset of the interval

        Some examples:

        >>> 0.0 in IReal()
        False
        >>> 0.0 in IReal(-1, -0.1)
        False
        >>> 0.0 in IReal(-1, 1)
        True
        >>> 0.0 in IReal(0.1, 1)
        False
        >>> IReal() in IReal()
        True
        >>> IReal("undefined") in IReal()
        False
        >>> IReal("undefined") in IReal("undefined")
        False
        >>> IReal(1) in IReal("undefined")
        False
        >>> IReal() in IReal(-1)
        True
        """
        if type(other) != type(self):
            other = IReal(other)
        if self.undefined or other.undefined:
            return False
        if self.empty and not other.empty:
            return False
        if other.empty:
            return True
        return self.inf <= other.inf and self.sup >= other.sup

    def __abs__(self):
        """Calculates the absolute value of the interval

        Some examples:

        >>> abs(IReal(-1, 1))
        1.0
        >>> abs(IReal(0.25, 1))
        1.0
        >>> abs(IReal()) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        EmptyIntervalError:...
        >>> abs(IReal("undefined")) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        UndefinedIntervalError:...
        """
        if self.empty:
            raise EmptyIntervalError()
        if self.undefined:
            raise UndefinedIntervalError()
        return max(abs(self.inf), abs(self.sup))

    def __repr__(self):
        """Gives a representation of the interval

        Some examples:

        >>> IReal(-1, 1)
        [-1.0, 1.0]
        >>> IReal()
        empty interval
        >>> IReal("undefined")
        undefined interval
        >>> IReal(0.25, NaN)
        undefined interval
        """
        if self.empty:
            return "empty interval"
        if self.undefined:
            return "undefined interval"
        return "[%r, %r]" % (self.inf, self.sup)

    def diameter(self):
        """Returns the distance between supremum and infimum of the interval

        Some examples:

        >>> rounding_mode_backup = rounding.get_mode()
        >>> IReal(-10, 1).diameter()
        11.0
        >>> IReal().diameter() # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        EmptyIntervalError:...
        >>> IReal("undefined").diameter() # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        UndefinedIntervalError:...
        >>> rounding_mode_backup == rounding.get_mode()
        True
        """
        if self.empty:
            raise EmptyIntervalError()
        if self.undefined:
            raise UndefinedIntervalError()
        rounding_mode_backup = rounding.get_mode()
        rounding.set_mode(1)
        ret = self.sup - self.inf
        rounding.set_mode(rounding_mode_backup)
        return ret

    def middle(self):
        """Returns the middle point of the interval

        Some examples:

        >>> rounding_mode_backup = rounding.get_mode()
        >>> IReal(-10, 5).middle()
        -2.5
        >>> IReal().middle() # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        EmptyIntervalError:...
        >>> IReal("undefined").middle() # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        UndefinedIntervalError:...
        >>> rounding_mode_backup == rounding.get_mode()
        True
        """
        if self.empty:
            raise EmptyIntervalError()
        if self.undefined:
            raise UndefinedIntervalError()
        rounding_mode_backup = rounding.get_mode()
        rounding.set_mode(1)
        ret = (self.inf + self.sup) / 2.0
        rounding.set_mode(rounding_mode_backup)
        return ret

    def distance(self, other):
        """Returns the Hausdorff distance of the interval

        Some examples:

        >>> rounding_mode_backup = rounding.get_mode()
        >>> IReal(-10, 5).distance(IReal(10))
        20.0
        >>> IReal(-10, 5).distance(IReal(10, 50))
        45.0
        >>> x = IReal(-10, 5); x.distance(x)
        0.0
        >>> IReal(-1).distance(IReal()) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        EmptyIntervalError:...
        >>> IReal().distance(IReal(-1)) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        EmptyIntervalError:...
        >>> IReal("undefined").distance(IReal(12)) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        UndefinedIntervalError:...
        >>> IReal(10).distance(IReal("undefined")) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        UndefinedIntervalError:...
        >>> rounding_mode_backup == rounding.get_mode()
        True
        """
        if self.empty or other.empty:
            raise EmptyIntervalError()
        if self.undefined or other.undefined:
            raise UndefinedIntervalError()
        rounding_mode_backup = rounding.get_mode()
        rounding.set_mode(1)
        ret = max(abs(self.inf-other.inf), abs(self.sup-other.sup))
        rounding.set_mode(rounding_mode_backup)
        return ret

    def hull(self, other):
        """Convex union operation

        Some examples:

        >>> IReal(2, 3).hull(IReal(2.5))
        [2.0, 3.0]
        >>> IReal(2).hull(IReal("undefined"))
        undefined interval
        >>> IReal().hull(IReal("undefined"))
        undefined interval
        >>> IReal().hull(IReal(-2, 2))
        [-2.0, 2.0]
        >>> IReal(-1).hull(IReal())
        [-1.0, -1.0]
        >>> IReal().hull(IReal())
        empty interval
        >>> IReal(-1, 0).hull(IReal(0.25, 10))
        [-1.0, 10.0]
        """
        if self.undefined or other.undefined:
            return IReal("undefined")
        if self.empty:
            return other
        if other.empty:
            return self
        return IReal(min(self.inf, other.inf), max(self.sup, other.sup))
