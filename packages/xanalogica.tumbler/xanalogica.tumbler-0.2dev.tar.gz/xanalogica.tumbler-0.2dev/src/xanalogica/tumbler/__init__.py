######################################################################
#
# Copyright 2008 Tau Productions Inc. and Contributors.
# All Rights Reserved.
#
# This file is part of the Xanalogica component set.
#
# xanalogica.tumbler is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# xanalogica.tumbler is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# xanalogica.tumbler.  If not, see <http://www.gnu.org/licenses/>.
#
######################################################################

"""Tumblers; the base type as well as address and difference tumblers.
"""

from types import IntType, LongType, TupleType, ListType

__all__ = ["Tumbler", "AddrTumbler", "NOWHERE", "DiffTumbler", "WidthNone"]

class Tumbler(tuple):
    """Base form of an immutable, multipart integer derived from a tuple."""

    def __new__(cls, *args):
        """Construct an immutable tumbler from a digit sequence or string.
        """
        if len(args) == 0: # If no arguments provided,
            args = (0, )   #   default to a tumbler of zero

        # Handle a dot-separated string of digits
        if len(args) == 1 and isinstance(args[0], basestring):
            return tuple.__new__(cls, map(int, args[0].split('.')))

        if len(args) == 1 and type(args[0]) in (TupleType, ListType):
            digits = args[0]
        else:
            digits = tuple(args)

        for digit in digits:
            if type(digit) not in (IntType, LongType):
                raise TypeError, "%s in %s is not an integer" % (repr(digit), repr(digits))
        return tuple.__new__(cls, digits)

    def __repr__(self):
        """Return a python expression that will reconstruct this tumbler.
        """
        # (used by subclasses as well, hence the use of __class__.__name__)
        return "%s(%s)" % (self.__class__.__name__, ','.join(map(str, self)))

    def __str__(self):
        """Return the period-separated string representation of the tumbler.
        """
        return '.'.join(map(str, self))

    # Comparative Methods
    #####################

    def __nonzero__(self):
        return any(self)

    def __lt__(self, other):  return NotImplemented
    def __le__(self, other):  return NotImplemented
    def __eq__(self, other):  return NotImplemented
    def __ne__(self, other):  return NotImplemented
    def __ge__(self, other):  return NotImplemented
    def __gt__(self, other):  return NotImplemented

    def __cmp__(self, other):
        """Compare two tumblers.

           Note that you only compare address tumblers with other address
           tumblers, and difference tumblers with difference tumblers.
           Comparing an address and a difference tumbler makes no mathematical
           sense.

       A difference tumbler always begins with one or more leading zeros,
       except where it designates the entire docuverse, in which case it
       is 1.

  Every address tumbler
       starts with a digit of 1, to permit referring to the entire docuverse.
        """

        if self[0] == 0 or tuple(self) == (1, ):
            if other[0] != 0 and tuple(self) != (1, ):
                raise TypeError, "%s is not an DiffTumbler" % repr(other)
        else:
            if other[0] == 0 or tuple(self) == (1, ):
                raise TypeError, "%s is not an AddrTumbler" % repr(other)

        for i in range(min(len(self), len(other))):
            if self[i] > other[i]: return +1 # Greater-Than
            if self[i] < other[i]: return -1 # Less-Than

        if len(other) > len(self): return +1 # Greater-Than
        if len(other) < len(self): return -1 # Less-Than
        return 0 # Equal










    def tweakdigit(self, i, tweak):
        """Add an integer to one digit of a tumbler, returning a new tumbler.

           The coordinate i is based on the TAIL of the tumbler, so zero is
           the last digit and one is a digit -after- the end of the tumbler.
        """

        i += len(self) - 1

        #TBD: pass back as a Tumbler, AddrTumbler, DiffTumbler or what ???

        if i < len(self): # Interior Manipulation
            return self.__class__(*self[:i] + (self[i] + tweak, ) + self[i+1:])
        else: # Extension Manipulation
            needed_zeros = i - len(self)
            return self.__class__(*self[:] + (0, ) * needed_zeros + (tweak, ))

    def setlength(self, n):
        "Set length of tumbler to n digits, by removing digits or adding zeros"

        # Note: this was misnamed tumblertruncate in Udanax Green, even though
        #       it sometimes -extends- a tumbler.

        if n <= len(self):
            return self.__class__(*self[:n])
        else:
            return self.__class__(*self[:] + (0, ) * (n - len(self)))

    def count(self, digit):
        n = 0
        for d in self:
            if d == digit:
                n += 1
        return n

    def startswith(self, other):
        "Return true if other is a prefix of self, like a string."

        if len(other) <= len(self):
            for i in range(len(other)):
                if other[i] != self[i]:
                    return False
            return True
        else:
            return False

#TBD: implement efficient pickling of tumblers
#TBD: add to docs, how to easy_install and --editable tumblers


#void
#tumblertruncate(Tumbler *aptr, int bint, Tumbler *cptr)
#{
#    Tumbler answer;
#    int i;
#
#    movetumbler(aptr, &answer);
#    for (i = answer.exp; i < 0 && bint > 0; ++i, --bint)
#        ;
#
#    if (bint <= 0)
#        tumblerclear(&answer);
#    else
#        for (; bint < NPLACES; ++bint)
#            answer.mantissa[bint] = 0;
#}



#        if self == Tumbler(0):
#            #tumblerclear(cptr); cptr->exp = -rightshift; cptr->mantissa[0] = bint; return;
#            return Tumbler((0, ) * rightshift + (bint, ))
#
#        if (self != cptr)
#            movetumbler(self, cptr);
#
#        int idx;
#        for (idx = NPLACES; self->mantissa[--idx] == 0 && idx > 0;)
#            ;
#
#
#
#        cptr->mantissa[idx + rightshift] += bint;
#        tumblerjustify(cptr);
#        return cptr



#    def write(self, stream):
#        "Write a tumbler to an 88.1 protocol stream."
#
#        exp = 0
#        for exp in range(len(self)):
#            if self[exp] != 0:
#                break
#
#        dump = "%d" % exp
#        for digit in self[exp:]:
#            dump = dump + "." + str(digit)
#
#        stream.write(dump + "~")

#def Tumbler_read(stream, prefix=""):
#    "Read a tumbler from an 88.1 protocol stream."
#
#    chunk = prefix + stream.readchunk()
#    digits = map(int, '.'.split(chunk))
#    if not digits:
#        raise ValueError, "exponent missing in tumbler read"
#
#    digits[:1] = (0, ) * digits[0]
#    return Tumbler(digits)

class AddrTumbler(Tumbler):
    """An address within the docuverse, represented as a specialized tumbler.

       An address tumbler may have at most three zero digits, which divide
       the address into at most four fields of digits.  Every address tumbler
       starts with a digit of 1, to permit referring to the entire docuverse.

       Immutable.
    """

    def __cmp__(self, other):
        """Compare two address tumblers."""

        if not isinstance(other, AddrTumbler):
            raise TypeError, "%s is not an AddrTumbler" % repr(other)
        return Tumbler.__cmp__(self, other)

    def __add__(self, other):
        """Add an address tumbler to a difference tumbler or integer, returning a new address tumbler.

           Algorithm: left-align the digits; for every leading zero in the other
           tumbler, copy into the answer the corresponding digit in the self.
           When a nonzero digit is encountered in the other tumbler, perform an
           integer addition for that pair of digits.  Then copy into the answer
           all remaining digits from the other tumbler.

           Note that under Python, adding a tuple to a tuple concatenates them.
           But adding a tumbler to either a tumbler or tuple arithematically
           *adds* them.  Therefore sometimes it is necessary to use the [:]
           form of subscripting to convert a tumbler into a tuple, when
           concatenation is desired.
        """

        if not isinstance(other, DiffTumbler):
            raise TypeError, "%s is not a DiffTumbler" % repr(other)

        if type(other) in (IntType, LongType): # Convert a Solitary Integer
            other = self.__class__(other)             #   into a Tumbler

        for i in range(len(self)):
            if len(other) > i and other[i] != 0:
                return self.__class__(self[:i] + (self[i] + other[i], ) + other[i+1:])

        for i in range(len(self), len(other)):
            if other[i] != 0:
                return self.__class__(self + other[len(self):])

        return self

    def __sub__(self, other):
        """Subtract an address tumbler or integer from an address tumbler, returning a new difference tumbler.

           Algorithm: left-align the digits; for every digit that is the same
           both, copy a zero into the answer.  When a difference in digits is
           found, subtract them and flag an error if negative.  Otherwise, copy
           the difference into the answer and then copy into the answer all
           subsequent digits from the self.
        """

        if not isinstance(other, AddrTumbler):
            raise TypeError, "%s is not an AddrTumbler" % repr(other)

        if type(other) in (IntType, LongType): # Convert a Solitary Integer
            other = self.__class__(other)             #   into a Tumbler

        for i in range(min(len(self), len(other))):
            if self[i] < other[i]:
                raise ValueError, "%s is larger than %s" % (other, self)

            if self[i] > other[i]:
                return DiffTumbler((0, ) * i + (self[i] - other[i], ) + self[i+1:])

        if len(self) < len(other):
            raise ValueError, "%s is larger than %s" % (other, self)

        if len(self) > len(other):
            return DiffTumbler([0] * len(other) + self[len(other):])

        return WidthNone

    def intdiff(self, other):
        " "

        diff = other - self
        for i in range(len(diff)):
            if diff[i] != 0:
                return diff[i]
        else:
            return 0

    def isaNodeAddress(self):
        return self.count(0) == 0

    def isaAccountAddress(self):
        return self.count(0) == 1

    def isaDocumentAddress(self):
        return self.count(0) == 2

    def isaAtomAddress(self):
        return self.count(0) == 3

#    def isaTextAtomAddress(self):
#        return self.count(0) == 3

#    def isaLinkAtomAddress(self):
#        return self.count(0) == 3

#    def split(self):
#        "For a global address, return the docid and local components."
#
#        delim = len(self) - 1
#        while self[delim] != 0:
#            delim -= 1
#        return AddrTumbler(self[:delim]), AddrTumbler(self[delim+1:])
#
#    def globalize(self, other):
#        """Return an global address given a local address into this one, a
#        global width given a local width, or global span given a local span."""
#
#        if isinstance(other, AddrTumbler):
#            return AddrTumbler(self.digits + [0] + other.digits)
#
#        if isinstance(other, DiffTumbler):
#            return DiffTumbler([0] * len(self.digits) + [0] + other.digits)
#
#        if isinstance(other, Span):
#            return Span(self.globalize(other.start), self.globalize(other.width))
#
#        raise TypeError, "%s is not an address, offset, or span" % repr(other)
#
#    def localize(self, other):
#        """Return a local address given a global address under this one, a
#        local width given a global width, or local span given a global span."""
#
#        if isinstance(other, AddrTumbler):
#            if len(other) > len(self) and self.digits[:len(self)] + [0] == other.digits[:len(self)+1]:
#                return AddrTumbler(other.digits[len(self)+1:])
#            else:
#                raise ValueError, "%s is not within %s" % (other, self)
#
#        if isinstance(other, DiffTumbler):
#            if [0] * len(self) + [0] == other.digits[:len(self)+1]:
#                return DiffTumbler(other.digits[len(self)+1:])
#            else:
#                raise ValueError, "%s extends outside of %s" % (other, self)
#
#        if isinstance(other, Span):
#            return Span(self.localize(other.start), self.localize(other.width))
#
#        raise TypeError, "%s is not an address, offset, or span" % repr(other)

NOWHERE = AddrTumbler()

class DiffTumbler(Tumbler):
    """A span within the docuverse, represented as a specialized tumbler.

       A difference tumbler may have any number of zeros, or none at all.
       It has no meaning unless it is paired with a parent address tumbler.
       This is because it does not represent a distance in bytes, documents
       or anything else.

       A difference tumbler always begins with one or more leading zeros,
       except where it designates the entire docuverse, in which case it
       is 1.

       Unknowns:
         1. can a difference tumbler be added to a difference tumbler?
         2. can a difference tumbler be subtracted from a difference tumbler?

       Immutable.
    """

    def __cmp__(self, other):
        """Compare two address tumblers."""

        if not isinstance(other, DiffTumbler):
            raise TypeError, "%s is not an DiffTumbler" % repr(other)
        return Tumbler.__cmp__(self, other)

    def __add__(self, other):
        "Difference tumblers cannot be on the left side of addition."
        raise TypeError, "%s cannot appear on the left side of addition" % repr(self)

    def __sub__(self, other):
        "Difference tumblers cannot be on the left side of subtraction."
        raise TypeError, "%s cannot appear on the left side of subtraction" % repr(self)

WidthNone = DiffTumbler()
