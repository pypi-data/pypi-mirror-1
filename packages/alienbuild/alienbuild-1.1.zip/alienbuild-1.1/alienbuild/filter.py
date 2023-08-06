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

import aliencommon
import color
import os
import command
from types import *
from subprocess import *
from stat import *

################################################################################
#FILTER
################################################################################

DefaultFilterOptions = {
	'IsFinal'  : False,
	'IsOutput' : False,
}

class FILTER:
	"""
	The FILTER object defines how to handle an input and produce an output.  For example,
	calling gcc on an input C file and producing an object file should be done via a FILTER.
	Example::

		CCompileFilter = alienbuild.FILTER(
			name                      = "C_COMPPILE",
			executable                = "gcc",
			inputExtension            = "c",
			outputExtension           = "o",
			commandLineOptions        = [ "-Wall", "-ansi", "-o {output}", "-c", "{input}" ],
			dependencyExtension       = "d",
			dependencyGenerateOptions = [ "-M" ],
		)
	
	When used in a L{alienbuild.FILETYPE}, this filter will run on any file in the L{alienbuild.PACKAGE} 
	matching the given extension.
	"""

	DependencyStylesSupported = [ 'MAKE', 'ALIENBUILD' ]

	def __init__ ( self, name, executable, inputExtension=None, outputExtension=None, commandLineOptions=[], externalDependencies=[], dependencyGenerator=None, dependencyExtension=None, dependencyGenerateOptions=[], dependencyStyle='MAKE', outputFilter=aliencommon.DefaultOutputFilter, options={}, warningsExtension='w', addOutputBackToPackage=False ):
		"""
		Construct a FILTER object.  A FILTER is capable of executing an external command or calling a python function.
		Simply pass a string or a Python function as the M{executable} argument.

		@type  name: string
		@param name: The name of the filter.  The name is printed on a line with the given output file name. I.e::
			[CCOMPILE]     hello.o
		@type  executable: string or function
		@param executable: The name of the executable.  If the given executable cannot be found, alienbuild will search the directories
		listed in a project's given exec_path symbol.  if the given executable is a Python function the function will be called with 
		a single argument 'args'::
			def CopyFile( args ):
				shutil.copyfile( args[ 0 ], args[ 1 ] )
			copyFilter = alienbuild.FILTER( name="COPY", executable=CopyFile, commandLineOptions=['{input}', '{output}'] )
		@type  inputExtension: string or list of strings
		@param inputExtension: The extension or extensions (without the period '.') of the input files this filter handles.  I.e. "c" For C files, and "cpp" for C++.
		@type  outputExtension: string
		@param outputExtension: The extension (without the period '.') of the output file this filter produces. I.e. "o" or "obj" for object files.
		@type  commandLineOptions: list of strings
		@param commandLineOptions: This parameter is used to construct the command line given to the executable. Symbols in curly braces are replaced
		using the package's symbol table and any on-the-fly symbols.  See L{symbols} for built in symbol list.
		@type  externalDependencies: list of strings
		@param externalDependencies: A list of strings representing files that this filter depends on.  For example, a link filter
		may depend on external libraries.
		@type  dependencyGenerator: string or function
		@param dependencyGenerator: An executable used to generate dependencies on the input to this filter.  If dependencyGenerator is not used
		and dependencyExtension is specified, dependencyGenerator defaults to M{executable}.
		@type  dependencyGenerateOptions: list of strings
		@param dependencyGenerateOptions: A set of command line options that are passed to the dependency generator.
		@type  dependencyStyle: string
		@param dependencyStyle: ???
		@type  outputFilter: function
		@param outputFilter: All text print to stdout and stderr are first filtered through the given function.
		@type  options: map
		@param options: Various options controlling the filter. If set, "IsFinal" will cause the use of the "bin" directory as output, instead of the "obj" output directory.
		@type  warningsExtension: string or None
		@param warningsExtension: If None, warnings are not printed every time the filter is processed.  Otherwise, this specifies the output extension on disk for the warnings file.
		"""
		assert dependencyStyle in self.DependencyStylesSupported

		self.Name                      = name
		self.Executable                = executable
		if type( inputExtension ) == StringType or type( inputExtension ) == UnicodeType:
			self.InputExtension    = [ inputExtension ]
		else:
			self.InputExtension    = inputExtension
		self.OutputExtension           = outputExtension
		self.CommandLineOptions        = commandLineOptions
		self.ExternalDependencies      = externalDependencies
		if dependencyExtension and not dependencyGenerator:
			self.DependencyGenerator = self.Executable
		else:
			self.DependencyGenerator = dependencyGenerator
		self.DependencyExtension       = dependencyExtension
		self.DependencyGenerateOptions = dependencyGenerateOptions
		self.DependencyStyle           = dependencyStyle
		self.OutputFilter              = outputFilter
		self.Options                   = {}
		for i in DefaultFilterOptions.iteritems():
			self.Options[i[0]] = i[1]
		for i in options.iteritems():
			self.Options[i[0]] = i[1]
		self.WarningsExtension         = warningsExtension
		self.AddOutputBackToPackage    = addOutputBackToPackage

	def __str__( self ):
		s  = "FILTER(\n" 
		s += "\tname = \"%s\",\n" % self.Name
		if type(self.Executable) == type(""):
			s += "\texecutable = \"%s\",\n" % self.Executable
		else:
			s += "\texecutable = %s,\n" % self.Executable
		s += "\tInputExtension = \"%s\",\n" % self.InputExtension
		s += "\tOutputExtension = \"%s\",\n" % self.OutputExtension
		s += "\tCommandLineOptions = %s,\n" % (str(self.CommandLineOptions))
		s += "\tWarningsExtensino = %s,\n" % str(self.WarningsExtension)
		s += ")"
		return s

	def __repr__( self ): 
		return self.__str__()

	def IsFunctionFilter ( self ):
		"""Private"""
		return not ( ( StringType == type( self.Executable ) ) or ( UnicodeType == type( self.Executable ) ) )

	def Match ( self, file ):
		"""Private"""
		for ext in self.InputExtension:
			if file.endswith( '.' + ext ): return True
		return False

	def GetOutputFileBaseName( self, package, file, alwaysObj=False ):
		"""Private"""
		def Get( x ): return package.Symbols[x].lower() + os.sep

		file = file.lower()
		file = file.replace( Get('packagebin'), '' )
		file = file.replace( Get('packageobj'), '' )
		for ext in self.InputExtension:
			file = file.replace( '.' + ext, '' )
		file = file.replace( '.' + self.OutputExtension, '' )
		try:
			file = file.replace( Get('sourcebase'), '' )
		except ValueError:
			pass #only replace if sourcebase exists
		if not alwaysObj and self.Options['IsFinal']:
			out = Get('packagebin') + file
		else:
			out = Get('packageobj') + file
		return out

	def GetOutputName ( self, package, file ):
		"""Private"""
		file = self.GetOutputFileBaseName( package, file )
		file = file.replace( '.' + self.OutputExtension, '' )
		file = file + '.' + self.OutputExtension
		return file

	def GetDependencyName ( self, package, file ):
		"""Private"""
		if not self.DependencyGenerator:
			raise ValueError( 'this filter does not have dependencies' )

		file = self.GetOutputFileBaseName( package, file, alwaysObj=True )
		file = file + '.' + self.OutputExtension + '.' + self.DependencyExtension
		return file

	def GetWarningsName ( self, package, file, isDependency=False ):
		"""Private"""
		if self.WarningsExtension == None:
			return None

		file = self.GetOutputFileBaseName( package, file, alwaysObj=True )
		if isDependency:
			file = file + '.' + self.OutputExtension + '.' + self.DependencyExtension + '.' + self.WarningsExtension
		else:
			file = file + '.' + self.OutputExtension + '.' + self.WarningsExtension
		return file

	def BuildCommandsFromInputFile ( self, package, file, outputname=None ):
		"""Private"""
		commands = []
		dd = package.DependencyDatabase

		#find output filename
		if outputname:
			output = self.GetOutputName( package, outputname )
		else:
			output = self.GetOutputName( package, file )

		#add to package outputs
		outputSymbolName = output[output.rfind(os.sep)+1:]
		if self.Options['IsOutput'] and ( outputSymbolName not in package.Symbols['outputs'] ):
			package.Symbols['outputs'][outputSymbolName] = output

		#generate final dependency
		dependency = dd.AddByPath( output )

		#if filter has dependencies add the dependency file and the command needed to build it
		if self.DependencyGenerator:
			if type( file ) == ListType:
				outputDependency = self.GetDependencyName( package, output )
				warningsName = self.GetWarningsName( package, output, isDependency=True )
			else:
				outputDependency = self.GetDependencyName( package, file )
				warningsName = self.GetWarningsName( package, file, isDependency=True )

			if self.DependencyStyle == 'ALIENBUILD':
				d = dd.AddDependencyFile( outputDependency )
			else:
				assert self.DependencyStyle == 'MAKE'
				d = dd.AddMakeStyleDependencyFile( outputDependency )
			dependency.AddDependency( d )
			dcmd = command.COMMAND( self, 'DEPENDENCY', self.DependencyGenerator, file, self.DependencyGenerateOptions + self.CommandLineOptions, package, d, outputDependency, self.OutputFilter, warningsFileName=warningsName )
			commands.append( dcmd )
		else:
			for i in package.GetMetaTable().ReplaceSymbolsInList( file ):
				dependency.AddDependency( dd.AddByPath( i ) )

		#add all external dependencies as new dependencies
		for i in package.GetMetaTable().ReplaceSymbolsInList( self.ExternalDependencies ):
			dependency.AddDependency( dd.AddByPath( i ) )

		#TODO: figure out a proper place to put this...
		#add any {libraries} as new dependencies
		for i in [ x for x in package.GetMetaTable().ReplaceSymbolsInList( package.Symbols['libraries'] ) if -1 != x.find(':') or x.startswith('/') ]:
			dependency.AddDependency( dd.AddByPath( i ) )

		#build the command
		if self.DependencyStyle == 'ALIENBUILD':
			warningsName = self.GetWarningsName( package, output )
			ccmd = command.COMMAND( self, self.Name, self.Executable, file, self.CommandLineOptions, package, dependency, output, self.OutputFilter, addDependencyOutputsBackToPackage=d, warningsFileName=warningsName )
		else:
			assert self.DependencyStyle == 'MAKE'
			warningsName = self.GetWarningsName( package, output )
			ccmd = command.COMMAND( self, self.Name, self.Executable, file, self.CommandLineOptions, package, dependency, output, self.OutputFilter, warningsFileName=warningsName, addOutputBackToPackage=self.AddOutputBackToPackage )
		commands.append( ccmd )

		return commands

