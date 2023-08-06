# -*- coding: utf-8 -*-
# Copyright (C)2009 Ingeniweb

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


from MemoryProfiler import Profiler


def initialize(context):
  control_panel = context._ProductContext__app.Control_Panel
  zpid = Profiler.id
  zp = getattr(control_panel, zpid, None)
  if zp is None:
    zp = Profiler()
    control_panel._setObject(zpid, zp)

