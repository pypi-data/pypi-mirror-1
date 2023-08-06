# Copyright (C) 2007 by INdT
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# @author Gustavo Sverzut Barbieri <gustavo.barbieri@openbossa.org>

from c_lightmediascanner import LightMediaScanner

LMS_PROGRESS_STATUS_UP_TO_DATE = 0
LMS_PROGRESS_STATUS_PROCESSED = 1
LMS_PROGRESS_STATUS_DELETED = 2
LMS_PROGRESS_STATUS_KILLED = 3
LMS_PROGRESS_STATUS_ERROR_PARSE = 4
LMS_PROGRESS_STATUS_ERROR_COMM = 5
