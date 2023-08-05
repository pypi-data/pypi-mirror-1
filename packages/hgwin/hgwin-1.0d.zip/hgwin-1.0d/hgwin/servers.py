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
import os
import sys

class SERVER:
	################################################################################
	################################################################################
	def __init__(self, name, repository, port):
		self.Name = name
		self.Repository = repository
		self.Port = port
		self.Serving = False
	
	################################################################################
	################################################################################
	def GetAsTuple(self):
		return (self.Name, self.Repository, self.Port)
	
	################################################################################
	################################################################################
	@staticmethod
	def FromTuple(tuple):
		return SERVER(tuple[0], tuple[1], tuple[2])

	################################################################################
	################################################################################
	def IsServing(self):
		return self.Serving

	################################################################################
	################################################################################
	def _RunServer(self):
		print "Starting..."
		cwd = os.getcwd()
		os.chdir( self.Repository )
		path = os.getenv( "PATH" )
		for val in path.split(";"):
			fname = val + os.sep + 'hg.exe'
			try:
				if os.stat( fname ):
					break
			except WindowsError:
				fname = None
				continue
		if not fname: 
			return -1
		args = [ 'hg', 'serve', '-n', '"%s"' % self.Name, '-p', '%d' % self.Port ]
		res = os.spawnl( os.P_NOWAIT, fname, *args )
		os.chdir( cwd )
		return res

	################################################################################
	################################################################################
	def StartServing(self):
		self.Pid = self._RunServer()
		print self.Pid
		if self.Pid == -1:
			return False
		self.Serving = True
		return True
	
	################################################################################
	################################################################################
	def StopServing(self):
		assert self.Pid != -1
		import ctypes
		kernel32 = ctypes.windll.kernel32
		kernel32.TerminateProcess( ctypes.c_int( self.Pid ), 0 )
		self.Pid = -1
		self.Serving = False

	################################################################################
	################################################################################
	def __str__(self):
		return "Name:\t%s\nRepo:\t%s\nPort:\t%d" % (self.Name, self.Repository, self.Port)

ServerList = []

################################################################################
################################################################################
def AddServer( server ):
	global ServerList
	ServerList.append( server )

################################################################################
################################################################################
def GetServer():
	for s in ServerList:
		yield s

################################################################################
################################################################################
def GetServerByName(name):
	x = filter( lambda x: x.Name == name, ServerList )
	assert len(x) == 1
	return x[0]

################################################################################
################################################################################
def GetServerByIndex(index):
	return ServerList[ index ]

################################################################################
################################################################################
def RemoveServerByName( name ):
	global ServerList
	ServerList = filter( lambda x: x.Name != name, ServerList )

################################################################################
################################################################################
def SaveServers( configfile ):
	fout = open( configfile, "w" )
	fout.write( "\nServerList = [\n" )
	for s in GetServer():
		fout.write( "\t%s,\n" % str( s.GetAsTuple() ) )
		print str(s), s.GetAsTuple()
	fout.write( "]\n\n" )
	fout.flush()
	fout.close()

################################################################################
################################################################################
def LoadServers( configfile ):
	global ServerList
	try: 
		configfile = __import__( configfile.split(".")[0], {}, {} )
		for tup in configfile.ServerList:
			ServerList.append( SERVER.FromTuple( tup ) )
	except ImportError:
		pass
	print "Loaded %d servers..." % len( ServerList )


