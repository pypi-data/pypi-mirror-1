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
This is a private module.
"""

import os
import re
from types import *

################################################################################
#METATABLE
################################################################################

class METATABLE:
	"""
	This is a private class.
	"""
	def __init__ ( self, package ):
		self.ReplaceRE = re.compile( r'{[^{}]+}' )
		self.Package  = package
		self._Build()
		self.Compile()

	def _GetValues ( self, v ):
		if type( v ) != ListType: return [ v ]
		else:                     return v

	def _Build ( self ):
		#search and replace input,output meta strings in the argument list
		get = self.Package.Symbols.__getitem__
		self.BaseMetaStrings = [
			( '{include}'   , get('include_dirs')                                 ),
			( '{obj}'       , [ get('packageobj') ]                               ),
			( '{bin}'       , [ get('packagebin') ]                               ),
			( '{databin}'   , [ os.sep.join( [ get('basebin'), '..', 'data' ] ) ] ),
		]

		self.BaseMetaStrings += [ ( '{%s}' % k, self._GetValues( v ) ) for k,v in self.Package.Symbols.iteritems() ]

	def BuildFromSymbols ( self, inputs, output=None, compile=True ):
		if type( inputs ) != ListType: inputs = [ inputs ]
		extra = [ ( '{input}' , inputs ) ]
		self.Input = extra
		if output:
			extra.append( ( '{output}', [ output ] ) )
			self.Output = extra[1]
		else:
			self.Output = []
		self.MetaStrings = self.BaseMetaStrings + extra

		for i in extra:
			self.MetaTable[i[0]] = i[1]

	def Compile ( self ):
		self.MetaTable = {}
		for i in self.BaseMetaStrings:
			if not self.MetaTable.has_key( i[0] ):
				self.MetaTable[i[0]] = i[1]

	def Replace ( self, lines ):
		rtn = []
		for line in lines:
			expanded = [ line ]
			if -1 != line.find( '{' ):
				for toReplace, withReplace in self.MetaStrings:
					if 0 < line.count( toReplace ):
						expanded = [ i.replace( toReplace, j ) for i in expanded for j in withReplace ]
			rtn = rtn + expanded
		return rtn

	def ReplaceString ( self, line ):
		return self.Replace( [ line ] )

	def ReplaceSymbolsInList ( self, list ):
		if type( list ) != ListType: list = [ list ]
		list = self.ReplaceFlagsInList( list )

		replaced = list
		while True:
			replacedFirst = self.Replace( replaced      )
			replaced      = self.Replace( replacedFirst )
			if replaced == replacedFirst: break
		return [ x for x in replaced if -1 == x.find( '{' ) ]

	def ReplaceFlagsInList ( self, list ):
		replaced = []
		for i in range( len( list ) ):
			if type( list[i] ) == TupleType:
				if list[i][0] in self.Package.BuildFlags:
					if type( list[i][1] ) == ListType:
						replaced += self.ReplaceFlagsInList( list[i][1] )
					else:
						replaced.append( list[i][1] )
			else:
				replaced.append( list[i] )
		return replaced

