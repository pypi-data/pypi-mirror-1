# Copyright (C) 2008-2009 John Millikin

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "John Millikin <jmillikin@gmail.com>"
__copyright__ = "Copyright 2008-2009, John Millikin"
__version__ = (1, 1, 3)
__license__ = "GPL"

from django_genshi.context import Context, RequestContext
from django_genshi.loader import get_template, select_template, TemplateNotFound
from django_genshi.shortcuts import (render_to_stream, render_to_response,
                                     render_to_response_autodetect)
