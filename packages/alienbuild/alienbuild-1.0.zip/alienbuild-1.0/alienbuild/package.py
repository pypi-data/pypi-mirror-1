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
import symbols
import workqueue

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

	def __init__( self, Symbols, BuildFlags, FileTypes, Files, Packager=None, absolutePaths=True ):
		"""
		Construct a PACKAGE object.  

		@type  Symbols: map
		@param Symbols: A string->string mapping.  Some symbols are user defined, some are built-in. 
		Some build-in symbols are "name", "include_dirs", and "libraries".
		@type  BuildFlags: list
		@param BuildFlags: A list of build flags, i.e: ['debug', 'noprofile'].
		@type  FileTypes: list 
		@param FileTypes: A list of L{alienbuild.FILETYPE}s.  Each element defining how to handle
		a given file-type. 
		@type  Files: list
		@param Files: A list of files to be built into this package.  If the file extension is
		found in the FileTypes list it will be processed by the filters specified in the FILETYPE object.
		Otherwise, the file will be ignored.
		@type  Packager: L{alienbuild.PACKAGER}
		@param Packager: A specified packager will be run with all built objects.  Packagers usually
		include things like M{ld}, the GNU linker, or M{ar}, the binutils archiver.
		@type  absolutePaths: bool
		@param absolutePaths: If true, all output directories will be specified in absolute paths. 
		Therefore, anything that defines a symbol in its packager will be defined with an absolute path.
		"""
		self.DependencyDatabase = dependencydatabase.DEPENDENCY_DATABASE()
		self.Packager           = Packager
		self.Files              = Files
		self.FileTypes          = FileTypes
		self.Symbols            = symbols.SYMBOLS( Symbols )
		self.BuildFlags         = BuildFlags
		self.UseAbsolutePaths   = absolutePaths

		flagdir = '_'.join( self.BuildFlags ).lower()

		def SetIfNotSet ( name, value ):
			try:
				self.Symbols.Get( name )
			except ValueError:
				self.Symbols.Set( name, value )

		SetIfNotSet( 'basebin'   , self.Symbols.Get('out') + os.sep + os.path.join( 'bin', '%s' ) % flagdir + os.sep )
		SetIfNotSet( 'packagebin', self.Symbols.Get('out') + os.sep + os.path.join( 'bin', '%s' ) % flagdir + os.sep + self.Symbols.Get('name') )
		SetIfNotSet( 'baseobj'   , self.Symbols.Get('out') + os.sep + os.path.join( 'obj', '%s' ) % flagdir + os.sep )
		SetIfNotSet( 'packageobj', self.Symbols.Get('out') + os.sep + os.path.join( 'obj', '%s' ) % flagdir + os.sep + self.Symbols.Get('name') )

		#you should not define these
		#self.Symbols.Get( 'input'        )
		#self.Symbols.Get( 'output'       )
		#self.Symbols.Get( 'bin'          )
		#self.Symbols.Get( 'obj'          )

		#raise an exception if none of the following symbols are defined
		self.Symbols.Get( 'name'         )
		self.Symbols.Get( 'include_dirs' )
		self.Symbols.Get( 'exec_paths'   )
		if Packager: self.Symbols.Get( 'output_extension')

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

	def Run ( self ):
		"""
		Build this package.  AlienBuild will do the work required to figure out dependencies
		and call the appropriate filters to build this project.
		"""
		color.DebugPrint( 'command generation: package %s' % self.Symbols.Get('name') )

		self.ExtraFiles = []

		#doing this here, allows you to change things after __init__ is called
		self.GenerateMetaTable()

		self.Work = workqueue.WORKQUEUE( aliencommon.NumberOfExecuteThreads )

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
			self.Work.Execute()
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
			self.Work.Execute()
		except aliencommon.ExitOnErrorException:
			return False

		if self.Packager != None:
			#link stage
			output = self.Symbols.Get('name').lower()
			color.DebugPrint( 'linking package %s' % output )

			#build commands
			cmds = self.Packager.BuildCommandsFromInputFiles( self, resultantFiles, output )

			#finish executing commands
			self.Work.Add( cmds )
			try:
				self.Work.Execute()
			except aliencommon.ExitOnErrorException:
				return False

		#success!
		return True

