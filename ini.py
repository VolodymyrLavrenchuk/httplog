#Copyright (C) 2009 Quest Software, Inc.
#File:		ini.py
#Version:	1.0.0.1000

############################################################
#
#	THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, 
#	EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
#	WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE. 
#
############################################################

from ConfigParser import RawConfigParser
def read( path, section, option):
	conf = RawConfigParser()
	conf.read( path )
	return conf.get( section, option )
