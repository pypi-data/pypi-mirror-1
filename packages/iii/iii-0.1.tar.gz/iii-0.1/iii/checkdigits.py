# Copyright (C) 2009 Mark A. Matienzo
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

# checkdigits.py - functions to work with III record number check digits

def calc_check_digit(digitseq):
    """calc_check_digit(): Calculate a check digit from an III record number
    
    calc_check_digit expects a sequence of integers representing the III
    record number without the initial character that specifies the type of
    record (e.g. 'b' for bibliographic record) or the final character that
    represents the check digit.
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
