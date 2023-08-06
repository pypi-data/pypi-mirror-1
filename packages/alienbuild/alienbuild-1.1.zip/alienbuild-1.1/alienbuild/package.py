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
import dependencydatabase
import os
import types
import workqueue

################################################################################
#PACKAGE_REGISTRY
################################################################################

class PACKAGE_REGISTRY:
	def __init__ ( self ):
		self.Registry = {}

	def AddByName ( self, name, package ):
		if self.Registry.has_key( name ):
			assert self.Registry[name] is package
		else:
			self.Registry[name] = package

	def GetByName ( self, name ):
		return self.Registry[name]

	def BuildPackageWithDependencies ( self, name, built ):
		if not self.Registry.has_key( name ):
			color.PrintError( 'package "%s" does not exist!' % name )
			return False

		p = self.Registry[name]
		for i in p.DependentPackages:
			assert i != name, 'circular dependency detected!!'
			if not self.BuildPackageWithDependencies( i, built ):
				return False

		if name not in built:
			if p.Run():
				color.PrintInfo( '[%s done]' % p.Name )
				built.append( p.Name )
			else:
				return False

		return True

	def BuildAll ( self ):
		built = []
		todo = self.Registry.keys()
		todo.sort()
		for p in todo:
			if not self.BuildPackageWithDependencies( p, built ):
				return False
		return True

Registry = PACKAGE_REGISTRY()

################################################################################
#PACKAGE
################################################################################

class PACKAGE:
	"""The PACKAGE object defines everything related to a final target in your
	build.  For example, a package that builds a single file would look like::

		simplePackage = PACKAGE( 
			Symbols    = {},
			BuildFlags = [],
			FileTypes  = [ CFileType ],
			Files      = [ "hello.c" ]
		)

	And finally issuing a package for build::

		simplePackage.Do()
	"""

	def __init__( self, symbols, buildFlags, fileTypes, files, packagers=[], absolutePaths=True, name='UNKNOWN', dependentPackages=[] ):
		"""
		Construct a PACKAGE object.  

		@type  symbols: map
		@param symbols: A string to string or list mapping.  Some symbols are user defined, some are built-in. 
		Some build-in symbols are "name", "include_dirs", and "libraries".
		@type  buildFlags: list
		@param buildFlags: A list of build flags, i.e: ['debug', 'noprofile'].
		@type  fileTypes: list 
		@param fileTypes: A list of L{alienbuild.FILETYPE}s.  Each element defining how to handle
		a given file-type. 
		@type  files: list
		@param files: A list of files to be built into this package.  If the file extension is
		found in the FileTypes list it will be processed by the filters specified in the FILETYPE object.
		Otherwise, the file will be ignored.
		@type  packagers: L{alienbuild.PACKAGER} (or a list of them)
		@param packagers: A specified packagers will be run with all built objects.  Packagers usually
		include things like M{ld}, the GNU linker, or M{ar}, the binutils archiver.
		@type  absolutePaths: bool
		@param absolutePaths: If true, all output directories will be specified in absolute paths. 
		Therefore, anything that defines a symbol in its packagers will be defined with an absolute path.
		"""
		self.Name               = name
		self.DependencyDatabase = dependencydatabase.DEPENDENCY_DATABASE()
		self.Packagers          = packagers
		self.Files              = files
		self.FileTypes          = fileTypes
		self.Symbols            = symbols
		self.BuildFlags         = buildFlags
		self.UseAbsolutePaths   = absolutePaths
		self.DependentPackages  = dependentPackages

		flagdir = '_'.join( self.BuildFlags ).lower()

		def SetIfNotSet ( name, value ):
			if not self.Symbols.has_key( name ):
				self.Symbols[name] = value

		SetIfNotSet( 'basebin'   , os.sep.join( [ self.Symbols['out'], 'bin', flagdir, '' ] ) )
		SetIfNotSet( 'packagebin', os.sep.join( [ self.Symbols['out'], 'bin', flagdir, '', self.Symbols['name'] ] ) )
		SetIfNotSet( 'baseobj'   , os.sep.join( [ self.Symbols['out'], 'obj', flagdir, '' ] ) )
		SetIfNotSet( 'packageobj', os.sep.join( [ self.Symbols['out'], 'obj', flagdir, '', self.Symbols['name'] ] ) )
		self.Symbols['outputs'] = {}

		#you should not define these
		assert not self.Symbols.has_key( 'input'  )
		assert not self.Symbols.has_key( 'output' )
		assert not self.Symbols.has_key( 'bin'    )
		assert not self.Symbols.has_key( 'obj'    )

		#raise an exception if none of the following symbols are defined
		self.Symbols['name']
		self.Symbols['include_dirs']
		self.Symbols['exec_paths']
		if self.Packagers:
			self.Symbols['output_extension']

		Registry.AddByName( self.Symbols['name'], self )

	def GenerateMetaTable ( self ):
		"""Private"""
		#generate metatable
		import metatable
		self.MetaTable = metatable.METATABLE( self )
		self.MetaTable.BuildFromSymbols( file )

	def GetMetaTable ( self ):
		"""Private"""
		return self.MetaTable

	def AddInputFiles ( self, files ):
		"""Private"""
		if files:
			for f in files:
				self.ExtraFiles.append( f )

	def Run ( self, debug=False, levels=None ):
		"""
		Build this package.  AlienBuild will do the work required to figure out dependencies
		and call the appropriate filters to build this project.

		@type debug: bool
		@var debug: When set to true, debugging information will be displayed when
		building.
		@type levels: map
		@var levels: When Debug is enabled, all debug information displayed is filtered
		by this debug levels there are keywords for the different debug info types,
		specify None for all debug info.
		"""

		def InjectList( name ):
			self.Symbols[name] += [ x for x in d.Symbols[name] if x not in self.Symbols[name] ]

		#inject vars from other dependent packages
		for dn in self.DependentPackages:
			d = Registry.GetByName( dn )

			#inject outputs from other dependent packages
			for k,v in d.Symbols['outputs'].iteritems():
				self.Symbols[k] = v

			#inject include_dirs from other dependent packages
			InjectList( 'include_dirs' )

			#inject force_includes from other dependent packages
			InjectList( 'force_includes' )

		color.Debug  = debug
		color.Levels = levels

		color.DebugPrint( 'command generation: package %s' % self.Symbols['name'] )

		self.ExtraFiles = []

		#doing this here allows you to change things after __init__ is called
		self.GenerateMetaTable()

		self.Work = workqueue.WORKQUEUE( aliencommon.NumberOfExecuteThreads )

		builtAnything = False

		#build up all of the commands in the package and add them to the work queue
		resultantFiles = []
		for file in self.Files:
			for type in self.FileTypes:
				if True == type.Match( file ):
					( commands, final ) = type.BuildCommandsFromInputFile( self, file )
					if final:
						resultantFiles.append( final )
					self.Work.Add( commands )
					break
			else:
				raise NameError, 'Did not find filetype for package file "%s"' % file

		#wait on the work queue to finish
		try:
			result = self.Work.Execute()
			builtAnything = builtAnything or result
		except aliencommon.ExitOnErrorException:
			return False

		#now execute all the extra files
		for file in self.ExtraFiles:
			for type in self.FileTypes:
				if True == type.Match( file ):
					( commands, final )= type.BuildCommandsFromInputFile( self, file )
					resultantFiles.append( final )
					self.Work.Add( commands )
					break
			else:
				#if we didnt process this file, then it goes in the packager
				resultantFiles.append( file )

		#wait on the work queue to finish
		try:
			result = self.Work.Execute()
			builtAnything = builtAnything or result
		except aliencommon.ExitOnErrorException:
			return False

		for packager in self.Packagers:
			#link stage
			output = self.Symbols['name'].lower()
			color.DebugPrint( 'linking package %s' % output )

			#build commands
			( cmds, final ) = packager.BuildCommandsFromInputFiles( self, resultantFiles, output )

			#finish executing commands
			self.Work.Add( cmds )
			try:
				result = self.Work.Execute()
				builtAnything = builtAnything or result
			except aliencommon.ExitOnErrorException:
				return False

			#add output back to inputs if it matches a filetype
			if aliencommon.DoesFileMatchAFileType( self.FileTypes, final ):
				( commands, final ) = type.BuildCommandsFromInputFile( self, final )
				resultantFiles.append( final )
				self.Work.Add( commands )

				#wait on the work queue to finish
				try:
					result = self.Work.Execute()
					builtAnything = builtAnything or result
				except aliencommon.ExitOnErrorException:
					return False

		name = self.Symbols['name']

		#success!
		return True

