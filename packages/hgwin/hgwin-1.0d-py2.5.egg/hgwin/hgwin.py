################################################################################
## hgwin.py - hg serve manager for Windows using wxPython
##
## Copyright (C) 2007  Charles Mason <cemasoniv@gmail.com>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
##
################################################################################
import wx
from taskbaricon import *
import servers
import os.path

################################################################################
################################################################################
Version = "1.0"

################################################################################
################################################################################
class TaskBarApp(wx.Frame):
	def __init__(self, parent, id, title):
		pass

################################################################################
################################################################################
class HGWIN_APPLICATION(wx.App):
	def OnInit(self):
		#frame = TaskBarApp(None, -1, ' ')
		#frame.Center(wx.BOTH)
		#frame.Show(False)
		self.TaskBarIcon = HGWIN_TASKBARICON()
		self.TaskBarIcon.SetIcon( os.path.join(os.path.dirname( __file__ ), "icon.bmp" ) )
		return True

################################################################################
################################################################################
def main():
	servers.LoadServers( "serverlist.py" )
	app = HGWIN_APPLICATION(0)
	app.MainLoop()

if __name__ == '__main__':
	main()

