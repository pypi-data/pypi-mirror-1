#
# setup.py
#
# Copyright (C) 2005 - Scott Robinson <scott@quadhome.com>
#
# This file is part of hardnote.
#
# hardnote is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# hardnote is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# hardnote; if not, write to the Free Software Foundation, Inc., 51 Franklin
# St, Fifth Floor, Boston, MA  02110-1301  USA
#

from setuptools import setup, find_packages

setup(name = "hardnote",
      version = "0.2.2",

      packages = find_packages(),

      entry_points = {'gui_scripts': ['hardnote = hardnote:main', ], },

      # Meta-data for PyPI.
      author = "Scott Robinson",
      author_email = "scott@quadhome.com",
      description = "A desktop notification daemon for hardware connection/disconnection events.",
      license = "GPL",
      keywords = "gnome hardware hotplug gtk notify notification",
      url = "http://tara.shadowpimps.net/~scott/hardnote/",
     )

# vim:et:sta:ts=8 sw=4
