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

class Graph (object):
	PNG_SIZE = (640, 480)
#	GDFONTPATH = "/usr/share/fonts/truetype/ttf-bitstream-vera"
	GDFONTPATH = "/usr/share/fonts/TTF/"
#	FONT = ("Vera", 10)
	FONT = ("DejaVuSans", 10)
	
	def __init__ (self):
		# Set the font path for gdlib
		if not os.path.isdir (self.GDFONTPATH):
			print "WARNING: GDFONTPATH points to a non-existant directory"
                os.environ["GDFONTPATH"] = self.GDFONTPATH

	def _initGnuplot (self, output_file):
		g = Gnuplot.Gnuplot ()
		
		# Set PNG output
		if self.FONT is not None:
			g ("set terminal png font %s size %s enhanced" % (" ".join ([str (i) for i in self.FONT]), ",".join ([str (i) for i in self.PNG_SIZE])))
		else:
			g ("set terminal png size %s enhanced" % ",".join ([str (i) for i in self.PNG_SIZE]))
		g ("set output \"%s\"" % output_file)
		return g

	
	def daily (self, tid, day, data, output_file):
		g = self._initGnuplot (output_file)
		
		# Graph style
		g ("set data style linespoints")
		g ("set nokey")
		g ("set grid")
		
		# Title
		title = "Ritardo treno %s - %s" % (tid, day.strftime ("%A %d %B %Y"))
		g.title (title)
		
		# X-Axis
		#g.xlabel ("Stazione")
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

	def aggregate_delay (self, tid, data_min, data_avg, data_max, output_file):
		g = self._initGnuplot (output_file)
		
		# Graph style
		g ("set data style linespoints")
		g ("set pointsize 1.5")
		g ("set key box")
		g ("set grid")
		
		# Title
#		title = "Ritardo treno %s - %s" % (tid, day.strftime ("%A %d %B %Y"))
#		g.title (title)
		
		# X-Axis
		#g.xlabel ("Stazione")
		g ("set xtics rotate")
		g ("set xzeroaxis linetype -1 linewidth .5")

		# X-tics
		assert (len (data_min) == len (data_avg))
		assert (len (data_min) == len (data_max))
		xtics = []
		for tic in [tup[0] for tup in data_min]:
			tup = '"%s" %d' % (tic, len (xtics))
			xtics.append (tup)
		g ("set xtics (%s)" % (",".join (xtics)))

		# Y-Axis
		g.ylabel ("Ritardo (min)")
		#set ydata time
		#set timefmt "%M"
		
		# Data
		if data_min is not None:
			vals = [tup[1] for tup in data_min]
			pi_min = Gnuplot.Data (vals, title = "Ritardo minimo")
		if data_avg is not None:
			vals = [tup[1] for tup in data_avg]
			pi_avg = Gnuplot.Data (vals, title = "Ritardo medio")
		if data_max is not None:
			vals = [tup[1] for tup in data_max]
			pi_max = Gnuplot.Data (vals, title = "Ritardo massimo")
		g.replot (pi_min, pi_avg, pi_max)

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
