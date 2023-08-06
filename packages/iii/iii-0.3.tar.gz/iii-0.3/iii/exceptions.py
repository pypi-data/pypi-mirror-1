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

# exceptions.py - Exceptions for III module

class ValidationError(Exception):
    """exceptions.ValidationError: Base class for validation errors"""
    pass


class InvalidCheckDigitError(ValidationError):
    "exceptions.InvalidCheckDigitError: Raised when check digit is invalid"
    pass


class InvalidRecordTypeError(ValidationError):
    "exceptions.InvalidRecordTypeError: Raised when record type is invalid"
    pass

class RecordDoesNotExistError(ValidationError):
    "exceptions.RecordDoesNotExistError: Raised when record doesn't exist'"
    pass

class InvalidWebPACInstanceError(ValidationError):
    pass
