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
import sys
import datetime
import locale
from optparse import OptionParser

from viaggiatreno.viaggiatreno import ViaggiaTreno
from graph import Graph

PROGRAM_VERSION = "0.2.1"

def main (argv = None):
	if argv is None:
		argv = sys.argv
		
	try:
		locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
	except Exception, e:
		print "Cannot set locale: %s" % e.message

	cmdline_parser = OptionParser (usage = "%prog -t <train_id> [-d <YYYYMMGG>|-T] [more_options]", description = "Get train time data from viaggiatreno.it", version = "%s" % PROGRAM_VERSION)
	cmdline_parser.add_option ("-t", "--train", action = "store", type = "int", dest = "trainId", help = "Train ID", default = None)
	cmdline_parser.add_option ("-d", "--date", action = "store", type = "string", dest = "date", help = "Train date", default = None)
	cmdline_parser.add_option ("-T", "--today", action = "store_true", dest = "today", help = "Use today's date", default = False)
	cmdline_parser.add_option ("-g", "--graph", action = "store", type = "string", dest = "graphfile", help = "File to write the graph to (PNG)", default = None)
	cmdline_parser.add_option ("-G", "--autograph", action = "store_true", dest = "autograph", help = "Automatically generate output graph filename", default = False)
	(options, args) = cmdline_parser.parse_args (argv[1:])

	if options.trainId is None:
		cmdline_parser.print_help ()
		ret = 1
	else:
		# Get the data
		if options.today:
			date = datetime.date.today ()
		elif options.date is not None:
			try:
# For Python 2.4
# t1 = time.strptime (options.date, "%Y%m%d")
# date = datetime.datetime (t1[0], t1[1], t1[2], t1[3], t1[4])
				dt = datetime.datetime.strptime (options.date, "%Y%m%d")
				date = dt.date ()
			except ValueError, e:
				print "Cannot parse date, please use the YYYYMMDD format."
				date = None
				ret = 2
		else:
			print "No date specified"
			cmdline_parser.print_help ()
			ret = 1
			date = None
			
		if date is not None:
			vt = ViaggiaTreno ()
			data = vt.get (options.trainId, date)
					
			# Create graph PDF
			if options.graphfile is not None:
				graphfile = options.graphfile
			elif options.autograph:
				graphfile = "%d-%s.png" % (options.trainId, date.strftime ("%Y%m%d"))
			else:
				graphfile = None
				
			if graphfile is not None:
				g = Graph ()
				g.daily (options.trainId, date, data, graphfile)
			
			ret = 0
	return ret

# Go!
if __name__ == "__main__":
	sys.exit (main ())
