# Fedora Developer Shell
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors: Yaakov M. Nemoy <ynemoy@redhat.com>
#

class Validator(object):
    def validate(obj):
        return None


class Identity(Validator):
    def validate(obj):
        return obj


class TypeValidator(Validator):
    def __init__(self, base, factory):
        self.base = base
        self.factory = factory

    def validate(self, obj):
        if issubclass(obj, self.base):
            return obj
        else:
            return self.validate(self.factory(obj))
        

# class Directory(Validator):
#     def validate(obj):
#         if issubclass(obj, Directory):
#             return obj
#         else:
#             return Directory(obj)
#     pass


def isvalidator(validator):
    return issubclass(validator, Validator)

def validate(validator):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **keys):
            
            return f(*args, **keys)
        return decorated
    return decorator
