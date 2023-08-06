#!/usr/bin/env python
# -*- mode: python; c-basic-offset: 2; indent-tabs-mode: nil; -*-
#  vim:expandtab:shiftwidth=2:tabstop=2:smarttab:
#  gearman-interface: Interface Wrappers for Gearman
#
#   Copyright (C) 2009 David Lenwell
#   Copyright (C) 2009 Monty Taylor
#    
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or 
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from gearman import libgearman
client = libgearman.Client()
client.add_server('localhost')
(ret, handle)= client.do_background('worker_func', 'Hello World!')
print handle
while True:
  (ret, is_known, is_running, numerator, denominator)= client.job_status(handle)
  if ret != libgearman.GEARMAN_SUCCESS:
    print "Error: ", ret
    break
  print ret, is_known, is_running, numerator, denominator
  if not is_known:
    break

