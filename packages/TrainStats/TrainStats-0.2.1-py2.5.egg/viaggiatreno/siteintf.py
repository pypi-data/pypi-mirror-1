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

import urllib
import urllib2
import re
import datetime

from BeautifulSoup import BeautifulSoup


class SiteInterface (object):
	BASEURL = "http://mobile.viaggiatreno.it/viaggiatreno/mobile/scheda"
	USERAGENT = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8) Gecko/20051111 Firefox/1.5"
	#USERAGENT = "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; InfoPath.1)"

# It seems using POST will not return the train detail
#	def _queryByPost (self, idTreno):
#		params = {"numeroTreno": idTreno, "dettaglio": "visualizza", "tipoRicerca": "", "lang": "IT"}
#		headers = {"User-Agent": self.USERAGENT}
#		enc_params = urllib.urlencode (params)
#		newurl = "%s?%s" % (baseurl, enc_params)
#		print newurl
#		req = urllib2.Request (newurl, headers = headers)
#		r = urllib2.urlopen (req)
#		return r.read ()

	def _queryByGet (self, idTreno):
		params = {"numeroTreno": idTreno, "dettaglio": "visualizza"}
		headers = {"User-Agent": self.USERAGENT}
		newurl = "%s?%s" % (self.BASEURL, urllib.urlencode (params))
		#print newurl
		req = urllib2.Request (newurl, headers = headers)
		r = urllib2.urlopen (req)
		html = r.read ()
		return html

	def _queryByFile (self, htmlfile = "tmp.htm"):
		# Gets the data from an existing file
		fp = open (htmlfile)
		html = fp.read ()
		return html
		
# For Python 2.4:
#		t1 = time.strptime (t1, "%H:%M")
#		t1 = datetime.datetime (t1[0], t1[1], t1[2], t1[3], t1[4])
#		t2 = time.strptime (t2, "%H:%M")
#		t2 = datetime.datetime (t2[0], t2[1], t2[2], t2[3], t2[4])
	def timediff (self, t1, t2):
		"""Returns the difference in minutes between t1 and 2.
		Both must be strings in the "%H:%M" format.
		If t2 < t1, result will be negative."""
		t1 = datetime.datetime.strptime (t1, "%H:%M")
		t2 = datetime.datetime.strptime (t2, "%H:%M")
		if t2 < t1:
			diff = (t1 - t2).seconds / -60
			# Here we try to workaround cases like 22:50 - 00:24, assuming the max negative timediff we might get is -10
			if diff < -10:
				diff = (t2 - t1).seconds / 60
		else:
			diff = (t2 - t1).seconds / 60
		return diff

	def dumpHtml (self, html, dumpfile = None):
		"""Dump HTML, if needed."""
		assert (html is not None)
		if dumpfile is not None:
			# Manipulate the HTML a bit
			re.sub (r'"/viaggiatreno/css/mobile.css"', '"mobile.css"', html)
			re.sub (r'"/"', '"http://mobile.viaggiatreno.it/"', html)

			# Write it out
			fp = open (dumpfile, "w")
			fp.write (html)
			fp.close ()

	def _parse (self, html):
		"""Parse HTML and extract the data of interest."""
		ret = []
		soup = BeautifulSoup (html)
		for div in soup.findAll ("div", {"class":  "giaeffettuate"}) + soup.findAll ("div", {"class":  "corpocentrale"}):
			station = div.find ("h2")
			station = str (station.contents[0])

			# Now get the time
			prog = None
			real = None
			tag = None
			for p in div.findAll ("p"):
				t = str (p.contents[0])
				time = p.find ("strong")
				if len (time.contents) > 0:
					time = str (time.contents[0])
				else:
					time = "00:00"
				if re.search ("(?i)programmat(a|o)", t):
					prog = time
				elif re.search ("(?i)effettiv(a|o)", t):
					real = time
					tag = "eff"
				elif re.search ("(?i)previst(a|o)", t):
					real = time
					tag = "est"
			assert (prog is not None and real is not None and tag is not None)
			e = (station, prog, real, self.timediff (prog, real), tag)
			ret.append (e)
		return ret

	def query (self, trainId, dumpfile = None, infile = None):
		if infile is not None:
			html = self._queryByFile (infile)
		else:
			html = self._queryByGet (trainId)
		self.dumpHtml (html, dumpfile)
		return self._parse (html)

if __name__ == "__main__":
	si = SiteInterface ()
	print si.query (2513)
