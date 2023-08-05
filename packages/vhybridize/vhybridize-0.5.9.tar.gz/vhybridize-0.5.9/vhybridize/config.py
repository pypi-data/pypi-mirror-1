#  Copyright (C) 2006-2007 Free Software Foundation

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


from vhybridize import __version__ as VERSION

FORMAT_VERSION = 1 # bump this if you change the format, update also
                   # the README

FILE_VERSION_TAG = "VHY-FORMAT-%s" % FORMAT_VERSION
FILE_FORMAT_CMT = "#(start, stop, probe, %length, %identity, probe_length)"

VHY_START = 0 
VHY_STOP  = 1
VHY_PROBE = 2
VHY_A_LEN = 3 # align %len
VHY_A_ID  = 4 # align %id
VHY_P_LEN = 5 # probe len
