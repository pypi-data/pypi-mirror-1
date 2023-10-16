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
import subprocess
import Gnuplot

class NotFoundInPathException (Exception):
	pass

# Useful function
def findInPath (path):
        """Find the file named path in the sys.path.
        Returns the full path name if found, None if not found"""

	for dirname in os.environ['PATH'].split (os.path.pathsep):
		possible = os.path.join (dirname, path)
		if os.path.isfile (possible):
			return possible
	
	# Not found
	raise NotFoundInPathException (path)

class Graph (object):
	PNG_SIZE = (640, 480)
	
	def __init__ (self):
		pass
	
	def daily (self, tid, day, data, output_file):
		g = Gnuplot.Gnuplot ()
		
		# Set PNG output
		g ("set terminal png size %s enhanced" % ",".join ([str (i) for i in self.PNG_SIZE]))
		g ("set output \"%s\"" % output_file)
		
		# Graph style
		g ("set data style linespoints")
		g ("set nokey")
		g ("set grid")
		
		# Title
		title = "Ritardo treno %s - %s" % (tid, day.strftime ("%A %d %B %Y"))
		g.title (title)
		
		# X-Axis
		g.xlabel ("Stazione")
		g ("set xtics rotate")
		g ("set xzeroaxis linetype -1 linewidth .5")

		# Y-Axis
		g.ylabel ("Ritardo (min)")
		#set ydata time
		#set timefmt "%M"
		
		# Data
		xtics = []
		for tic in [tup[0] for tup in data]:
			tup = '"%s" %d' % (tic, len (xtics))
			xtics.append (tup)
		g ("set xtics (%s)" % (",".join (xtics)))
		vals = [tup[3] for tup in data]
		g.plot (vals)

# Go!
if __name__ == "__main__":
	import datetime
	import locale
	
	try:
		locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
	except Exception, e:
		print "Cannot set locale: %s" % e.message
		
	g = Graph ()
	g.daily (400, datetime.date.today (), [("milano", 10), ("roma", 5)], "test.png")
