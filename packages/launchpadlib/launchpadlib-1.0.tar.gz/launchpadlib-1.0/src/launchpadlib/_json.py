# Copyright 2009 Canonical Ltd.

# This file is part of launchpadlib.
#
# launchpadlib is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, version 3 of the License.
#
# launchpadlib is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with launchpadlib. If not, see <http://www.gnu.org/licenses/>.

"""Classes for working with JSON."""

__metaclass__ = type
__all__ = ['DatetimeJSONEncoder']

import datetime
import simplejson

class DatetimeJSONEncoder(simplejson.JSONEncoder):
    """A JSON encoder that understands datetime objects.

    Datetime objects are formatted according to ISO 1601.
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return simplejson.JSONEncoder.default(self, obj)
