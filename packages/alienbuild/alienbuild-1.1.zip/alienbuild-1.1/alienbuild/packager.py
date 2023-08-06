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
This module implements the PACKAGER class.
"""

import color
import types

################################################################################
#PACKAGER
################################################################################

class PACKAGER:
	"""
	A PACKAGER class. 

	A PACKAGER is often called a "grouper" or a "collector" of object files.  Its
	only difference from a L{alienbuild.FILTER} is that instead of one input a PACKAGER
	takes multiple inputs and produces a single output.

	Still, however, a PACKAGER is defined by a list of filters.  
	"""

	def __init__ ( self, name, filterList ):
		"""
		Construct a PACKAGER class.

		An example PACKAGER that builds an archive (.a) file on Linux::

			LibBuilder = FILTER(
				name                      = 'LIB',
				executable                = 'ar',
				inputExtension            = 'o',
				outputExtension           = 'a',
				commandLineOptions        = [ 'rc', '{output}', '{input}' ],
				options                   = { 'IsFinal':True, 'AddToGlobalSymbols': True }
			)

			LibPackager = PACKAGER(
				name        = 'Library Builder',
				filterList  = [ LibBuilder ]
			)

			
		@type name: string
		@param name: The name of this PACKAGER.
		@type filterList: list of L{alienbuild.FILTER}s
		@param filterList: Declares the FILTERs to run on the inputs.
		"""
		self.Name               = name
		self.FilterList         = filterList

	def BuildCommandsFromInputFiles ( self, package, inputs, output ):
		"""This is a private function."""
		if len( self.FilterList ) == 0: return []

		input = []
		for i in inputs:
			if not self.FilterList[0].Match( i ):
				color.DebugPrint( 'removing input "%s" from packager "%s"' % ( i, self.Name ) )
			else:
				input.append( i )

		commands = []
		first = True
		for filter in self.FilterList:
			if first:
				first = False
			else:
				output = filter.GetOutputName( package, input )
			commands += filter.BuildCommandsFromInputFile( package, input, output )
			if type( input ) == types.ListType:
				input = filter.GetOutputName( package, output )
			else:
				input = filter.GetOutputName( package, input )
		return ( commands, input )

