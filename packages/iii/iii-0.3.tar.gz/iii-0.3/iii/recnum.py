# Copyright (C) 2009-2010 Mark A. Matienzo
#
# This file is part of iii, the Python Innovative Interfaces utility module.
#
# iii is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# iii is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with iii.  If not, see <http://www.gnu.org/licenses/>.

# recnum.py - functions to work with III record numbers

from iii.exceptions import InvalidCheckDigitError, InvalidRecordTypeError

RECORD_TYPES = {'a': 'authority',
                'b': 'bibliographic',
                'c': 'checkin',
                'e': 'electronic resource',
                'i': 'item',
                'l': 'license',
                'o': 'order',
                'p': 'patron',
                'r': 'course reserve',
                'v': 'vendor'}

def calc_check_digit(digitseq):
    """calc_check_digit(): Calculate a check digit from an III record number
    
    calc_check_digit() expects a sequence of integers representing the III
    record number without the initial character that specifies the type of
    record (e.g. 'b' for bibliographic record) or the final character that
    represents the check digit.
    
    The algorithm to calculate check digits is found at the following URL:
    http://csdirect.iii.com/manual/rmil_records_numbers.html (sign-in
    required).
    """
    _sum = 0
    multiplier = 2
    for d in reversed(digitseq):
        assert 0 <= d <= 9
        d *= multiplier
        _sum += d
        multiplier += 1
    cdig = _sum % 11
    if cdig == 10:
        return 'x'
    else:
        return str(cdig)


def validate(rec_num, quiet=True):
    """validate(): Validate a III record number containing a check digit
    
    validate() expects a string containing a III record number with a check
    digit and containing an alphabetical first character specifying the type
    of record. If quiet is True, validate() will not raise exceptions and
    instead only return True or False.
    
    A check digit of 'a' is considered valid and acts as a wildcard check
    digit replacement in contexts where the check digit is necessary.
    """
    if RECORD_TYPES.has_key(rec_num[0]):
        rec_seq = [int(digit) for digit in rec_num[1:-1]]
        check_digit = rec_num[-1]
        if (check_digit is 'a') or (check_digit == calc_check_digit(rec_seq)):
            return True
        elif quiet is True:
            return False
        else:
            raise InvalidCheckDigitError
    elif quiet is True:
        return False
    else:
        raise InvalidRecordTypeError
