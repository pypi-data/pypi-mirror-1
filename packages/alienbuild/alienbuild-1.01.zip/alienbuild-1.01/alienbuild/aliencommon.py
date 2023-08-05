################################################################################
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
The alienbuild.aliencommon module provides a number of function that assist in
some of the more complicated details of building projects and filters.  One
such example is the L{alienbuild.aliencommon.GlobRecursively} function, which 
will search for files matching a given L{alienbuild.FILETYPE}.
"""

import os, sys
import platform
from stat import *
from types import *

################################################################################
#useful things
################################################################################

NumberOfExecuteThreads = 8

UseShortOutput = True

################################################################################
#more useful things
################################################################################

def FindPath ( pathList, executable ):
	"""
	Finds a relative or absolute path of a given executable.  General usage could be::
		cmd = FindPath( os.getenv("PATH").split(":"), "gcc" ) + os.sep + "gcc"
	
	If the given executable cannot be found, a M{NameError} exception will be raised.
	@return: A string is returned giving the location of the executable.  The executable
	is not appended to the path string returned.
	"""
	for path in pathList:
		file = os.sep.join( [ path, executable ] )
		if True == os.path.isfile( file ):
			return path
	raise NameError, 'Did not find path for "%s"' % executable

def ReplaceExtension ( file, toReplace, replaceWith ):
	"""
	Replaces a given filename's extension with another. For example, M{ReplaceExtension("test.c", "c", "o")} will
	return "test.o"

	@return: a string representing the given file with its extension changed.
	"""
	return file.rpartition( '.' + toReplace )[0] + '.' + replaceWith

def MakeDirectoryForFile ( file ):
	"""
	Given a filename, create recursively all directories needed to create the file M{file}.
	"""
	dir = os.path.dirname( file )
	if os.path.isdir( dir ):
		return
	else:
		MakeDirectoryForFile( dir )
		try:
			os.mkdir( dir )
		except StatException:
			#directory already exists
			pass

def ReadMakeDependencyFile ( filename ) :
	"""
	Reads in a given GNU make-style dependency file.  A dependency file consists of a
	filename followed by a colon followed by a white-space separated list of other files.

	@return: A 2-tuple with the first element the source and the 2nd element a list of dependencies.
	"""
	f = open( filename )
	str = f.read()
	f.close()
	str = str.replace( '\\\n', '' ).replace( '/', os.sep ).replace( '\\:','_SeP_' )
	try:
		s = str.split( ':', 1 )
		src  = s[ 0 ].replace('_SeP_',':').replace( '__SpAcE__', ' ' )
		deps = s[ 1 ].replace('_SeP_',':').split()
		for i in xrange( len( deps ) ):
			deps[i] = deps[i].replace( '__SpAcE__', ' ' ).strip('"')
		last = None
		return ( src, deps )
	except IndexError:
		raise ValueError( 'not a make dependency file' )

def GlobRecursively ( filetypes, Path ):
	"""
	Searches M{Path} recursively to find files that match the given M{filetypes}. This function 
	uses L{FastWalk} so you should be aware of the L{FastWalk} limitations.

	@type filetypes: list of L{alienbuild.FILETYPE}s
	@param filetypes: Use the filetype definitions to match files in the given directory.
	@type Path: string
	@param Path: The path in which to search recursively for the given file types.

	@return: A list of file paths
	"""
	Result = []

	## Build the extension list
	extensionList = [ y.lower() for x in [ ft.FilterList[0] for ft in filetypes ] for y in x.InputExtension ];

	for root, dirs, files in FastWalk( Path ):
		for file in files:
			if os.path.splitext(file)[1][1:].lower() in extensionList:
				Result.append( os.path.join( root, file ) )

	return Result

def GlobRecursivelyForAFile ( filetofind, Path ):
	"""
	Searches M{Path} recursively to find a specific file. This function 
	uses L{FastWalk} so you should be aware of the L{FastWalk} limitations.

	@type filetofind: string
	@param filetofind: The name of the file to find
	@type Path: string
	@param Path: The path in which to search recursively for the given file.

	@return: A string of the given file to find, or just M{filetofind} if not found.
	"""
	filetofind = filetofind.lower()

	for root, dirs, files in FastWalk( Path ):
		for file in files:
			if file.lower() == filetofind:
				return os.sep.join( [ root, file ] )

	return filetofind

def GlobRecursivelyForFiles ( Path ):
	"""
	Searches M{Path} recursively to find all files. This function 
	uses L{FastWalk} so you should be aware of the L{FastWalk} limitations.

	@type Path: string
	@param Path: The path in which to search recursively for files.

	@return: A list of strings of files found.
	"""
	Result = []
	for root, dirs, files in FastWalk( Path ):
		for file in files:
			Result.append( os.sep.join( [ root, file ] ) )
	return Result

def GlobRecursivelyForDirs ( Path, maxdepth=32 ):
	"""
	Searches M{Path} recursively to find all directories. This function 
	uses L{FastWalk} so you should be aware of the L{FastWalk} limitations.

	@type Path: string
	@param Path: The path in which to search recursively for directories.

	@return: A list of strings of directories found.
	"""
	Result = []
	for root, dirs, files in FastWalk( Path, maxdepth=maxdepth ):
		for dir in dirs:
			Result.append( os.sep.join( [ root, dir ] ) )
	return Result

def CmdLineToString ( line ):
	"""
	Converts a list of command line arguments into a command line string with spaces between the arguments.

	@type line: list of strings
	@param line: The command line to convert to a string

	@return: A string of the command line
	"""
	o = ''
	for l in line:
		o = ''.join( [ o, ' ', l ] )
	return o

################################################################################
################################################################################

def BuildCommandLine ( files, package, output, commandLine, executable ):
	"""Private"""
	from metatable import METATABLE
	meta = METATABLE( package )
	meta.BuildFromSymbols( files, output )

	files = meta.ReplaceSymbolsInList( files )

	#find exec name
	if not ( ( StringType == type( executable ) ) or ( UnicodeType == type( executable ) ) ):
		return meta.ReplaceSymbolsInList( commandLine )
	else:
		if package.UseAbsolutePaths:
			try:
				first = [ os.sep.join( [ FindPath( package.Symbols.Get('exec_paths'), executable ), executable ] ) ]
			except NameError:
				#we didnt find the path so just guess that it's correct
				first = [ executable ]
		else:
			first = [ executable ]
		return meta.ReplaceSymbolsInList( first + commandLine )

################################################################################
################################################################################

def IsLinux():
	"""
	Check if running on Linux.

	@return: True if the current system is Linux; False otherwise.
	"""
	return platform.system() == 'Linux'

def IsWindows():
	"""
	Check if running on Windows.

	@return: True if the current system is Windows; False otherwise.
	"""
	return platform.system() == 'Windows'

################################################################################
################################################################################

if IsLinux():
	StatException = OSError
else:
	StatException = WindowsError

################################################################################
################################################################################

def DefaultOutputFilter ( standardOut, standardError, header ):
	"""
	This is the default OutputHandler for L{alienbuild.FILTER}s.  Its goal is
	to display standard out text in yellow (Info) and standard error text 
	in red (Error).

	This function is not meant to be called directly.
	"""
	#TODO: upgrade this to use the header...

	import color
	if standardOut   != '': color.PrintInfo( standardOut )
	if standardError != '': color.PrintError( standardError )

################################################################################
################################################################################

def FastWalk(top, depth=0, topdown=True, onerror=None, maxdepth=32):
	"""
	Recursively walk a directory using Python generators. This function is
	an optimized version of os.walk. To optimize the speed, we make the assumption
	that any file with a dot in it is not a directory. As it turns out Subversion
	software stores information in the ".svn" directory of every directory.  
	Recursing these is problamatic and time consuming.
	
	If you need to be able to use directories with dots in them you cannot use
	this function.
	"""

	# Prevent too deep of recursion
	if depth > maxdepth:
		return

	from os.path import join, isdir, islink

	# We may not have read permission for top, in which case we can't
	# get a list of the files the directory contains.  os.path.walk
	# always suppressed the exception then, rather than blow up for a
	# minor reason when (say) a thousand readable directories are still
	# left to visit.  That logic is copied here.
	try:
		# Note that listdir and error are globals in this module due
		# to earlier import-*.
		names = os.listdir(top)
	except os.error, err:
		if onerror is not None:
			onerror(err)
		return

	dirs, nondirs = [], []
	for name in names:
		#this is one of two changes from os.walk (the find)
		if ( -1 == name.find('.') ) and os.path.isdir(join(top, name)):
			dirs.append(name)
		else:
			nondirs.append(name)

	if topdown:
		yield top, dirs, nondirs
	for name in dirs:
		path = join(top, name)
		if not os.path.islink(path):
			#this is the second change from os.walk (to call our FastWalk recursively instead)
			for x in FastWalk(path, depth+1, topdown, onerror, maxdepth):
				yield x
	if not topdown:
		yield top, dirs, nondirs

################################################################################
################################################################################

def OutputFilter_IgnoreAll ( stdoutput, stderror, header ):
	"""
	An output filter for L{alienbuild.FILTER}s.  Use this if you want to ignore all
	output from an external command.
	"""
	pass

################################################################################
################################################################################

class ExitOnErrorException ( Exception ):
	pass

