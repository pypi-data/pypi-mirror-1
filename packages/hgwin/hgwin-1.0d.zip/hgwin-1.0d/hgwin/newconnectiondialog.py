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
import servers

class HGWIN_NEW_CONNECTION_DIALOG(wx.Dialog):
	ID_CHOOSE_REPOSITORY = 10

	################################################################################
	################################################################################
	def __init__( self, parent, id, title ):
		wx.Dialog.__init__( self, parent, id, title )

		panel = wx.Panel( self, -1, style=wx.RAISED_BORDER )

		name     = wx.StaticText( panel, -1, 'Name:' )
		text     = wx.StaticText( panel, -1, 'Repository:' )
		choose   = wx.Button    ( panel, self.ID_CHOOSE_REPOSITORY, "..." )
		porttext = wx.StaticText( panel, -1, 'Port #:' )
		self.NameTextControl       = wx.TextCtrl( panel, -1, '',     style=wx.TE_LEFT )
		self.RepositoryTextControl = wx.TextCtrl( panel, -1, '',     style=wx.TE_LEFT )
		self.PortTextControl       = wx.TextCtrl( panel, -1, '8000', style=wx.TE_RIGHT )

		pvbox = wx.BoxSizer( wx.VERTICAL   )
		phbox = wx.BoxSizer( wx.HORIZONTAL )
		phbox.Add( name                , proportion=0, flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=2 )
		phbox.Add( self.NameTextControl, proportion=1, flag=wx.ALL                           , border=2 )
		pvbox.Add( phbox               , proportion=0, flag=wx.ALL|wx.ALIGN_TOP|wx.EXPAND    , border=1 )

		phbox = wx.BoxSizer( wx.HORIZONTAL )
		phbox.Add( text                      , proportion=0, flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=2 )
		phbox.Add( self.RepositoryTextControl, proportion=1, flag=wx.ALL                           , border=2 )
		phbox.Add( choose                    , proportion=0, flag=wx.TOP|wx.LEFT|wx.BOTTOM         , border=2 )
		pvbox.Add( phbox                     , proportion=0, flag=wx.ALL|wx.ALIGN_TOP|wx.EXPAND    , border=1 )

		phbox = wx.BoxSizer( wx.HORIZONTAL )
		phbox.Add( porttext            , proportion=0, flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=2 )
		phbox.Add( self.PortTextControl, proportion=1, flag=wx.ALL                           , border=2 )
		pvbox.Add( phbox               , proportion=0, flag=wx.ALL|wx.ALIGN_TOP|wx.EXPAND    , border=1 )

		panel.SetSizer( pvbox )

		vbox = wx.BoxSizer( wx.VERTICAL )
		vbox.Add( panel, 1, wx.ALL|wx.EXPAND, 5 )

		buttonSizer = self.CreateButtonSizer( wx.CANCEL|wx.OK )
		vbox.Add( buttonSizer, 0, wx.ALIGN_CENTER|wx.BOTTOM )

		self.SetSizer( vbox )
		self.Centre()
		self.SetSize( (320, 200) )

		self.Bind( wx.EVT_BUTTON, self.OnOkClicked, id=wx.ID_OK )
		self.Bind( wx.EVT_BUTTON, self.OnChooseRepositoryDirectory, id=10 )

	################################################################################
	################################################################################
	def OnOkClicked(self, event):
		self.Repository = self.RepositoryTextControl.GetValue()
		self.Port       = self.PortTextControl.GetValue()
		self.Name       = self.NameTextControl.GetValue()
		def p():
			try:
				self.Server.Name       = self.Name
				self.Server.Repository = self.Repository
				self.Server.Port       = int( self.Port )
			except AttributeError:
				s = servers.SERVER( self.Name, self.Repository, int( self.Port ) )
				print str(s)
				servers.AddServer( s )
		p()
		self.Close()
	
	################################################################################
	################################################################################
	def Edit(self, server):
		self.RepositoryTextControl.SetValue( server.Repository )
		self.PortTextControl.SetValue( str( server.Port ) )
		self.NameTextControl.SetValue( str( server.Name ) )
		self.Server = server

	################################################################################
	################################################################################
	def OnChooseRepositoryDirectory(self, event):
		dlg = wx.DirDialog( self, "Choose a repository:", style=wx.DD_DEFAULT_STYLE )
		if dlg.ShowModal() == wx.ID_OK:
			self.RepositoryTextControl.SetValue( dlg.GetPath() )
		dlg.Destroy()

