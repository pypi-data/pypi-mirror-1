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
This module won't be documented, since it won't be released in AlienBuild.
"""

import os
import shutil
import aliencommon
from filter   import FILTER
from filetype import FILETYPE
from packager import PACKAGER

################################################################################
################################################################################

DefaultCompileArguments = {
	'ARM9': [ '-marm', '-mthumb-interwork', '-quiet', '-DARM9', '-DSDK_ARM9', '-DSDK_NO_THREAD', '-Dstringify(x)=#x', ( 'debug', [ '-g3', '-DDEBUG' ] ), ( 'noopt', [ '-O0', '-fno-inline' ] ), ( 'opt', [ '-O3', '-finline -ffast-math' ] ), '-I{include}', '-o {output}', '{input}', ( 'emu', '-DEMU' ), ( 'profile', [ '-finstrument-functions', '-DPROFILE' ] ) ],

	'ARM7': [ '-marm', '-mthumb-interwork', '-quiet', '-DASM="*(short int*)-1=0; while(1){}"', '-DARM7', '-DSDK_ARM7', '-DSDK_NO_THREAD', '-Dstringify(x)=#x', '-g0', '-O3', '-I{include}', '-o {output}', '{input}' ],
}

################################################################################
#Filters
################################################################################

CppPreprocessFilter = FILTER(
	name                      = 'PREPROCESS',
	executable                = 'cc1plus.exe',
	inputExtension            = 'cpp',
	outputExtension           = 'icpp',
	commandLineOptions        = [ '-E', ( 'ARM9', DefaultCompileArguments['ARM9'] ), ( 'ARM7', DefaultCompileArguments['ARM7'] ) ],
	dependencyExtension       = 'd',
	dependencyGenerateOptions = [ '-M' ]
)

CppCompileFilter = FILTER(
	name                      = 'COMPILE',
	executable                = 'cc1plus.exe',
	inputExtension            = 'icpp',
	outputExtension           = 's',
	commandLineOptions        = [ ( 'ARM9', DefaultCompileArguments['ARM9'] ), ( 'ARM7', DefaultCompileArguments['ARM7'] ) ],
)

CPreprocessFilter = FILTER(
	name                      = 'PREPROCESS',
	executable                = 'cc1.exe',
	inputExtension            = 'c',
	outputExtension           = 'ic',
	commandLineOptions        = [ '-E', ( 'ARM9', DefaultCompileArguments['ARM9'] ), ( 'ARM7', DefaultCompileArguments['ARM7'] ) ],
	dependencyExtension       = 'd',
	dependencyGenerateOptions = [ '-M' ]
)

CCompileFilter = FILTER(
	name                      = 'COMPILE',
	executable                = 'cc1.exe',
	inputExtension            = 'ic',
	outputExtension           = 's',
	commandLineOptions        = [ ( 'ARM9', DefaultCompileArguments['ARM9'] ), ( 'ARM7', DefaultCompileArguments['ARM7'] ) ]
)

Crt0CompileFilter = FILTER(
	name                      = 'COMPILE',
	executable                = 'cc1.exe',
	inputExtension            = 'ic',
	outputExtension           = 's',
	commandLineOptions        = [ ( 'ARM9', DefaultCompileArguments['ARM9'] ), ( 'ARM7', [ arg for arg in DefaultCompileArguments['ARM7'] if arg != '-O3' ] ) ]
)

AsmFilter = FILTER(
	name                      = 'ASM',
	executable                = 'as.exe',
	inputExtension            = 's',
	outputExtension           = 'o',
	commandLineOptions        = [ '-o', '{output}', '{input}' ]
)

LibBuilder = FILTER(
	name                      = 'AR',
	executable                = 'ar.exe',
	inputExtension            = 'o',
	outputExtension           = 'lib',
	commandLineOptions        = [ 'rc', '{output}', '{input}' ],
	options                   = { 'IsFinal':True, 'AddToGlobalSymbols': True }
)

Ld = FILTER(
	name                      = 'LINK',
	executable                = 'ld.exe',
	inputExtension            = 'o',
	outputExtension           = 'elf',
	commandLineOptions        = [
#TODO: replace all of these libraries that are grouped with something else!
		( 'ARM9', [ '-o', '{output}', '{input}', '{crt0-arm9.o}', '{libgame.lib}', '{libfat.lib}', '--start-group', '{prebuilt_libs_dir}\\sdk\\lib\\libgcc.a', '{prebuilt_libs_dir}\\sdk\\lib\\libc.a', '{prebuilt_libs_dir}\\sdk\\lib\\libsysbase.a', '{prebuilt_libs_dir}\\sdk\\lib\\libg.a', '{prebuilt_libs_dir}\\sdk\\lib\\libnosys.a', '{prebuilt_libs_dir}\\sdk\\lib\\libstdc++.a', '--end-group', '--start-group', '{libraries}', '--end-group', '-T', '{prebuilt_libs_dir}\\sdk\\lib\\arm9\\app.cmd', '-e', '_start' ] ),
		( 'ARM7', [ '-o', '{output}', '{input}', '{crt0-arm7.o}', '--start-group', '{prebuilt_libs_dir}\\sdk\\lib\\libgcc.a', '--end-group', '--start-group', '{prebuilt_libs_dir}\\sdk\\lib\\libgcc.a', '{prebuilt_libs_dir}\\sdk\\lib\\libg.a', '{prebuilt_libs_dir}\\sdk\\lib\\libnosys.a', '{libraries}', '--end-group', '-T', '{prebuilt_libs_dir}\\sdk\\lib\\arm7\\app.cmd', '-e', '_start' ] )
	],
#TODO: replace all of these libraries that are grouped with something else!
	externalDependencies      = [
		( 'ARM9', [ '{crt0-arm9.o}', '{libgame.lib}', '{libfat.lib}', '{prebuilt_libs_dir}\\sdk\\lib\\libgcc.a', '{prebuilt_libs_dir}\\sdk\\lib\\libc.a', '{prebuilt_libs_dir}\\sdk\\lib\\libsysbase.a', '{prebuilt_libs_dir}\\sdk\\lib\\libnosys.a', '{prebuilt_libs_dir}\\sdk\\lib\\libstdc++.a', '{libraries}' ] ),
		( 'ARM7', [ '{crt0-arm7.o}', '{prebuilt_libs_dir}\\sdk\\lib\\libgcc.a', '{prebuilt_libs_dir}\\sdk\\lib\\libnosys.a', '{prebuilt_libs_dir}\\sdk\\lib\\libg.a', '{libraries}' ] )
	]
)

ObjCopy = FILTER(
	name                      = 'OBJCOPY',
	executable                = 'objcopy.exe',
	inputExtension            = 'elf',
	outputExtension           = 'bin',
	commandLineOptions        = [ '-O', 'binary', '{input}', '{output}' ],
	options                   = { 'IsFinal':True }
)

RomObjCopy = FILTER(
	name                      = 'OBJCOPY',
	executable                = 'objcopy.exe',
	inputExtension            = 'elf',
	outputExtension           = 'bin',
	commandLineOptions        = [ '-O', 'binary', '{input}', '{output}' ],
	options                   = { 'IsFinal':True, 'AddToGlobalSymbols':False }
)

NdsTool = FILTER(
	name                      = 'NDSTOOL',
	executable                = 'ndstool.exe',
	inputExtension            = 'bin',
	outputExtension           = 'nds',
	commandLineOptions        = [ '-g', 'AL2P', '-9', '{input}', '-7', '{arm7.bin}', '-e7', '0x037f8000', '-d', '{databin}', '-c', '{output}' ],
	externalDependencies      = [ '{databin}', '{arm7.bin}' ],
	outputFilter              = aliencommon.OutputFilter_IgnoreAll,
	options                   = { 'IsFinal':True }
)

DemoNdsTool = FILTER(
	name                      = 'NDSTOOL',
	executable                = 'ndstool.exe',
	inputExtension            = 'bin',
	outputExtension           = 'nds',
	commandLineOptions        = [ '-g', 'AL2P', '-9', '{input}', '-7', '{arm7.bin}', '-e7', '0x037f8000', '-c', '{output}' ],
	externalDependencies      = [ '{arm7.bin}' ],
	outputFilter              = aliencommon.OutputFilter_IgnoreAll,
	options                   = { 'IsFinal':True }
)

DldiTool = FILTER(
	name                      = 'DLDITOOL',
	executable                = 'dlditool.exe',
	inputExtension            = 'nds',
	outputExtension           = 'nds',
#TODO: replace this hard coded libname
	commandLineOptions        = [ '{prebuilt_libs_dir}\\sdk\\lib\\r4tf.dldi', '{input}' ],
	options                   = { 'IsFinal':True }
)

CopyCrt0 = FILTER(
	name                      = 'COPY',
	executable                = lambda args: shutil.copyfile( args[ 0 ], args[ 1 ] ),
	inputExtension            = 'o',
	outputExtension           = 'o',
	commandLineOptions        = [ '{input}', '{output}' ],
	options                   = { 'AddToGlobalSymbols':True }
)

def RdfHeaderFilterExecutable( args ):
	from libgame.tools import buildrdfheader
	import libgame.tools.toollib
	xmldict = libgame.tools.toollib.ReadXmlFile( args[0] )
	#TODO: make this process all children not just the first 'resource' it finds
	buildrdfheader.BuildRdfHeader( xmldict['children'][0], args[1] )

################################################################################
#filetypes
################################################################################

CppFileType = FILETYPE(
	extension  = 'cpp',
	filterList = [ CppPreprocessFilter, CppCompileFilter, AsmFilter ]
)

CFileType = FILETYPE(
	extension  = 'c',
	filterList = [ CPreprocessFilter, CCompileFilter, AsmFilter ]
)

Crt0FileType = FILETYPE(
	extension  = 'c',
	filterList = [ Crt0CompileFilter, AsmFilter ]
)

AsmFileType = FILETYPE(
	extension  = 's',
	filterList = [ AsmFilter ]
)

################################################################################
#packagers
################################################################################

LibPackager = PACKAGER(
	name        = 'Library Builder',
	filterList  = [ LibBuilder ]
)

RomPackager = {
	'ARM9': PACKAGER(
		name        = 'Rom Builder',
		filterList  = [ Ld, ObjCopy, NdsTool ]
	),
	'ARM7': PACKAGER(
		name        = 'Rom Builder',
		filterList  = [ Ld, RomObjCopy ]
	)
}
if not '1' == os.getenv("EMU"): RomPackager['ARM9'].FilterList.append( DldiTool )

DemoRomPackager = PACKAGER(
	name        = 'Demo Rom Builder',
	filterList  = [ Ld, ObjCopy, DemoNdsTool ]
)
if not '1' == os.getenv("EMU"): DemoRomPackager.FilterList.append( DldiTool )

Crt0Packager = PACKAGER(
	name        = 'Crt0 Builder',
	filterList  = [ CopyCrt0 ]
)

