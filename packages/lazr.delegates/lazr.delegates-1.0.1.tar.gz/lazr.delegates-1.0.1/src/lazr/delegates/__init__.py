# Copyright 2008 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.delegates.
#
# lazr.delegates is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# lazr.delegates is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.delegates.  If not, see <http://www.gnu.org/licenses/>.

"""Decorator helpers that simplify class composition."""

__version__ = '1.0.1'

# Re-export in such a way that __version__ can still be imported if
# dependencies are not yet available.
try:
    # While we generally frown on "*" imports, this, combined with the fact we
    # only test code from this module, means that we can verify what has been
    # exported.
    from lazr.delegates._delegates import *
    from lazr.delegates._delegates import __all__
except ImportError:
    pass
