#     Copyright (C) 2009
#     Associated Universities, Inc.  Washington DC, USA.
#
#     This file is part of caslib.
# 
#     caslib is free software: you can redistribute it and/or modify it under
#     the terms of the GNU Lesser General Public License as published by the
#     Free Software Foundation, either version 3 of the License, or (at your
#     option) any later version.
#
#     caslib is distributed in the hope that it will be useful, but WITHOUT ANY
#     WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#     FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
#     more details.
#
#     You should have received a copy of the GNU Lesser General Public License
#     along with caslib.  If not, see <http://www.gnu.org/licenses/>.

'''Provides an interface to CAS servers and services'''

from cas_dance import *

# If the new ssl module is available, then export validating_https bits
try:
    import ssl

except ImportError:
    pass

else:
    from validating_https import *

