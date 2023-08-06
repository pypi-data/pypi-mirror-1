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

import aliencommon
import color

################################################################################
################################################################################

def DoPackage ( package, debug=False, levels=None ):
	"""
	Issue a package for building.  Properly initializing a package and its
	L{alienbuild.FILTER}s is key to an efficient and correct build.
	
	@type  package: L{alienbuild.PACKAGE}
	@param package: Defines the package to be built.
	@type debug: bool
	@var debug: When set to true, debugging information will be displayed when
	building.
	@type levels: map
	@var levels: When Debug is enabled, all debug information displayed is filtered
	by this debug levels there are keywords for the different debug info types,
	specify None for all debug info.
	"""
	if False == aliencommon.UseShortOutput:
		color.PrintInfo( '[%s Build Start]' % package.Symbols.Get('name').upper() )
	if package.Run( debug, levels ):
		color.PrintInfo( '[%s Build Done]' % package.Symbols.Get('name').upper() )
		return True
	else:
		return False

