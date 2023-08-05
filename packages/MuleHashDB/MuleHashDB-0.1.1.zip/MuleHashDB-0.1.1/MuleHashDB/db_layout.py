#!/usr/bin/env python
# -*- coding: iso8859-15 -*-

# =============================================================================
# $Id: db_layout.py 54 2006-02-04 03:19:35Z s0undt3ch $
# =============================================================================
#             $URL: http://mulehashdb.ufsoft.org/svn/tags/MuleHashDB-0.1.1/MuleHashDB/db_layout.py $
# $LastChangedDate: 2006-02-04 03:19:35 +0000 (Sat, 04 Feb 2006) $
#             $Rev: 54 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================

###############################################################################
#                                                                             # 
# Copyright © 2005 by Pedro Algarvio                                          # 
#                                                                             #
# This program is free software; you can redistribute it and/or modify it     #
# under the terms of the GNU General Public License as published by the Free  #
# Software Foundation; either version 2 of the License, or (at your option)   #
# any later version.                                                          #
# This program is distributed in the hope that it will be useful, but WITHOUT #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       #
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for   #
# more details.                                                               #
#                                                                             #
###############################################################################

# =============================================================================
# vim: set tabstop=4
# vim: set shiftwidth=4
#
# Display a red square on the 80th char so we can easely limit line width to a
# max of 79 chars, the way it should be.
# vim: autocmd BufEnter * match Error /\%80v/
# =============================================================================

try:
	from sqlobject import \
			SQLObject, DateCol, BoolCol, StringCol, \
			IntCol, DateTimeCol, EnumCol
except ImportError:
	raise ImportError, "You need sqlobject to run MuleHashDB"



class ED2kLink(SQLObject):
	"""
	Our Database Layout
	"""
	added			= DateCol()
	modified		= DateCol()
	finished 		= BoolCol(default=0)
	finished_date	= DateTimeCol(default=None)
	filename		= StringCol()
	size			= IntCol()
	hash			= StringCol(length=32, unique=True)
	rating			= EnumCol(
							enumValues=[
										'Not Rated',
										'Invalid/Corrupt/Fake',
										'Poor',
										'Good',
										'Fair',
										'Excellent'
										],
							default='Not Rated')
	comment			= StringCol(length=200, default=None)
	raw_link		= StringCol()


	def roundSize(self, size):
		if size < 1024: rounded = str(size) + ' bytes'
		elif size < 1048576: rounded = str(size / 1024) + ' KB'
		elif size < 1073741824: rounded = str(size / 1048576) + ' MB'
		else: rounded = str(size / 1073741824) + ' GB'
		return rounded
	
	def output(self):
		print
		print '\033[1m         ID:\033[m %d' % self.id
		print '\033[1m Date Added:\033[m %s' % self.added
		if not self.finished_date: # == 'None':
			print '\033[1m   Finished:\033[m %s' % str(self.finished)
		else:
			print '\033[1m   Finished:\033[m %s (%s)' \
					% (str(self.finished), str(self.finished_date))
		print '\033[1m   Filename:\033[m %s' % self.filename
		if self.size == 0:
			print '\033[1m       Size:\033[m No info available ' \
												'(added from amulecmd)'
		else:
			print '\033[1m       Size:\033[m %s' % self.roundSize(self.size)
		print '\033[1m       Hash:\033[m %s' % self.hash
		print

