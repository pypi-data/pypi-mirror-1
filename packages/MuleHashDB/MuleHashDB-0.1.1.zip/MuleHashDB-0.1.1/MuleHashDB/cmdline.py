#!/usr/bin/env python
# -*- coding: iso8859-15 -*-

# =============================================================================
# $Id: cmdline.py 51 2006-01-31 21:55:49Z s0undt3ch $
# =============================================================================
#             $URL: http://mulehashdb.ufsoft.org/svn/tags/MuleHashDB-0.1.1/MuleHashDB/cmdline.py $
# $LastChangedDate: 2006-01-31 21:55:49 +0000 (Tue, 31 Jan 2006) $
#             $Rev: 51 $
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

import sys, string
import MuleHashDB
from MuleHashDB.core import MuleHashDBCore
from urllib import unquote
class CmdLine:
	def __init__(self):
		try:
			from optparse import OptionParser
		except ImportError:
			try:
				from optik import OptionParser
			except ImportError:
				raise ImportError, \
						'Requires Python 2.3 or the Optik option parsing library.'
		
		usage = '%prog -a "link1 link2" | -d "link1 link2" [ extra option(s) ]'
		parser = OptionParser(
				usage, version='%prog (MuleHashDB) ' + MuleHashDB.__version__)
	
		parser.description = '\033[1;32mMuleHashDB is a simple tool to ' + \
				'keep track of downloaded aMule file hashes.\033[m ' + \
				'\033[1;31mSubmit bugs or new features to:\033[m \
				\t\t\033[1;33m *\033[m\033[1;34m http://mulehashdb.ufsoft.org\
				\t\t\033[m\033[1;33m *\033[m\033[1;34m ufs@ufsoft.org\033[m'
	
		parser.add_option('-V',
				action = 'store_true',
				dest = 'version',
				help = 'Display long version number, ie,\
						with svn revision number.')
	
		parser.add_option('-a', '--add',
				type = 'string',
				dest = 'add_links',
				metavar = 'ED2k_LINK(S)',
				help = 'Add ED2k link(s) to DB and Mule.\
						Separate links by spaces.')
	
		parser.add_option('-d', '--del',
				type = 'string',
				dest = 'del_links',
				metavar = 'ED2k_LINK(S)_OR_HASH(ES)',
				help = 'Delete ED2k link(s) from DB.\
						Pass a ED2k link or the hash only.')
	
		parser.add_option('-n', '--no-mule',
				action = 'store_true',
				dest = 'no_mule',
				default = 'false',
				help = 'Don\'t add link(s) to Mule.\
						Default: %default')
	
		parser.add_option('-c', '--mark-complete',
				type = 'string',
				dest = 'completed',
				metavar = 'ED2k_LINK(S)_OR_HASH(ES)',
				help = 'Mark a database entry as completly downloaded.\
						Pass the hash(es) or ED2k link of the complete\
						filename(s). Separate them by spaces.')
	
		parser.add_option('-F', '--fill-from-dl-list',
				action = 'store_true',
				dest = 'fill',
				default ='false',
				help = "Fill DB with your Mule's download list.\
						Requires amulecmd binary.")
	
		parser.add_option('-s', '--stats',
				type = 'string',
				dest = 'stats',
				metavar = 'EXTRA_ARG',
				help = 'Display some statistics.\
						Pass one of, all, complete, incomplete, today.\
						all - list all database entries.\
						today - list all entries completed today.\
						complete - list all completed entries.\
						incomplete - list all incomplete entries.')

		parser.add_option('--config',
				type = 'string',
				dest = 'configfile',
				metavar = 'PATH_TO_CONFIG_FILE',
				help = 'Use a diferent configuration file.')
	
		parser.add_option('-D', '--debug',
				action = 'store_const',
				const = 2,
				dest = 'verbose',
				help = 'Run in debug mode.')
	
		parser.add_option('-Q', '--quiet',
				action = 'store_const',
				const = 0,
				dest = 'verbose',
				help = 'Run in quiet mode')
		
		(options, args) = parser.parse_args(sys.argv[1:])
	
		if not sys.argv[1:]:
			parser.error('Pass at least one of --add, --del "ED2k_link(s)".')

		if options.configfile:
			muleHashDB = MuleHashDBCore(
								verbose=options.verbose,
								configfile=options.configfile
								)
		else:
			muleHashDB = MuleHashDBCore(verbose=options.verbose)
				
		if options.version == 1:
			print 'mhdb (MuleHashDB) ' + MuleHashDB.__version__ + \
					' - Revision ' + muleHashDB.__revision__.split(' ').pop(1)
			# Exit Cleanly without any further output
			sys.exit(0)
	
		# Output a blank line before any output
		print
	
		if options.add_links:
			options.add_links = unquote(options.add_links)
			if options.add_links.find('ed2k://') != -1:
				ed2k_links = []
				for ed2k_link in options.add_links.split(' ed2k://'):
					if ed2k_link.find('|file|') and not \
							ed2k_link.find('ed2k://|file|'):
								ed2k_link = string.replace(
										ed2k_link, 'ed2k://|file|','|file|')
					ed2k_links.append(ed2k_link)
				muleHashDB.addLinks(ed2k_links, options.no_mule)
			else:
				parser.error('You must pass a valid ED2k link')
	
		if options.del_links:
			muleHashDB.delLinks(unquote(options.del_links))
	
	
		if options.completed:
			muleHashDB.markComplete(unquote(options.completed))
	
	
		if options.fill == 1:
			muleHashDB.addFromAmuleCMD()
	
		if options.stats:
			if options.stats.lower() == 'complete':
				muleHashDB.stats('complete')
			elif options.stats.lower() == ('incomplete'):
				muleHashDB.stats('incomplete')
			elif options.stats.lower() == 'yesterday':
				muleHashDB.stats('yesterday')
			elif options.stats.lower() == 'today':
				muleHashDB.stats('today')
			elif options.stats.lower() == 'all':
				muleHashDB.stats('all')
			else:
				parser.error("'" + options.stats + \
						"' is not a valid '-s|--stats' argument.")
