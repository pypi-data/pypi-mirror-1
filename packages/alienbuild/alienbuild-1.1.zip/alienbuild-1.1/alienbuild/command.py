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
This module is a private module.

You should not need to use any functions or classes in this module.
"""

import types
import os
import color
import sys
import aliencommon
from stat import *
from subprocess import *

PrintingAlignment = 11

################################################################################
#COMMAND
################################################################################

class COMMAND:
	"""
	This class is private.
	"""

	_States = [
		'READY',
		'RUNNING',
		'DONE',
	]

	def __init__ ( self, filter, name, cmd, files, arguments, package, dependency, output, outputFilter=aliencommon.DefaultOutputFilter, addDependencyOutputsBackToPackage=None, warningsFileName=None, addOutputBackToPackage=False ):
		self.Filter           = filter
		self.Name             = name
		self.Cmd              = cmd
		self.Arguments        = arguments
		self.Dependency       = dependency
		self.OutputFilter     = outputFilter
		self.Output           = output
		self.Package          = package
		self.Files            = files
		self.Status           = 'READY'
		self.Pid              = None
		self.WarningsFileName = warningsFileName
		self.AddDependencyOutputsBackToPackage = addDependencyOutputsBackToPackage
		self.AddOutputBackToPackage            = addOutputBackToPackage

	def __str__ ( self ):
		return 'cmd: %s\n\targs: %s\n\tfiles: %s\n\tdep: %s\n\toutput filter: %s\n\toutput: %s\n\twarnings: %s' % ( self.Cmd, self.Arguments, self.Files, self.Dependency, self.OutputFilter, self.Output, str(self.WarningsFileName) )

	def Check ( self ):
		if self.AddDependencyOutputsBackToPackage:
			self.AddDependencyOutputsBackToPackage.Update( self.Package.DependencyDatabase )
			self.Package.AddInputFiles( self.AddDependencyOutputsBackToPackage.GetOutputs() )
		if self.AddOutputBackToPackage:
			self.Package.AddInputFiles( [ self.Output ] )

		result = self.Dependency.Check()
		if result:
			if not self.WarningsFileName is None:
				try:
					warnings = open( self.WarningsFileName, "rb" ).read()
					color.SetOutputColor( color.WarningColor )
					print warnings
					color.SetOutputColor()
				except IOError:
					pass

		return result

	def Execute ( self ):
		self.Status  = 'RUNNING'
		self.Pid     = None
		self.Failure = True
		self.StdOut  = ''
		self.StdErr  = ''

		try:
			self.OutputDate = os.stat( self.Output )[ST_MTIME]
		except aliencommon.StatException:
			self.OutputDate = None

		def Replace( y, x ): return y.replace( self.Package.Symbols[x].lower() + os.sep, '' )
		basename = Replace( Replace( self.Output.lower(), 'packageobj' ), 'packagebin' )

		global PrintingAlignment
		print '[%s] %s%s' % ( self.Name, ' ' * ( PrintingAlignment - len( self.Name ) ), basename )

		#make output directory if needed
		aliencommon.MakeDirectoryForFile( self.Output )
		aliencommon.MakeDirectoryForFile( self.Package.Symbols['packagebin'] + os.sep + "x" )

		#build command line
		self.Args = aliencommon.BuildCommandLine( self.Files, self.Package, self.Output, self.Arguments, self.Cmd )

		#remove old warnings file
		if self.WarningsFileName != None:
			color.DebugPrint( 'removing: %s' % self.WarningsFileName )
			try:
				os.unlink( self.WarningsFileName )
			except aliencommon.StatException:
				pass

		if type( self.Cmd ) in [ types.StringType, types.UnicodeType ]:
			#is not a function command
			try:
				color.DebugPrint( 'executing: %s' % self.Cmd )
				self.Pid = Popen( aliencommon.CmdLineToString( self.Args ), stdout=PIPE, stderr=PIPE, env=os.environ, shell=True )
				if not self.Pid:
					self.Failure = True
					self._HandleDone()
			except KeyboardInterrupt, instance:
				color.PrintError( 'Got user interput request; now exiting...' )
				self.Failure = True
				self._HandleDone()
				raise
			except Exception, instance:
				color.PrintError( 'Got exception while running Popen for command "%s"! now exiting...' % self.Cmd )
				color.PrintError( 'exception: %s' % instance )
				self.Failure = True
				self._HandleDone()

		else:
			#is a function command
			color.DebugPrint( 'executing function "%s" with arguments "%s"' % ( self.Cmd, self.Args ) )
			try:
				self.Cmd( self.Args, self )
				self.Failure = False
				self._HandleDone()
			except KeyboardInterrupt, instance:
				color.PrintError( 'Got user interput request; now exiting...' )
				raise

	def IsDoneExecuting ( self ):
		assert self.Status != 'INIT'
		if ( self.Status != 'RUNNING' ) or not self.Pid:
			return True
		else:
			result = self.Pid.poll()
			if None == result:
				self.StdOut += self.Pid.stdout.read()
				self.StdErr += self.Pid.stderr.read()
			else:
				self.Failure = 0 != result
				self._HandleDone()
			return False

	def _HandleDone ( self ):
		#print stream output handles
		try:
			if self.Pid:
				self.StdOut += self.Pid.stdout.read()
				self.StdErr += self.Pid.stderr.read()
		except AttributeError:
			pass

		warnings = self.OutputFilter( self.StdOut, self.StdErr, '[%s] ' % self.Name, self )

		if not self.WarningsFileName is None:
			if len(warnings) != 0:
				## create the .w file
				open( self.WarningsFileName, "wb" ).write( warnings )

		#handle failure
		if self.Failure:
			color.PrintWarning( 'Command "%s" failed to execute with arguments "%s"' % ( self.Cmd, self.Args ) )

			#delete the output file if it was modified
			if os.path.isfile( self.Output ):
				outputDateNow = os.stat( self.Output )[ST_MTIME]
				if self.OutputDate != outputDateNow:
					color.PrintWarning( 'Deleting output file "%s"' % self.Output )
					os.remove( self.Output )

			#exit on error
			raise aliencommon.ExitOnErrorException()
		elif self.AddDependencyOutputsBackToPackage:
			#add the outputs back to the input if they exist
			self.AddDependencyOutputsBackToPackage.Update( self.Package.DependencyDatabase )
			self.Package.AddInputFiles( self.AddDependencyOutputsBackToPackage.GetOutputs() )

		self.Status = 'DONE'

