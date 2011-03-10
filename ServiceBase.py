#Copyright (C) 2009 Quest Software, Inc.
#File:		ServiceBase.py
#Version:	1.0.0.203

############################################################
#
#	THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND,
#	EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED 
#	WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE. 
#
############################################################

import win32serviceutil
import win32service

import os
import sys
import time

sys.stopdriver = "false" 

class ServiceLauncher(win32serviceutil.ServiceFramework):
	
	_exe_name_ = r"..\Python25\lib\site-packages\win32\PythonService.exe"
	
	def __init__(self, args, register):
		#self.init_func = init
		self.register_func = register
		win32serviceutil.ServiceFramework.__init__(self, args)

		
	def SvcStop(self):
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		sys.stopservice = "true"
		import cherrypy
		cherrypy.engine.exit()
		
	def SvcDoRun(self):
		#self.init_func()
		self.register_func()
		
class ServiceHelperBase:
	def GetPathToCurrentClass(self, cls, fileName):
		import win32api
		import os	
		try:
			fname = win32api.GetFullPathName(fileName)
			path = os.path.split(fname)[0]
			fname = os.path.join(path, win32api.FindFiles(fname)[0][8])
		except win32api.error:
			raise error, "Could not resolve the path name '%s' to a full path" % (argv[0])
		
		modName = os.path.splitext(fname)[0]
		return modName + "." + cls.__name__

	def CallUtil(self, *argvLine):
		cmdLine = ['ServiceBase.py',]
		cmdLine.extend(list(argvLine))
		import win32serviceutil
		win32serviceutil.HandleCommandLine(self.Class, serviceClassString =  self.GetPathToCurrentClass(self.Class, self.File), argv = cmdLine)	

	def Start(self):
		self.CallUtil('--wait', 60, 'start')

	def Stop(self):
		self.CallUtil('--wait', 60, 'stop')
		
	def Install(self):
		self.CallUtil( '--startup', 'auto',  'install' )	

	def Remove(self):
		self.CallUtil("remove")			