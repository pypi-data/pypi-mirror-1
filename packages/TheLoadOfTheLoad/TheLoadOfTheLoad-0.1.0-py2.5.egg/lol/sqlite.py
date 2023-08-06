#!/usr/bin/env python2.5
# coding: utf-8

import sqlite3

import logging
logger = logging.getLogger()

class SQLite():

	def __init__( self, databaseConfig ):
		self.connection = None
		self.databaseConfig = databaseConfig
		logger.debug( "sqllite connecter created" )

	def doConnect( self ):
		self.connection = sqlite3.connect( self.databaseConfig.getDsn() )

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
