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
import shutil
import stat
import subprocess

################################################################################
################################################################################

DefaultCompileArguments = [
	'/D{defines}',
	( 'debug', [ '' ] ),
	'/Zi',
	( 'noopt', [ '' ] ),
	( 'opt', [ '' ] ),
	'/I"{include}"',
	( 'profile', [ '/DPROFILE' ] ),
	'/wd4530',
	'/Fd{pdb}',
	'{input}',
	'/Fo{output}',
]

################################################################################
################################################################################

def MicrosoftOutputFilter ( standardOut, standardError, header ):
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

################################################################################
#Filters
################################################################################

def ClDependencyGenerator ( args, cmd ):
	"""
	This Function will generate dependencies for a C style preprocessed file using Microsoft's CL.exe.
	"""
	output = args[-1].replace('/Fo','')
	input  = args[-2]

	#run cl to get c preprocessed output
	stdOut = ''
	stdErr = ''
	args = args[:-1]
	pid = subprocess.Popen( aliencommon.CmdLineToString( ['cl.exe'] + args ), stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ, shell=True )

	result = None
	while result == None:
		result = pid.poll()
		if not result:
			stdOut += pid.stdout.read()
			stdErr += pid.stderr.read()
		else:
			if result != 0:
				color.PrintError( stdErr )
				raise NameError( 'ClDependencyGenerator failed!' )
			stdOut += pid.stdout.read()
			stdErr += pid.stderr.read()

	#strip #line's from the preprocessed output
	lines = []
	for i in re.compile( '#line .*"(.*)"', re.MULTILINE ).findall( stdOut, re.MULTILINE ):
		if i not in lines:
			lines.append( i )

	#write pp file
	file( output + '.pp', 'wb' ).write( stdOut )

	#write the dependency file
	o = file( output, 'wb' )
	o.write( '"%s" : "%s"' % ( input.replace('\\','\\\\').replace(':','\\:'), input.replace(':','\\:').replace(' ','__SpAcE__') ) )
	for i in lines:
		o.write( '\\\n\t"%s"' % i.replace(':','\\:').replace(' ','__SpAcE__') )

CompileFilter = FILTER(
	name                      = 'COMPILE',
	executable                = 'cl.exe',
	inputExtension            = 'cpp',
	outputExtension           = 'o',
	commandLineOptions        = [ '/c' ] + DefaultCompileArguments,
	options                   = { 'IsFinal':False },
	dependencyGenerator       = ClDependencyGenerator,
	dependencyExtension       = 'd',
	dependencyGenerateOptions = [ '/E' ],
	outputFilter              = MicrosoftOutputFilter,
)

LibBuilder = FILTER(
	name                      = 'LIB',
	executable                = 'lib.exe',
	inputExtension            = 'o',
	outputExtension           = 'lib',
	commandLineOptions        = [ '/SUBSYSTEM:WINDOWS', '/OUT:{output}', '/LIBPATH:"{library_paths}"', '{input}', '{libraries}' ],
	options                   = { 'IsFinal':True, 'AddToGlobalSymbols': True },
	outputFilter              = MicrosoftOutputFilter,
)

DllBuilder = FILTER(
	name                      = 'DLL',
	executable                = 'link.exe',
	inputExtension            = 'o',
	outputExtension           = 'dll',
	commandLineOptions        = [ ( 'DEBUG', '/DEBUG' ), '/DLL', '/OUT:{output}', '/LIBPATH:"{library_paths}"', '{input}', '{libraries}' ],
	options                   = { 'IsFinal':True, 'AddToGlobalSymbols': True },
	outputFilter              = MicrosoftOutputFilter,
)

PydBuilder = FILTER(
	name                      = 'PYD',
	executable                = 'link.exe',
	inputExtension            = 'o',
	outputExtension           = 'pyd',
	commandLineOptions        = [ ( 'DEBUG', '/DEBUG' ), '/DLL', '/OUT:{output}', '/LIBPATH:"{library_paths}"', '{input}', '{libraries}' ],
	options                   = { 'IsFinal':True, 'AddToGlobalSymbols': True },
	outputFilter              = MicrosoftOutputFilter,
)

Link = FILTER(
	name                      = 'LINK',
	executable                = 'link.exe',
	inputExtension            = 'o',
	outputExtension           = 'exe',
	commandLineOptions        = [ '/DEBUG', '/SUBSYSTEM:WINDOWS', '/PDB:{pdb}', '/OUT:{output}', '/LIBPATH:"{library_paths}"', '{input}' ],
	options                   = { 'IsFinal':True },
	outputFilter              = MicrosoftOutputFilter,
)

################################################################################
#filetypes
################################################################################

CppFileType = FILETYPE(
	extension  = 'cpp',
	filterList = [ CompileFilter ]
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

