#!/usr/bin/env python

###########################################################################
#   Copyright (C) 2009 by SukkoPera                                       #
#   sukkosoft@sukkology.net                                               #
#                                                                         #
#   This program is free software; you can redistribute it and/or modify  #
#   it under the terms of the GNU General Public License as published by  #
#   the Free Software Foundation; either version 2 of the License, or     #
#   (at your option) any later version.                                   #
#                                                                         #
#   This program is distributed in the hope that it will be useful,       #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#   GNU General Public License for more details.                          #
#                                                                         #
#   You should have received a copy of the GNU General Public License     #
#   along with this program; if not, write to the                         #
#   Free Software Foundation, Inc.,                                       #
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
###########################################################################

import os
import pickle
from datetime import date

from siteintf import SiteInterface

class DataUnavailable (Exception):
	pass

class ViaggiaTreno:
	DEFAULT_CACHE_DIR = "cache"

	def __init__ (self, dir = DEFAULT_CACHE_DIR):
		self.dir = dir
		if not os.path.isdir (self.dir):
			os.mkdir (self.dir)
		self._si = SiteInterface ()
	
	def _getFilename (self, tid, date_):
		datef = date_.strftime ("%Y%m%d")
		file = "%d-%s.txt" % (tid, datef)
		ret = os.path.join (self.dir, file)
		return ret
		
	def _getHTMLFilename (self, tid, date_):
		datef = date_.strftime ("%Y%m%d")
		file = "%d-%s.html" % (tid, datef)
		ret = os.path.join (self.dir, file)
		return ret
	
	def haveCacheTxt (self, tid, date_):
		return os.path.isfile (self._getFilename (tid, date_))

	def haveCacheHTML (self, tid, date_):
		return os.path.isfile (self._getHTMLFilename (tid, date_))

	def isCached (self, tid, date_):
		return self.haveCacheTxt (tid, date_) or self.haveCacheHTML (self, tid, date_)
	
	def get (self, tid, date_):
		if self.haveCacheTxt (tid, date_):
			pkl_file = open (self._getFilename (tid, date_), 'rb')
			data = pickle.load (pkl_file)
			pkl_file.close ()
		elif self.haveCacheHTML (tid, date_):
			data = self._si.query (tid, infile = self._getHTMLFilename (tid, date_))
			output = open (self._getFilename (tid, date_), 'wb')
			pickle.dump (data, output)
			output.close ()
		elif date_ == date.today ():
#			print "not in cache"
			# Not in cache, get from site
			data = self._si.query (tid, self._getHTMLFilename (tid, date_))
			output = open (self._getFilename (tid, date_), 'wb')
			pickle.dump (data, output)
			output.close ()
		else:
			raise DataUnavailable ()
		return data

if __name__ == "__main__":
	import datetime
	vt = ViaggiaTreno ()
	data = vt.get (663, datetime.date.today ())
	print data
