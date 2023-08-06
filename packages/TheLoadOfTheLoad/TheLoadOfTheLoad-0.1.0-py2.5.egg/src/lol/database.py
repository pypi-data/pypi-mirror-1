#!/usr/bin/env python2.5
# coding: utf-8
from sqlite import SQLite
from mysql import MySQL

import logging
logger = logging.getLogger()


class Database( object ):

	def __init__( self, databaseConfig ):
		self.database = None
		self.databaseConfig = databaseConfig
		if self.databaseConfig.getDbms() == "sqlite3":
			self.database = SQLite( self.databaseConfig )
		elif self.databaseConfig.getDbms() == "mysql":
			self.database = MySQL( self.databaseConfig )

	def connect( self ):
		logger.debug( "connect" )
		return self.database.doConnect()

	def query( self, sql ):
		logger.debug( "query:" + sql )
		return self.database.doQuery( sql )

	def execute( self, sql ):
		logger.debug( "execute:" + sql )
		return self.database.doExecute( sql )

	def commit( self ):
		logger.debug( "commit" )
		return self.database.doCommit()

	def rollback( self ):
		logger.debug( "rollback" )
		return self.database.doRollback()

	def close( self ):
		logger.debug( "close" )
		return self.database.doClose()

	def __del__( self ):
		if self.database is not None:
			del self.database
		if self.databaseConfig is not None:
			del self.databaseConfig
