#################################################################################
#
# (C) Falling Down Games, Inc.  2007
#
# AlienBuild - A large code and asset build system written in python
#
# by Patrick Crawley (pncrawley@gmail.com) and Charles Mason
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-130
#
################################################################################

"""
The alienbuild.filetype module implements the L{alienbuild.FILETYPE} class.
"""

import color
from types import *

################################################################################
#FILETYPE
################################################################################

class FILETYPE:
	"""
	A file type.  This class contains information pertaining to how to process
	a single file type from filter to filter.
	"""

	def __init__ ( self, extension, filterList, name=None ):
		"""
		Construct a FILETYPE object.

		@type extension: string or list of strings
		@param extension: The file type extension without the period '.'.  I.e., "cpp" or "c"
		@type filterList: a list of L{alienbuild.FILTER}s.
		@param filterList: Each filter is run in sequence passing output to input of the next
		in order to process a file.  For instance a C++ project might do 
		M{PREPROCESS->COMPILE->ASSEMBLE}.
		@type name: string
		@param name: The name of this file type.  Largely unused, but provided for completeness.
		"""
		self.Name        = name
		self.FilterList  = filterList
		if type( extension ) == StringType or type( extension ) == UnicodeType:
			self.Extension = [ extension ]
		else:
			self.Extension = extension

	def Match ( self, file ):
		"""Private"""
		for ext in self.Extension:
			if file.endswith( '.' + ext ): return True
		return False

	def BuildCommandsFromInputFile ( self, package, file ):
		"""Private"""
		commands = []
		for filter in self.FilterList:
			commands += filter.BuildCommandsFromInputFile( package, file )
			file = filter.GetOutputName( package, file )
		if self.FilterList[-1].DependencyStyle == 'ALIENBUILD':
			return ( commands, None )
		else:
			return ( commands, file )

