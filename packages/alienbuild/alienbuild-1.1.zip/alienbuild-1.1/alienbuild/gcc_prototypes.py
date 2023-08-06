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
on Linux.

@var DefaultCompileArguments: The default compile arguments for compile filters
in this module.
@type DefaultCompileArguments: list
@var CppPreprocessFilter: A FILTER for processing .cpp into pre-processed C++ output.
@type CppPreprocessFilter: L{alienbuild.FILTER}
@var CppCompileFilter: A FILTER for compiling a cpp file into an object file.
@type CppCompileFilter: L{alienbuild.FILTER}
@var LibBuilder: A FILTER for creating an archive (libfoo.a) from a collection of object (.o) files.
@type LibBuilder: L{alienbuild.FILTER}
@var Link: A FILTER for creating an Linux ELF executable from a collection of object (.o) files.
@type Link: L{alienbuild.FILTER}
@var RdfToHeaderFilter: A FILTER to parse RDF files and generate header files (.h).
@type RdfToHeaderFilter: L{alienbuild.FILTER}

@var CppFileType: A FILETYPE that defines how to handle a C++ file
@type CppFileType: L{alienbuild.FILETYPE}
@var RdfFileType: A FILETYPE that defines how to handle an RDF file
@type RdfFileType: L{alienbuild.FILETYPE}

@var LibPackager: A PACKAGER that defines how to build libraries
@type LibPackager: L{alienbuild.PACKAGER}

"""

import os
import shutil
from filter   import FILTER
from filetype import FILETYPE
from packager import PACKAGER

################################################################################
################################################################################

DefaultCompileArguments = [
	( 'debug'  , '-g3' ),
	( 'nodebug', '-g0' ),
	( 'opt'    , '-O3' ),
	( 'noopt'  , '-O0' ),
	'-I{include}', 
	'-o {output}', 
	'{input}', 
	'-D{defines}',
	'-DGCC',
]

################################################################################
#Filters
################################################################################

CppCompileFilter = FILTER(
	name                      = 'COMPILE',
	executable                = 'g++',
	inputExtension            = 'cpp',
	outputExtension           = 'o',
	commandLineOptions        = [ '-c' ] + DefaultCompileArguments,
	dependencyExtension       = 'd',
	dependencyGenerateOptions = [ '-M' ]
)

## TODO: remove this.
CompileFilter = FILTER(
	name                      = 'COMPILE',
	executable                = 'g++',
	inputExtension            = 'cpp',
	outputExtension           = 'o',
	commandLineOptions        = [ '-c' ] + DefaultCompileArguments,
)

LibBuilder = FILTER(
	name                      = 'LIB',
	executable                = 'ar',
	inputExtension            = 'o',
	outputExtension           = 'a',
	commandLineOptions        = [ 'rc', '{output}', '{input}' ],
	options                   = { 'IsFinal':True, 'IsOutput': True }
)

Link = FILTER(
	name                      = 'LINK',
	executable                = 'g++',
	inputExtension            = 'o',
	outputExtension           = 'elf',
	commandLineOptions        = [ '-o {output}', '{input}', '-L{library_paths}', '{libraries}' ],
	options                   = { 'IsFinal':True }
)

## TODO: move to common_prototypes
def RdfHeaderFilterExecutable( args ):
	"""
	Runs the RDF utility on args[0] and produces args[1]

	This is an internal function.
	"""

	from libgame.tools import buildrdfheader
	import libgame.tools.toollib
	xmldict = libgame.tools.toollib.ReadXmlFile( args[0] )
	#TODO: make this process all children not just the first 'resource' it finds
	buildrdfheader.BuildRdfHeader( xmldict['children'][0], args[1] )

RdfToHeaderFilter = FILTER(
	name                      = 'RDFHEADER',
	executable                = RdfHeaderFilterExecutable,
	inputExtension            = 'rdf',
	outputExtension           = 'h',
	commandLineOptions        = [ '{input}', '{output}' ],
	externalDependencies      = [ '{libgame}/tools/buildrdfheader.py', '{libgame}/tools/buildrdfresource.py' ],
	options                   = { 'IsFinal':True }
)

################################################################################
#filetypes
#TODO: these are common
################################################################################

CppFileType = FILETYPE(
	extension  = 'cpp',
	filterList = [ CppCompileFilter ]
)

RdfFileType = FILETYPE(
	extension  = 'rdf',
	filterList = [ RdfToHeaderFilter ]
)

################################################################################
#packagers
#TODO: also common
################################################################################

LibPackager = PACKAGER(
	name        = 'Library Builder',
	filterList  = [ LibBuilder ]
)

ExePackager = PACKAGER(
	name        = 'Executable Builder',
	filterList  = [ Link ]
)


################################################################################
#GetPrototype(name)
################################################################################

Mapping = {
	'C++ Filter'        : CompileFilter,
	'Library Filter'    : LibBuilder,
	'Link Filter'       : Link,
	'C++ File Type'     : CppFileType,
	'Library Packager'  : LibPackager,
	'Executable Packager': ExePackager,
}

def GetPrototype ( name ):
	return Mapping[ name ]

