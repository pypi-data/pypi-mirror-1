#!/usr/bin/env python
# -*- coding: iso8859-15 -*-

# =============================================================================
# $Id: core.py 51 2006-01-31 21:55:49Z s0undt3ch $
# =============================================================================
#             $URL: http://mulehashdb.ufsoft.org/svn/tags/MuleHashDB-0.1.1/MuleHashDB/core.py $
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

AVAILABLE_DB_TYPES = 'sqlite'

# Some needed indexes
FILENAME	= 2
SIZE		= 3
HASH		= 4

import sys

try:
	from sqlobject import *
except ImportError:
	print "You need sqlobject to run MuleHashDB."
	print "You can find it on http://sqlobject.org"
	sys.exit(1)
	
try:
	from sqlobject import sqlhub
except ImportError:
	print "You need sqlobject 0.7 to run MuleHashDB."
	print "You can find it on http://sqlobject.org"
	sys.exit(1)



import os, subprocess, re, string, logging
from datetime import date, datetime, timedelta

from MuleHashDB.db_layout import ED2kLink

HASH_RE = re.compile('[0-9A-Fa-f]{32}')


class MuleHashDBCore:
	"""
	Class to manage a database of ED2k hashes
	"""
	__revision__ = '$Rev: 51 $'

	def __init__(self, verbose=1, configfile='None'):
		"""
		Load the DB, or create it if non-existant.
		"""
		# Setup verbosity
		if not verbose:
			self.verbose = 1
		else:
			self.verbose = verbose
			
		global QUIET
		global DEBUG

		if self.verbose == 0:
			QUIET = True
			DEBUG = False
		elif self.verbose == 1:
			QUIET = False
			DEBUG = False
		elif self.verbose >= 2:
			QUIET = False
			DEBUG = True
		
		if configfile == 'None':
			# We're not passing any alternate config file.
			# So, we first check for one at the default path
			if os.access(
					os.path.join(os.environ['HOME'],'.mulehashdb'), os.F_OK):
				if DEBUG: print 'Configuration file exists...'
				CONFIG_FILE = os.path.join(os.environ['HOME'], '.mulehashdb')
			else:
				# We haven't found a config file on the default path
				# So, we copy the default config file to the default path
				from MuleHashDB import locations
				from shutil import copyfile
				print 'You dont have a configuration file.'
				print 'Copying the default one...'
				copyfile(locations.__share_dir__ + '/mulehashdb.conf',
						os.path.join(os.environ['HOME'], '.mulehashdb'))
				CONFIG_FILE = os.path.join(os.environ['HOME'], '.mulehashdb')
				print 'Done!'
				print
				print "You should edit' " + \
						str(os.path.abspath(CONFIG_FILE)) + \
						"' before running MuleHashDB again."
				sys.exit(0)
		else:
			# We're passing an alternate config file
			if configfile.find('~') != -1:
				CONFIG_FILE = os.path.expanduser(configfile)
			else:
				CONFIG_FILE = configfile

		if os.access(CONFIG_FILE, os.R_OK + os.W_OK):
			if DEBUG: print 'Loading configuration from ' +\
					str(os.path.abspath(CONFIG_FILE))
			import ConfigParser
			config = ConfigParser.ConfigParser()
			config.read([CONFIG_FILE])
			LOGFILE				= config.get('main', 'LOGFILE')
			DB_TYPE				= config.get('main', 'DB_TYPE')
			DB_NAME				= config.get('main', 'DB_NAME')
			AMULE_HOME			= config.get('main', 'AMULE_HOME')
			self.ED2K_BIN		= config.get('main', 'ED2K_BIN')
			self.AMULECMD_BIN	= config.get('main', 'AMULECMD_BIN')
			#Is the user passing it's home directory?
			if AMULE_HOME.find('~') != -1:
				self.AMULE_HOME = os.path.expanduser(AMULE_HOME)
			else:
				self.AMULE_HOME = AMULE_HOME
			if DEBUG:
				print '  AMULE_HOME: ' + self.AMULE_HOME
				print '     LOGFILE: ' + LOGFILE + ' (in aMule\'s Home dir)'
				print '     DB_TYPE: ' + DB_TYPE
				print '     DB_NAME: ' + DB_NAME + ' (in aMule\'s Home dir)'
				print '    ED2K_BIN: ' + self.ED2K_BIN
				print 'AMULECMD_BIN: ' + self.AMULECMD_BIN
		else:
			print 'Can\'t access ' + str(os.path.abspath(CONFIG_FILE))
		

		# Setup the console log format
		console_fmt = logging.Formatter(
				'%(levelname)-8s %(message)s')

		# setup the logfile logger for all verbose level
		logging.basicConfig(level=logging.DEBUG,
				format='%(asctime)s : %(levelname)-8s %(message)s',
				datefmt='%Y-%m-%d %H:%M:%S',
				filename=os.path.join(self.AMULE_HOME, LOGFILE),
				filemode='a')
		# setup the console logger for default verbose level - INFO
		console = logging.StreamHandler(sys.stdout)
		console.setFormatter(console_fmt)
		console.setLevel(logging.ERROR)
		logging.getLogger('').addHandler(console)

		# setup console logger for the other verbose levels
		if self.verbose >= 2:
			console.setLevel(logging.DEBUG)
		
		# We now define logger as global so we can just use it anywhere we
		# want to
		global logger
		logger = logging.getLogger('MuleHashDB')

		# What DB type are we using?
		if DB_TYPE == 'sqlite':
			# The step bellow ain't probably necessary.
			# SQLObject will probably complain
			try:
				from pysqlite2 import dbapi2 as sqlite
			except ImportError:
				raise ImportError, "You need pysqlite to run MuleHashDB"

			DB = os.path.join(self.AMULE_HOME, DB_NAME)
			conn_str = 'sqlite:' + DB
			if not os.access(DB, os.F_OK):
				# Database does not exist.
				MSG = "Database \033[1m'%s'\033[m doesn't exist. " \
						"Creating..." % str(DB)
				if not QUIET: print MSG
				logger.info(MSG)
				
				self.db = connectionForURI(conn_str)
				sqlhub.processConnection = self.db
				ED2kLink.createTable()
				if DEBUG: print 'Done!!!'
				logger.debug('Done!!!')
			elif not os.access(DB, os.R_OK + os.W_OK):
				MSG = "You don't have the permissions to access " + str(DB)
				logger.error(MSG)
				sys.exit(1)
			else:
				self.db = connectionForURI(conn_str)
				sqlhub.processConnection = self.db				
		else:
			logger.error('Wrong settings for DB_TYPE!')
			logger.error('Select a db type from the following available ' + \
					'to MuleHashDB: - %s', AVAILABLE_DB_TYPES)
			sys.exit(1)



	def __add_to_mule(self, ed2k_link):
		"""
		Private function to pass the link(s) to the ed2k binary, which then
		add's them to the Mule's download list
		"""

		self.ed2k_link = ed2k_link

		process = subprocess.Popen(
								[self.ED2K_BIN, 'ed2k://' + self.ed2k_link],
								stdout=subprocess.PIPE
								)

		ED2KLinks_FILE = os.path.join(self.AMULE_HOME, 'ED2KLinks')
		
		# We wait until the temporary ED2KLinks file is removed so we don't
		# get any race conditions, and all files are added.
		while os.access(ED2KLinks_FILE, os.F_OK):
			pass

		for line in process.stdout.readlines():
			if line == 'Link succesfully queued.\n':
				print line
				return 0
			else:
				return 1

		
	

	def search(self, hash_str, filename_str='None'):
		"""
		Search an ed2k link on the database.
		Returns a resultset of the found entries.
		TODO: In case filename_str is also passed search the database for
		a similiar name.
		"""
		self.hash		= hash_str.upper()
		self.filename	= filename_str
		
		
		hash_matches = ED2kLink.select(ED2kLink.q.hash==self.hash)
		
		if self.filename != 'None':
			name_matches = ED2kLink.select(ED2kLink.q.filename==self.filename)
			return hash_matches, name_matches
		else:
			return hash_matches



	def addLinks(self, ed2k_links, dont_add_to_mule):
		"""
		Add a new ed2k link to the database
		"""
		self.dont_add_to_mule = dont_add_to_mule
		total_links = 0
		for ed2k_link in ed2k_links:
			self.ed2k_link          = ed2k_link
			self.ed2k_link_hash     = ed2k_link.split('|').pop(HASH)
			self.ed2k_link_filename = ed2k_link.split('|').pop(FILENAME)
			self.ed2k_link_size		= ed2k_link.split('|').pop(SIZE)

			hash_matches, name_matches = self.search(
										self.ed2k_link_hash,
										filename_str=self.ed2k_link_filename)

			if hash_matches.count() == 0:
				if not QUIET:
					print 'Adding to database:'
					print '\033[1m Filename:\033[m %s' % \
							self.ed2k_link_filename
					print '\033[1m     Size:\033[m %s' % \
							self.ed2k_link_size
					print '\033[1m     Hash:\033[m %s' % \
							self.ed2k_link_hash
				
				logger.info('Adding %s(%s) to database',
						self.ed2k_link_filename,
						self.ed2k_link_hash.upper())
				
				ED2kLink(
						added		= date.today(),
						modified	= date.today(),
						finished	= 0,
						filename	= self.ed2k_link_filename,
						size		= int(self.ed2k_link_size),
						hash		= self.ed2k_link_hash.upper(),
						raw_link	= self.ed2k_link
						)
				# Increase total_links
				total_links += 1
				
				if DEBUG:
					print 'Done!!!'
				
				if self.dont_add_to_mule == 'true':
					pass
				else:
					if not QUIET: print 'Adding Link to Mule...'
					logger.info('Adding "%s" to mule', self.ed2k_link)
					retcode = self.__add_to_mule(self.ed2k_link)
					if retcode == 0:
						logger.info('Done...')
						if DEBUG: print 'Done...'
					else:
						logger.error('Failed to add link to mule...')
			else:
				# we won't check verbosity here cuz we need user input
				print
				MSG = 'ED2k link hash exists on DB'
				print MSG					
				logger.info(MSG)
				answers = ('y', 'ye', 'yes', 'n', 'no')
				positive_answers = ('y', 'ye', 'yes')
				negative_answers = ('n', 'no')
				for match in hash_matches:
					ED2kLink.output(match)
					if self.dont_add_to_mule == 'false':
						answer = ""
						while answer.lower() not in answers:
							answer = raw_input("Do you still want to add " + \
									"it to your Mule (y/n)? ")
							if answer.lower() in positive_answers:
								MSG = 'Updating database entry (Row ID: %d)' \
										% match.id
								print MSG
								logger.info(MSG)
								match.modified	= date.today()
								match.finished	= 0
								match.filename	= self.ed2k_link_filename
								match.size		= int(self.ed2k_link_size)
								match.hash		= self.ed2k_link_hash.upper()
								match.raw_link	= self.ed2k_link
								# Increase total_links
								total_links += 1
								if DEBUG: print 'Done...'
								logger.info('Done...')
								MSG = 'Adding "%s" to mule' % self.ed2k_link
								print MSG
								logger.info(MSG)
								retcode = self.__add_to_mule(self.ed2k_link)
								if retcode == 0:
									logger.info('Done...')
									if DEBUG: print 'Done...'
								else:
									logger.error('Failed...')
							elif answer.lower() in negative_answers:
								print '...not adding to Mule...'
							else:
								print 'Could not figure out your answer...'
					elif self.dont_add_to_mule == 'true':
						answer = ""
						while answer.lower() not in answers:
							answer = raw_input(
									"Do you wan't to update the DB (y/n)?")
							if answer.lower() in positive_answers:
								MSG = 'Updating database entry (Row ID: %d)' \
										% match.id
								print MSG
								logger.info(MSG)
								# since we're not adding to mule, we won't
								# update 'finished' and 'added'
								match.modified	= date.today()
								match.filename	= self.ed2k_link_filename
								match.size		= self.ed2k_link_size
								match.hash		= self.ed2k_link_hash.upper()
								match.raw_link	= self.ed2k_link
								# Increase total_links
								total_links += 1
								logger.info('Done...')
								if DEBUG: print 'Done...'
							elif answer.lower() in negative_answers:
								pass
							else:
								print 'Could not figure out your answer...'
		if not QUIET: print 'Processed ' + str(total_links) + ' links...'
	


	def delLinks(self, ed2k_links):
		"""
		Function to remove entries from database, only database.
		"""
		for hash in re.findall(HASH_RE, ed2k_links):
			matches = self.search(hash)
			if matches.count() == 1:
				for match in matches:
					MSG = "Deleted entry ID: %d matching hash '%s'" \
							% (match.id, hash)
					ED2kLink.delete(match.id)
					logger.info(MSG)
					if not QUIET:
						print 'Deleted entry:'
						ED2kLink.output(match)
			elif matches.count() == 0:
				MSG = "No database entry matching hash '%s' to delete." % hash
				logger.info(MSG)
				if not QUIET: print MSG
			else:
				# This won't occur, cuz hashes on db will be unique.
				logger.error('We have several matches!!!')


	
	def markComplete(self, hash_list):
		"""
		Function to mark database entry(ies) as completely downloaded.
		"""
		for hash in re.findall(HASH_RE, hash_list):
			matches = self.search(hash)
			if matches.count() == 1:
				for match in matches:
					if match.finished != 1:
						match.finished = 1
						match.modified = date.today()
						match.finished_date = datetime.today()
						MSG = "Marked '%s' as complete. (ID: %d)" % \
								(match.hash, match.id)
						if not QUIET:
							print 'Marked as complete:'
							ED2kLink.output(match)
						logger.info(MSG)
					else:
						MSG = "Hash '%s' already marked complete. (ID: %d)" \
								% (match.hash, match.id)
						logger.info(MSG)
						if not QUIET: print MSG
			elif matches.count() == 0:
				MSG = "No database entry matching hash '%s'" % hash + \
						" to mark as complete"
				if not QUIET: print MSG
				logger.info(MSG)
			else:
				# This won't occur, cuz hashes on db will be unique.
				logger.error('We have several matches!!!')
	
	
	
	def addFromAmuleCMD(self):
		"""
		Function that executes "amulecmd -c 'show dl'", parses the output
		and add's the hashes/filenames to the database.
		"""

		dlList = subprocess.Popen(
				[self.AMULECMD_BIN, '-c', 'show dl'],
				stdout = subprocess.PIPE)
		
		output = dlList.stdout.readlines()
		entries = []
		for line in output:
			if re.search(HASH_RE, line):
				entries.append(line.rsplit('[',1)[0][3:])
		for entry in entries:
			hash = entry[:32].upper()
			filename = entry[33:].rstrip()
			matches = self.search(hash)
			if matches.count() == 0:
				if not QUIET:
					print 'Adding to database:'
					print '\033[1mFilename:\033[m %s' % filename
					print '\033[1m    Hash:\033[m %s' % hash
				logger.info("Adding filename '%s' with hash '%s' to database",
						filename, hash)
				
				ED2kLink(
						added		= date.today(),
						modified	= date.today(),
						finished	= 0,
						filename	= filename,
						size		= 0,
						hash		= hash,
						raw_link	= 'added from amulecmd'
						)
			else:
				for match in matches:
					if not QUIET:
						print ' Not adding to database:'
						ED2kLink.output(match)
					logger.info("Not adding filename '%s' with hash '%s' " + \
							"to database", filename, hash)
	


	def stats(self, query):
		logger.debug('Running some statistics...')
		if query == 'complete':
			matches = ED2kLink.select(
								ED2kLink.q.finished==1,
								orderBy='finished_date')
		elif query == 'incomplete':
			matches = ED2kLink.select(
								ED2kLink.q.finished==0,
								orderBy='added')
		elif query == 'yesterday':
			matches = ED2kLink.select(AND(
				ED2kLink.q.modified == date.today() - timedelta(1),
				ED2kLink.q.finished==1),
				orderBy='finished_date')
		elif query == 'today':
			matches = ED2kLink.select(AND(
				ED2kLink.q.modified == date.today(),
				ED2kLink.q.finished==1),
				orderBy='finished_date')
		elif query == 'all':
			matches = ED2kLink.select(orderBy='added')

		entries = matches.count()

		if entries > 0:
			for match in matches:
				ED2kLink.output(match)
		
		if entries == 0:
			print ' No matching database entries found for your query.'
		elif entries == 1:
			print ' Found\033[1m 1\033[m database entry...'
		else:
			print ' Found\033[1m %d\033[m database entries...' % entries
		

