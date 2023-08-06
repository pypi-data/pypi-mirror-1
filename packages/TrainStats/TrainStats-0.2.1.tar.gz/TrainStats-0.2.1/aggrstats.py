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

# Ritardo min/max/medio (per tutte fermate, evidenziare riga 10 min)
# Ritardo giornaliero per una fermata

import sys
import datetime
import locale
from optparse import OptionParser

#from viaggiatreno.viaggiatreno import ViaggiaTreno
import viaggiatreno.viaggiatreno as viaggiatreno
from trainstats.graph import Graph


def getData (days):
	"""Extract all the data of interest."""
	vt = viaggiatreno.ViaggiaTreno ()
	allData = {}
	for day in days:
		try:
			data = vt.get (tid, day)
			allData[day] = data
		except viaggiatreno.DataUnavailable:
			pass
	return allData


year = 2009
month = 1
day = range (1, 32)
tid = 2513

days = [datetime.date (year, month, x) for x in day]
allData = getData (days)

# Init arrays
avg = {}
min = {}
max = {}
stazioni_sorted = []
for stazione, prog, eff, ritardo, tag in allData.values ()[0]:
	max[stazione] = -999999
	min[stazione] = 999999	# I know I'm optimistic ;)
	avg[stazione] = 0
	stazioni_sorted.append (stazione)


for day, tup in allData.iteritems ():
	for stazione, prog, eff, ritardo, tag in tup:
		if ritardo < min[stazione] and ritardo > 0:
			min[stazione] = ritardo
		if ritardo > max[stazione]:
			max[stazione] = ritardo
		avg[stazione] += ritardo
for x in avg:
	avg[x] /= float (len (allData))

min_sorted = [(staz, min[staz]) for staz in stazioni_sorted]
avg_sorted = [(staz, avg[staz]) for staz in stazioni_sorted]
max_sorted = [(staz, max[staz]) for staz in stazioni_sorted]
g = Graph ()
g.aggregate_delay (tid, min_sorted, avg_sorted, max_sorted, "aggregate.png")
