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

import os, sys
import aliencommon
import color
from stat import *
import pickle

################################################################################
################################################################################

def debug ( this, i, msg, level='dependency' ):
	if not color.IsDebug( level ): return

	mapping = {
		'self.Path'   : this.Path,
		'self.Type'   : this.Type,
		'self.Result' : this.Result,
	}
	if i:
		mapping['i.Path']      = i.Path
		mapping['i.Type']      = i.Type
		mapping['i.Result']    = i.Result
	else:
		mapping['i.Path']      = 'None'
		mapping['i.Type']      = 'None'
		mapping['i.Result']    = 'None'

	color.DebugPrint( msg % mapping, level )

################################################################################
#DEPENDENCY_FILE
################################################################################

class DEPENDENCY_FILE:
	def __init__ ( self, path, targets, dependencies, type, outputs=None ):
		assert type in DEPENDENCY.SupportedTypes
		self.Path         = path
		self.Targets      = targets
		self.Dependencies = dependencies
		self.Type         = type
		self.Outputs      = outputs

	def Save ( self ):
		import pickle
		pickle.Pickler( open( self.Path, 'wb' ) ).dump( self )

################################################################################
#DEPENDENCY
################################################################################

class DEPENDENCY:
	'''one dependency
	each dependency has a list of dependencies that it depends upon
	and a list of targets that depend upon this
	this makes a DEPENDENCY object into one node of a dependency graph

	you dont have to call both AddTarget and AddDependency to add a graph node linked in both directions
	both AddTarget and AddDependency link them bidirectionally, both are included as it's easier to use
	sone or the other in a certain situation

	you should use the DEPENDENCYDATABASE to manage collection and creation of these

	there can also be empty dependencies;
	an empty dependency doesnt check the path that it points to, only it's children
	two usages of this is a make style dependency file, and a directory
	an empty dependency will use the time stamp from it's parent node, which is what makes it cool
	'''

	SupportedTypes = [ 
		'TIMESTAMP',
		'EXISTS',
		'NONE',
	]

	########################################################################
	########################################################################

	def __init__ ( self, path, osstat, type='TIMESTAMP', outputs=None ):
		assert type in self.SupportedTypes
		self.Path         = path
		self.Targets      = {}
		self.Dependencies = {}
		self.Stat         = osstat
		self.Type         = type
		self.Result       = 'UNCHECKED'
		self.Outputs      = outputs
		self.Exists       = None
		self.OldestChild  = None

	def __str__ ( self ):
		return 'dependency: %s\n\tresult: %s\n\ttargets: %s\n\tdependencies: %s\n\ttype: %s\n\tstat: %s\n\toldestChild: %s' % ( self.Path, self.Result, self.Targets, self.Dependencies, self.Type, self.Stat, self.OldestChild )

	########################################################################
	########################################################################

	def AddTarget ( self, target ):
		self.Targets[target.Path]      = target
		target.Dependencies[self.Path] = self

	def AddDependency ( self, dependency ):
		self.Dependencies[dependency.Path] = dependency
		dependency.Targets[self.Path]      = self

	########################################################################
	#Check
	########################################################################

	def Check ( self, parentStat=None, parentPath=None ):
		assert self.Result in [ 'UNCHECKED', 'FAILED', 'SUCCESS', 'EMPTY' ]
		if self.Type == 'TIMESTAMP':
			newer     = self.Stat
			newerPath = self.Path
		else:
			newer     = parentStat
			newerPath = parentPath
			assert newer, '%s' % self

		if self.Result == 'UNCHECKED':
			#check that self exists
			if self.Type != 'EMPTY' and not self.Stat:
				debug( self, None, 'dependency path:"%(self.Path)s" type:"%(self.Type)s" failed due to non-existance', None )
				self._FailMe()

			#check all child dependencies
			if self.Result != 'FAILED':
				self._CheckAllChildDependencies( newer, newerPath )

			#if we succeded then set result to proper value
			if self.Result != 'FAILED':
				if self.Type == 'TIMESTAMP':
					self.Result = 'SUCCESS'
					assert self.Stat
				else:
					self.Result = 'EMPTY'
					assert self.OldestChild or ( len( self.Dependencies ) == 0 )

		#success!
		return ( self.Result == 'SUCCESS' )

	def _FailMe ( self ):
		self.Result = 'FAILED'

		#we've failed, so mark all targets as failed
		for i in self.Targets.itervalues():
			assert i.Result == 'UNCHECKED' or i.Result == 'FAILED', 'target was "%s"' % i.Result
			if i.Result != 'FAILED':
				debug( self, i, 'target "%(i.Path)s" is failing due to "%(self.Path)s"', None )
				i.Result = 'FAILED'

	def _SetOldestChild ( self, old ):
		assert old
		if not self.OldestChild:
			self.OldestChild = old
		else:
			if old[ST_MTIME] < self.OldestChild[ST_MTIME]:
				self.OldestChild = old

	def _DoCheckAgainstSelf ( self, i, newer, newerPath ):
		assert newer, '%s' % self

		if i.Result == 'SUCCESS':
			older = i.Stat
		elif i.Result == 'EMPTY':
			older = i.OldestChild
		else:
			assert False, 'not supposed to happen; i.Result==%s' % i.Result

		if older == None:
			debug( self, i, 'dependency "' + str( newerPath ) + '" failed because "%(i.Path)s" did not exist (child)', None )
			return False
		elif newer[ST_MTIME] < older[ST_MTIME]:
			debug( self, i, 'dependency "' + str( newerPath ) + '" failed because "%(i.Path)s" is older', None )
			return False
		else:
			self._SetOldestChild( older )
			return True

	def _CheckAllChildDependencies ( self, newer, newerPath ):
		for i in self.Dependencies.itervalues():
			if i == self: continue

			if i.Result == 'UNCHECKED':
				i.Check( newer, newerPath )
				assert i.Result != 'UNCHECKED', 'this cant ever happen!, right?'

			if i.Result in [ 'SUCCESS', 'EMPTY' ]:
				#check the dependency against this
				if not self._DoCheckAgainstSelf( i, newer, newerPath ):
					debug( self, i, '\tdependency failed while checking child path:"%(i.Path)s" type:"%(i.Type)s"', None )
					self._FailMe()
					break
				continue
			elif i.Result == 'FAILED':
				debug( self, i, 'dependency failed because a child "%(i.Path)s" of "%(self.Path)s" that failed', None )
				self._FailMe()
				break
			else:
				assert False, 'invalid result type'

	########################################################################
	#uncheck
	########################################################################

	def UnCheck ( self ):
		self.Stat   = None
		self.Result = 'UNCHECKED'
		for i in self.Targets:
			i.UnCheck()

	########################################################################
	#accessors
	########################################################################

	def GetFile ( self ):
		return DEPENDENCY_FILE( self.Path, self.Targets.keys(), self.Dependencies.keys(), self.Type, self.Outputs )

	def GetOutputs ( self ):
		return self.Outputs

	########################################################################
	#update
	########################################################################

	def Update ( self, dependencyDatabase ):
		#0: read dep file
		try:
			depFile = pickle.Unpickler( file( self.Path, 'r' ) ).load()
		except IOError:
			return

		assert depFile.__class__ is DEPENDENCY_FILE

		#1: create dependency file and add data
		self.Type    = depFile.Type
		self.Outputs = depFile.Outputs

		for i in depFile.Targets:
			t = dependencyDatabase.AddByPath( i )
			self.AddTarget( t )
		for i in depFile.Dependencies:
			t = dependencyDatabase.AddByPath( i )
			self.AddDependency( t )

################################################################################
#DEPENDENCYDATABASE
################################################################################

def _Stat ( path ):
	try                             : return os.stat( path )
	except aliencommon.StatException: return None

class DEPENDENCY_DATABASE:
	'a database containing all of the DEPENDENCY objects'

	def __init__ ( self, filename=None ):
		if filename == None:
			self.Db = {}
		else:
			import pickle
			self = pickle.Unpickler( open( filename, 'rb' ) ).load()

	def Save ( self, filename ):
		import pickle
		pickle.Pickler( open( filename, 'wb' ) ).dump( self )

	def AddByPath ( self, path ):
		if not self.Db.has_key( path ):
			osstat = _Stat( path )
			if osstat and S_ISDIR( osstat[ST_MODE] ):
				#this is a directory dependency
				#add it as a empty dependency and add to that all it's children
				self.Db[path] = DEPENDENCY( path, osstat, type='EXISTS' )
				for entry in os.listdir( path ):
					if entry.startswith( '.' ): continue
					self.Db[path].AddDependency( self.AddByPath( path + os.sep + entry ) )
			else:
				#this is a normal file dependency
				self.Db[path] = DEPENDENCY( path, osstat )
		return self.Db[path]

	def AddMakeStyleDependencyFile ( self, path ):
		#0: return if exists
		if self.Db.has_key( path ):
			return self.Db[path]

		#1: read dep file
		try:
			( theMakeDepFile, deps ) = aliencommon.ReadMakeDependencyFile( path )
		except ValueError:
			color.PrintWarning( 'found invalid dependency file "%s" deleting...' % path )
			os.remove( path )
			return self.AddByPath( path )
		except IOError:
			#return a normal dependency if no file
			return self.AddByPath( path )

		#2: create dep file, and add each file as a dependency in dep file
		d = self.AddByPath( path )
		for i in deps:
			d.AddDependency( self.AddByPath( i ) )

		#3: return dep file
		return d

	def AddDependencyFile ( self, path ):
		#0: return if exists
		if self.Db.has_key( path ):
			return self.Db[path]

		#1: read dep file
		try:
			depFile = pickle.Unpickler( file( path, 'r' ) ).load()
		except IOError:
			#if the file doesnt exist just add it as a normal file
			return self.AddByPath( path )

		assert depFile.__class__ is DEPENDENCY_FILE

		#2: create dependency file and add data
		d         = self.AddByPath( depFile.Path )
		d.Type    = depFile.Type
		d.Outputs = depFile.Outputs

		for i in depFile.Targets:
			t = self.AddByPath( i )
			d.AddTarget( t )
		for i in depFile.Dependencies:
			t = self.AddByPath( i )
			d.AddDependency( t )

		return d

