#!/usr/bin/env python
#
# Copyright (C) 2008 Martin Owens
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from distutils.core import setup
from fnmatch        import fnmatch
from moxml.config   import __version__
import os

# remove MANIFEST. distutils doesn't properly update it when the contents of directories change.
if os.path.exists('MANIFEST'): os.remove('MANIFEST')

def listfiles(*dirs):
	dir, pattern = os.path.split(os.path.join(*dirs))
	return [os.path.join(dir, filename)
		for filename in os.listdir(os.path.abspath(dir))
			if filename[0] != '.' and fnmatch(filename, pattern)]


setup(
		name             = 'python-moxml-config',
		version          = __version__,
		description      = 'Python XML Based Configuration Management',
		long_description = "Using xml this base module allows the storage of configuration and caches.",
		author           = 'Martin Owens',
		author_email     = 'doctormo@gmail.com',
		platforms        = 'linux',
		license          = 'GPLv3',
		py_modules       = [ 'moxml.config' ],
		provides         = [ 'moxml.config' ],
	)

