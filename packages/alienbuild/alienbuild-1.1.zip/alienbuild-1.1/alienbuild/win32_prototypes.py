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
This module declares generic L{alienbuild.FILETYPE}s, L{alienbuild.FILTER}s, and
L{alienbuild.PACKAGER}s useful for building standard C and C++ applications
on Windows using MSVC.

@var DefaultCompileArguments: The default compile arguments for compile filters
in this module.
@type DefaultCompileArguments: list
@var CompileFilter: A FILTER for compiling a cpp file into an object file but also provides a dependency generator.
@type CompileFilter: L{alienbuild.FILTER}
@var LibBuilder: A FILTER for creating an archive (foo.lib) from a collection of object (.obj) files.
@type LibBuilder: L{alienbuild.FILTER}
@var Link: A FILTER for creating an Windows EXE executable from a collection of object (.obj) files.
@type Link: L{alienbuild.FILTER}

@var CppFileType: A FILETYPE that defines how to handle a C++ file
@type CppFileType: L{alienbuild.FILETYPE}

@var LibPackager: A PACKAGER that defines how to build libraries
@type LibPackager: L{alienbuild.PACKAGER}

"""

from filetype import FILETYPE
from filter   import FILTER
from packager import PACKAGER
import aliencommon
import color
import os
import re
import types

################################################################################
################################################################################

DefaultCompileArguments = [
	( 'noopt', [ '/GL-', '/Od' ] ),
	( 'opt'  , [ '/GL', '/Ox' ] ),
	( 'profile', [ '/DPROFILE' ] ),
	'/D{defines}',
	'/U{undefines}',
	( 'debug', [ '/DDEBUG', '/D_DEBUG' ] ),
	( 'nodebug', [ '/DNDEBUG' ] ),
	'/DWIN32',
	'/I"{include}"',
	'/Fd"{pdb}"',
	'"{input}"',
	'/Fo"{output}"',
]

################################################################################
################################################################################

def MicrosoftOutputFilter ( standardOut, standardError, header, cmd ):
	"""
	This is the output filter used on Microsoft's MSVC Compiler.
	"""
	import color
	def Strip( x ):
		x = re.compile( r'Microsoft \(R\).*' ).sub( '', x )
		x = re.compile( r'Copyright \(C\) Microsoft Corporation.*' ).sub( '', x )
		x = re.compile( r'Creating library.*' ).sub( '', x )

		#libgame specific...
		x = re.compile( r'.*__NULL_IMPORT_DESCRIPTOR already defined in.*second definition ignored.*' ).sub( '', x )
		x = re.compile( r'.*no public symbols found; archive member will be inaccessible.*' ).sub( '', x )

		x = x.strip( ' \t\r\n')
		if header and x:
			return header + x.replace( '\n', '\n' + header )
		else:
			return x
	
	standardOut   = Strip( standardOut )
	standardError = Strip( standardError )

	#for msvc strip out that one line filename that it says when it completes a file
	if type( cmd.Files ) in [ types.StringType, types.UnicodeType ]:
		input = cmd.Files[cmd.Files.rfind(os.sep)+1:]
		if standardOut.endswith( input ):
			standardOut = standardOut.replace( header + input, '' )

	if standardOut:
		if -1 != standardOut.find( 'warning' ):
			color.SetOutputColor( color.WarningColor )
		elif -1 != standardOut.find( 'error' ):
			color.SetOutputColor( color.ErrorColor )
		else:
			color.SetOutputColor( color.InfoColor )

		print standardOut
		color.SetOutputColor()
	if standardError:
		color.SetOutputColor( color.ErrorColor )
		print standardError
		color.SetOutputColor()

	## Need to return warnings
	return standardOut

################################################################################
#Filters
################################################################################

import gendep

CompileFilter = FILTER(
	name                      = 'COMPILE',
	executable                = 'cl.exe',
	inputExtension            = [ 'cpp', 'c' ],
	outputExtension           = 'o',
	commandLineOptions        = [ '/c', '/FI"{force_includes}"', '/Zi' ] + DefaultCompileArguments,
	options                   = { 'IsFinal':False },
	dependencyGenerator       = 'python.exe',
	dependencyExtension       = 'd',
	dependencyGenerateOptions = [ '"%s"' % gendep.__file__, '/E' ],
	outputFilter              = MicrosoftOutputFilter,
)

CompileUsingPchFilter = FILTER(
	name                      = 'COMPILE',
	executable                = 'cl.exe',
	inputExtension            = 'cpp',
	outputExtension           = 'o',
	commandLineOptions        = [ '/c', '/Yu"{pch}"', '/FI"{pch}"', '/Fp"{pch_object}"', '/Zi' ] + DefaultCompileArguments,
	options                   = { 'IsFinal':False },
	dependencyGenerator       = 'python.exe',
	dependencyExtension       = 'd',
	dependencyGenerateOptions = [ '"%s"' % gendep.__file__, '/E' ],
	outputFilter              = MicrosoftOutputFilter,
)

PchFilter = FILTER(
	name                      = 'PCH',
	executable                = 'cl.exe',
	inputExtension            = 'pch_cpp',
	outputExtension           = 'pch',
	commandLineOptions        = DefaultCompileArguments[:-2] + [ '/Zi', '/TP', '/c', '/Yc', '"{input}"', '/Fp"{output}"' ],
	options                   = { 'IsFinal':True, 'IsOutput':True },
	dependencyGenerator       = 'python.exe',
	dependencyExtension       = 'd',
	dependencyGenerateOptions = [ '"%s"' % gendep.__file__, '/E' ],
	outputFilter              = MicrosoftOutputFilter,
)

LibBuilder = FILTER(
	name                      = 'LIB',
	executable                = 'lib.exe',
	inputExtension            = 'o',
	outputExtension           = 'lib',
	commandLineOptions        = [ '/SUBSYSTEM:WINDOWS', '/OUT:{output}', '/LIBPATH:"{library_paths}"', '"{input}"', '"{libraries}"' ],
	options                   = { 'IsFinal':True, 'IsOutput':True },
	outputFilter              = MicrosoftOutputFilter,
#	externalDependencies      = [ '{libraries}' ],
)

DllBuilder = FILTER(
	name                      = 'DLL',
	executable                = 'link.exe',
	inputExtension            = 'o',
	outputExtension           = 'dll',
	commandLineOptions        = [ '/DEBUG', '/PDB:"{pdb}"', '/DLL', '/OUT:"{output}"', '/LIBPATH:"{library_paths}"', '"{input}"', '"{libraries}"' ],
	options                   = { 'IsFinal':True, 'IsOutput': True },
	outputFilter              = MicrosoftOutputFilter,
#	externalDependencies      = [ '{libraries}' ],
)

PydBuilder = FILTER(
	name                      = 'PYD',
	executable                = 'link.exe',
	inputExtension            = 'o',
	outputExtension           = 'pyd',
	commandLineOptions        = [ ( 'DEBUG', '/DEBUG' ), '/DLL', '/OUT:{output}', '/LIBPATH:"{library_paths}"', '"{input}"', '"{libraries}"' ],
	options                   = { 'IsFinal':True, 'IsOutput': True },
	outputFilter              = MicrosoftOutputFilter,
#	externalDependencies      = [ '{libraries}' ],
)

Link = FILTER(
	name                      = 'LINK',
	executable                = 'link.exe',
	inputExtension            = 'o',
	outputExtension           = 'exe',
	commandLineOptions        = [ '/DEBUG', '/SUBSYSTEM:WINDOWS', '/PDB:"{pdb}"', '/OUT:"{output}"', '/LIBPATH:"{library_paths}"', '"{input}"', '"{libraries}"' ],
	options                   = { 'IsFinal':True },
	outputFilter              = MicrosoftOutputFilter,
#	externalDependencies      = [ '{libraries}' ],
)

################################################################################
#filetypes
################################################################################

CppFileType = FILETYPE(
	extension  = [ 'cpp', 'c' ],
	filterList = [ CompileFilter ]
)

PchFileType = FILETYPE(
	extension  = 'pch_cpp',
	filterList = [ PchFilter ]
)

################################################################################
#packagers
################################################################################

LibPackager = PACKAGER(
	name        = 'Library Builder',
	filterList  = [ LibBuilder ]
)

DllPackager = PACKAGER(
	name        = 'Dll Builder',
	filterList  = [ DllBuilder ]
)

PydPackager = PACKAGER(
	name        = 'Pyd Builder',
	filterList  = [ PydBuilder ]
)

ExePackager = PACKAGER(
	name        = 'Exe Builder',
	filterList  = [ Link ]
)

################################################################################
#GetPrototype(name)
################################################################################

Mapping = {
	'C++ Filter'         : CompileFilter,
	'Pch Filter'         : PchFilter,
	'Library Filter'     : LibBuilder,
	'Dll Filter'         : DllBuilder,
	'Pyd Filter'         : PydBuilder,
	'Link Filter'        : Link,
	'C++ File Type'      : CppFileType,
	'Pch File Type'      : PchFileType,
	'Library Packager'   : LibPackager,
	'Dll Packager'       : DllPackager,
	'Pyd Packager'       : PydPackager,
	'Executable Packager': ExePackager,
}

def GetPrototype ( name ):
	return Mapping[ name ]

def AddPrototype ( name, value ):
	Mapping[ name ] = value

