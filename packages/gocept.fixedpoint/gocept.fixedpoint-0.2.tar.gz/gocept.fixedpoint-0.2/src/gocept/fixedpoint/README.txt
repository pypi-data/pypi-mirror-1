================
FixedPoint Usage
================

>>> from gocept.fixedpoint import FixedPoint

FixedPoint objects support decimal arithmetic with a fixed number of
digits (called the object's precision) after the decimal point.  The
number of digits before the decimal point is variable & unbounded.

The precision is user-settable on a per-object basis when a FixedPoint
is constructed, and may vary across FixedPoint objects.  The precision
may also be changed after construction via FixedPoint.set_precision(p).
Note that if the precision of a FixedPoint is reduced via set_precision,
information may be lost to rounding.

>>> x = FixedPoint("5.55")  # precision defaults to 2
>>> print x
5.55
>>> x.set_precision(1)      # round to one fraction digit
>>> print x
5.6
>>> print FixedPoint("5.55", 1)  # same thing setting to 1 in constructor
5.6
>>> repr(x) #  returns constructor string that reproduces object exactly
"FixedPoint('5.6', 1)"

When FixedPoint objects of different precision are combined via + - * /,
the result is computed to the larger of the inputs' precisions, which also
becomes the precision of the resulting FixedPoint object.

>>> print FixedPoint("3.42") + FixedPoint("100.005", 3)
103.425
>>> print FixedPoint("2.1") * FixedPoint("10.995", 3)
23.090

When a FixedPoint is combined with other numeric types (ints, floats,
strings representing a number) via + - * /, then similarly the computation
is carried out using-- and the result inherits --the FixedPoint's
precision.

>>> print FixedPoint(1) / 7
0.14
>>> print FixedPoint(1, 30) / 7
0.142857142857142857142857142857
>>>

The string produced by str(x) (implictly invoked by "print") always
contains at least one digit before the decimal point, followed by a
decimal point, followed by exactly x.get_precision() digits.  If x is
negative, str(x)[0] == "-".

>>> print FixedPoint("1.0", 5)
1.00000
>>> print FixedPoint("1.234567", 2)
1.23
>>> str(FixedPoint("-1.45"))[0] == "-"
True

The FixedPoint constructor can be passed an int, long, string, float,
FixedPoint, or any object convertible to a float via float() or to a
long via long().  Passing a precision is optional; if specified, the
precision must be a non-negative int.  There is no inherent limit on
the size of the precision, but if very very large you'll probably run
out of memory.

>>> FixedPoint("1.0", -3) # negative precision values are not allowed
Traceback (most recent call last):
...
ValueError: precision must be >= 0: -3

Note that conversion of floats to FixedPoint can be surprising, and
should be avoided whenever possible.  Conversion from string is exact
(up to final rounding to the requested precision), so is greatly
preferred.

>>> print FixedPoint(1.1e30)
1099999999999999993725589651456.00
>>> print FixedPoint("1.1e30")
1100000000000000000000000000000.00
>>>

The following Python operators and functions accept FixedPoints in the
expected ways:

    - binary + - * / % divmod with auto-coercion of other types to
      FixedPoint. + - % divmod of FixedPoints are always exact.* / of
      FixedPoints may lose information to rounding, in which case the
      result is the infinitely precise answer rounded to the result's
      precision.
    - divmod(x, y) returns (q, r) where q is a long equal to
      floor(x/y) as if x/y were computed to infinite precision,
      and r is a FixedPoint equal to x - q * y; no information
      is lost.  Note that q has the sign of y, and abs(r) < abs(y).
    - unary -
    - == != < > <= >=  cmp
    - min, max
    - float, int, long (int and long truncate)
    - abs
    - str, repr
    - hash
    - use as dict keys
    - use as boolean (e.g. "if some_FixedPoint:" -- true iff not zero)

Methods unique to FixedPoints:
   - copy(): return new FixedPoint with same value
   - frac(): long(x) + x.frac() == x
   - get_precision(): return the precision(p) of this FixedPoint object
   - set_precision(p): set the precision of this FixedPoint object

>>> FixedPoint("1.0", 3).copy()
FixedPoint('1.000', 3)
>>> FixedPoint("1.0").copy() # default precision is 2
FixedPoint('1.00', 2)

>>> FixedPoint('123.45').frac()
FixedPoint('0.45', 2)

>>> FixedPoint('123').get_precision()
2
>>> fp = FixedPoint('123')
>>> fp.set_precision(5)
>>> fp
FixedPoint('123.00000', 5)

Testing several operators:

>>> fp = FixedPoint
>>> o = fp("0.1")
>>> str(o) == "0.10"
True
>>> t = fp("-20e-2", 5)
>>> str(t) == "-0.20000"
True
>>> t < o
True
>>> o > t
True
>>> min(o, t) == min(t, o) == t
True
>>> max(o, t) == max(t, o) == o
True
>>> o != t
True
>>> --t == t
True
>>> abs(t) > abs(o)
True
>>> abs(o) < abs(t)
True
>>> o == o and t == t
True
>>> t.copy() == t
True
>>> o == -t/2 == -.5 * t
True
>>> abs(t) == o + o
True
>>> abs(o) == o
True
>>> o/t == -0.5
True
>>> -(t/o) == (-t)/o == t/-o == 2
True
>>> 1 + o == o + 1 == fp(" +00.000011e+5  ")
True
>>> 1/o == 10
True
>>> o + t == t + o == -o
True
>>> 2.0 * t == t * 2 == "2" * t == o/o * 2L * t
True
>>> 1 - t == -(t - 1) == fp(6L)/5
True
>>> t*t == 4*o*o == o*4*o == o*o*4
True
>>> fp(2) - "1" == 1
True
>>> float(-1/t) == 5.0
True
>>> 1/(42 + fp("1e-20", 20) - 42) == fp("100.0E18")
True
>>> o = fp(".9995", 4)
>>> 1 - o == fp("5e-4", 10)
True
>>> o.set_precision(3)
>>> o == 1
True
>>> o = fp(".9985", 4)
>>> o.set_precision(3)
>>> o == fp(".998", 10)
True
>>> o == o.frac()
True
>>> o.set_precision(100)
>>> o == fp(".998", 10)
True
>>> o.set_precision(2)
>>> o == 1
True
>>> x = fp(1.99)
>>> long(x) == -long(-x) == 1L
True
>>> int(x) == -int(-x) == 1
True
>>> x == long(x) + x.frac()
True
>>> -x == long(-x) + (-x).frac()
True
>>> fp(7) % 4 == 7 % fp(4) == 3
True
>>> fp(-7) % 4 == -7 % fp(4) == 1
True
>>> fp(-7) % -4 == -7 % fp(-4) == -3
True
>>> fp(7.0) % "-4.0" == 7 % fp(-4) == -1
True
>>> fp("5.5") % fp("1.1") == fp("5.5e100") % fp("1.1e100") == 0
True
>>> divmod(fp("1e100"), 3) == (long(fp("1e100")/3), 1)
True
>>> fp("1") != ''
True
