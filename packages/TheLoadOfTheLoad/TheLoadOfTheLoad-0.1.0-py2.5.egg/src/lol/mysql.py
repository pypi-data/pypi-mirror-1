#!/usr/bin/env python2.5
# coding: utf-8

import MySQLdb

import logging
logger = logging.getLogger()

class MySQL():

	def __init__( self, databaseConfig ):
		self.connection = None
		self.databaseConfig = databaseConfig
		logger.debug( "MySQL connecter created" )

	def doConnect( self ):
		self.connection = MySQLdb.connect( 
										db = self.databaseConfig.getDatabase(), 
										host = self.databaseConfig.getHost(), 
										port = self.databaseConfig.getPort(), 
										user = self.databaseConfig.getUser(), 
										passwd = self.databaseConfig.getPassword()
										)

	def doQuery( self, sql ):
		cursor = self.connection.cursor()
		cursor.execute( sql )
		return cursor
	
	def doExecute( self, sql ):
		cursor = self.connection.cursor()
		cursor.execute( sql )
		return cursor
	
	def doCommit( self ):
		return self.connection.commit()
	
	def doRollback( self ):
		return self.connection.rollback()

	def doClose( self ):
		return self.connection.close()

	def __del__( self ):
		if self.connection is not None:
			del self.connection
		if self.databaseConfig is not None:
			del self.databaseConfig
