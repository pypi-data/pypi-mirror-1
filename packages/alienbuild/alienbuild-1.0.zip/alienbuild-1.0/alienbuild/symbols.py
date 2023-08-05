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
The alienbuild.symbols module is to provide symbol support.  A symbol is a word
enclosed in curly braces in certain fields of certain classes.  For example,
the L{alienbuild.FILTER} class's CommandLineOptions field can use symbols.  The
built-in symbols are:

	1. for L{alienbuild.FILTER}s
		- {input} : the input file to the filter
		- {output} : the target output file to the filter
		- {include} : replaced once for every include path
	2. TODO
"""

GlobalSymbols = {}

#items in second will override items in first
def MergeDict( first, second ):
	"""
	Merge two maps.

	@type first: map
	@type second: map

	@returns: Return a new map that contains the keys either both maps.  If a key exists in both, the M{second}'s
	entry will be used.
	"""
	merge = { }
	for i in first.iteritems():
		merge[i[0]] = i[1]
	for i in second.iteritems():
		merge[i[0]] = i[1]
	return merge

def SetGlobalSymbols ( symbols ):
	"""
	Set the global symbol table used in AlienBuild.  
	
	The global symbol table includes things like exec_paths that need to be set in order
	for packages to build properly.  

	@type symbols: map
	"""
	global GlobalSymbols
	GlobalSymbols = symbols

def SetGlobalSymbol ( name, value ):
	"""
	Insert a key/value pair into the global symbol table.
	
	The global symbol table includes things like exec_paths that need to be set in order
	for packages to build properly.  

	@type name: string
	@type value: string
	"""

	global GlobalSymbols
	GlobalSymbols[name] = value

def GetGlobalSymbol ( name ):
	"""
	Look up a given key in the global symbol table.
	
	The global symbol table includes things like exec_paths that need to be set in order
	for packages to build properly.  

	@type name: string
	@return: A string, or raises a KeyError exception.
	"""
	global GlobalSymbols
	return GlobalSymbols[name]

class SYMBOLS:
	"""A private class."""
	def __init__ ( self, symbols={} ):
		self.Symbols = symbols

	def Get ( self, name ):
		if self.Symbols.has_key( name ):
			return self.Symbols[name]
		global GlobalSymbols
		if GlobalSymbols.has_key( name ):
			return GlobalSymbols[name]
		else:
			raise ValueError( 'no symbol "%s" defined' % name )

	def Set ( self, name, value ):
		self.Symbols[name] = value

	def All ( self ):
		global GlobalSymbols
		items = self.Symbols.items()
		for i in GlobalSymbols.items():
			if not self.Symbols.has_key( i[0] ):
				items.append( i )
		return items

	def LocalIter ( self ):
		return self.Symbols.iteritems()
	def GlobalIter ( self ):
		global GlobalSymbols
		return GlobalSymbols.iteritems()

	def Exists ( self, name ):
		global GlobalSymbols
		return GlobalSymbols.has_key( name ) or self.Symbols.has_key( name )

