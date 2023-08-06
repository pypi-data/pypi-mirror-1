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
The alienbuild.color module is used to pretty-print some text in various 
colors. 
"""

import aliencommon

################################################################################
#color stuff
################################################################################

COLOR_FOREGROUND_BLUE       = 0x01
COLOR_FOREGROUND_GREEN      = 0x02
COLOR_FOREGROUND_RED        = 0x04
COLOR_FOREGROUND_INTENSITY  = 0x08
COLOR_BACKGROUND_BLUE       = 0x10
COLOR_BACKGROUND_GREEN      = 0x20
COLOR_BACKGROUND_RED        = 0x40
COLOR_BACKGROUND_INTENSITY  = 0x80
COLOR_DEFAULT               = COLOR_FOREGROUND_BLUE  | COLOR_FOREGROUND_GREEN | COLOR_FOREGROUND_RED
COLOR_FOREGROUND_YELLOW     = COLOR_FOREGROUND_GREEN | COLOR_FOREGROUND_RED
COLOR_FOREGROUND_LIGHT_BLUE = COLOR_FOREGROUND_GREEN | COLOR_FOREGROUND_BLUE
COLOR_FOREGROUND_PURPLE     = COLOR_FOREGROUND_RED   | COLOR_FOREGROUND_BLUE

import ctypes

STD_INPUT_HANDLE  = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE  = -12

if not aliencommon.IsWindows():
	std_out_handle = None
	EscapeString   = "\x1B\x5B0m"
	EndString      = "\x1B\x5B0m"
else:
	std_out_handle = ctypes.windll.kernel32.GetStdHandle( STD_OUTPUT_HANDLE )
	EscapeString   = ""
	EndString      = ""

################################################################################
################################################################################

PrintLine_FilenameOffset = 20

InfoColor    = COLOR_FOREGROUND_GREEN  | COLOR_FOREGROUND_INTENSITY
ErrorColor   = COLOR_FOREGROUND_RED    | COLOR_FOREGROUND_INTENSITY
DebugColor   = COLOR_FOREGROUND_BLUE   | COLOR_FOREGROUND_INTENSITY
WarningColor = COLOR_FOREGROUND_YELLOW | COLOR_FOREGROUND_INTENSITY

UseShortOutput = True

Debug  = False
Levels = None

################################################################################
################################################################################

def PrintLine ( toolname, filename ):
	"""
	Display a line of text prefixed by the M{toolname}.  I.e::

		[TOOLNAME]     filename
	
	The output text is printed in the color set by calling L{SetOutputColor}. Calling
	this function does not reset the output color.

	@param toolname: The [TOOLNAME] part of the output text.
	@type  toolname: string
	@param filename: the M{filename} part of the output text.
	@type  filename: string
	"""
	o = ' |%s| ' % toolname
	while len(o) < PrintLine_FilenameOffset:
		o += ' '
	print '%s%s %s%s' % ( EscapeString, o, filename, EndString )

def PrintWarning ( line ):
	"""
	Display M{line} in the warning color (Yellow).  The text will be prefixed with
	"[AlienBuild Warning]".

	The default output color will be reset.

	@type line: string
	@param line: The text to be displayed
	"""
	SetOutputColor( WarningColor )
	print '%s[AlienBuild Warning] %s%s' % ( EscapeString, line, EndString )
	SetOutputColor()

def PrintError ( line ):
	"""
	Display M{line} in the error color (Red).  The text will be prefixed with
	"[AlienBuild Error]".

	The default output color will be reset.

	@type line: string
	@param line: The text to be displayed
	"""
	SetOutputColor( ErrorColor )
	print '%s[AlienBuild Error] %s%s' % ( EscapeString, line, EndString )
	SetOutputColor()

def PrintInfo ( line ):
	"""
	Display M{line} in the info color (Green).  The text will not be prefixed.

	The default output color will be reset.

	@type line: string
	@param line: The text to be displayed
	"""
	SetOutputColor( InfoColor )
	print '%s%s%s' % ( EscapeString, line, EndString )
	SetOutputColor()

def IsDebug ( level=None ):
	if True != Debug: return False

	if ( Levels != None ) and ( level != None ):
		if level not in Levels: return False

	return True

def DebugPrint ( line, level=None ):
	"""
	Display M{line} in the debug color (Blue).  The text will be prefixed with
	"[AlienBuild Debug]".

	The default output color will be reset.

	@type line: string
	@param line: The text to be displayed
	@type level: int
	@param level: The M{line} will only be displayed if M{level} is less than L{alienbuild.aliencommon.Level} and
	L{alienbuild.aliencommon.Debug} is True.
	"""
	if not IsDebug( level ): return

	#passed checks, so print output
	SetOutputColor( DebugColor )
	print '%s[AlienBuild Debug] %s%s' % ( EscapeString, line, EndString )
	SetOutputColor()

def SetOutputColor ( color=COLOR_DEFAULT, handle=std_out_handle ) :
	"""
	Change the output color to M{color}.  The given M{handle} is only useful
	on Windows platforms.   This is mostly an internal function.

	@type  color: COLOR_* constant
	@param color: The color to change to
	@type  handle: Win32 HANDLE
	@param handle: handle to the console
	"""
	if not aliencommon.IsWindows():
		escapeString = "\x1B\x5B"

		colorToString = {
			( 0, 0, 0 ): "0",
			( 0, 0, 1 ): "4",
			( 0, 1, 0 ): "2",
			( 0, 1, 1 ): "6",
			( 1, 0, 0 ): "1",
			( 1, 0, 1 ): "5",
			( 1, 1, 0 ): "3",
			( 1, 1, 1 ): "7"
		}

		if color == COLOR_DEFAULT:
			escapeString = "0m"
		else:
	
			if ( color & COLOR_FOREGROUND_RED ) != 0  : red = 1
			else                                      : red = 0
			if ( color & COLOR_FOREGROUND_GREEN ) != 0: green = 1
			else                                      : green = 0
			if ( color & COLOR_FOREGROUND_BLUE ) != 0 : blue = 1
			else                                      : blue = 0
	
			escapeString += "3" + colorToString[ (red, green, blue) ] + ";"
	
			if ( color & COLOR_BACKGROUND_RED ) != 0  : red = 1
			else                                      : red = 0
			if ( color & COLOR_BACKGROUND_GREEN ) != 0: green = 1
			else                                      : green = 0
			if ( color & COLOR_BACKGROUND_BLUE ) != 0 : blue = 1
			else                                      : blue = 0
	
			escapeString += "4" + colorToString[ (red, green, blue) ] + ";"
	
			if ( color & COLOR_FOREGROUND_INTENSITY ) != 0:
				escapeString += "1"
			else:
				escapeString += "0"
	
		global EscapeString
		EscapeString = escapeString + "m"
	else:
		bool = ctypes.windll.kernel32.SetConsoleTextAttribute( handle, color )
		return bool

