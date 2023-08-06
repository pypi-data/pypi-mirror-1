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

from ez_setup import use_setuptools
use_setuptools ()
from setuptools import setup, find_packages

# This is nice, but won't work on Python 2.3 :(
import subprocess
pkgver = subprocess.Popen (["./trainstats.py", "--version"],
                stdout = subprocess.PIPE).communicate ()[0].strip ()


setup (
	name = 'TrainStats',
	version = pkgver,
	packages = find_packages (),
#	scripts = ['trainstats.py'],
#	py_modules = ['dnsomatic_api'],

	include_package_data = True,
	zip_safe = True,

	# metadata for upload to PyPI
	author = 'SukkoPera',
	author_email = 'software@sukkology.net',
	description = 'Get train time data from viaggiatreno.it',
	url = 'http://www.sukkology.net',
	license = "GPLv2",
	keywords = "trenitalia ffss fs viaggiatreno ritardo",
	# could also include long_description, download_url, classifiers, etc.

	entry_points = {
		'console_scripts': [
			'trainstats = trainstats.trainstats:main'
		],
		'setuptools.installation': [
			'eggsecutable = trainstats.trainstats:main',
		]
	}
)
