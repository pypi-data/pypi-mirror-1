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

"""This is a private module."""

import command
import Queue
import aliencommon
import ctypes

################################################################################
#WORKQUEUE
################################################################################

class WORKQUEUE:
	"""This is a private class.
	
	A queue that holds work to be executed
	you can remove work from this queue in a thread safe manor using the Remove function
	"""

	def __init__ ( self, maxNumThreads=4 ):
		self.Work          = []
		self.Executing     = []
		self.MaxNumThreads = maxNumThreads

	def Add ( self, cmdList ):
		self.Work.append( cmdList )

	def Execute ( self ):
		#dep check all
		work = []
		for i in self.Work:
			l = [ c for c in i if not c.Check() ]
			if l: work.append( l )
		self.Work = work

		#check for nothing to build
		if not self.Work:
			return False

		#execute all work
		while self.Work:
			if len( self.Executing ) < self.MaxNumThreads:
				cl = self.Work.pop()
				cl[0].Execute()
				self.Executing.append( cl )

			self._CheckForDoneExecuting()

		while self.Executing:
			self._CheckForDoneExecuting()

		assert not self.Work
		assert not self.Executing

		return True

	def _CheckForDoneExecuting ( self ):
		for i in xrange( len( self.Executing ) ):
			if self.Executing[i][0].IsDoneExecuting():
				del self.Executing[i][0]
				if self.Executing[i]:
					self.Executing[i][0].Execute()
				else:
					del self.Executing[i]
				break

