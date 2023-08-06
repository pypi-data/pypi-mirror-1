#!/usr/bin/env python2.5
# coding: utf-8
from database import Database
from databaseconfig import DatabaseConfig
from dataconfig import DataConfig
from datafile import DataFile
from loader import Loader
import sys

import logging

class LOL( object ):

	def __init__( self ):
		self.databaseConfig = DatabaseConfig()
		self.dataConfig = DataConfig()
		self.dataFile = DataFile()
		self.loader = Loader()
		self.database = None

	def loadConfig( self, configFile ):
		self.databaseConfig.load( configFile )
		self.database = Database( self.databaseConfig )
		self.dataConfig.load( configFile )

	def loadData( self, dataFile ):
		self.dataFile.load( dataFile )
		self.loader.load( self.database, self.dataConfig, self.dataFile )

	def __del__( self ):
		if self.databaseConfig is not None:
			del self.databaseConfig
		if self.dataConfig is not None:
			del self.dataConfig
		if self.database is not None:
			del self.database
		if self.dataFile is not None:
			del self.dataFile
		if self.loader is not None:
			del self.loader

if __name__ == "__main__":
	
	configPath = "./config.yml"
	dataPath = "./data.csv"
	tracelevel = logging.INFO
	for arg in sys.argv:
		if arg[:len( "-config=" )] == "-config=":
			configPath = arg[len( "-config=" ):]
		elif arg[:len( "-data=" )] == "-data=":
			dataPath = arg[len( "-data=" ):]
		elif arg[:len( "-tracelevel=" )] == "-tracelevel=":
			if arg[len( "-tracelevel=" ):] == "DEBUG":
				tracelevel = logging.DEBUG
			elif arg[len( "-tracelevel=" ):] == "INFO":
				tracelevel = logging.INFO
			elif arg[len( "-tracelevel=" ):] == "WARN":
				tracelevel = logging.WARN
			elif arg[len( "-tracelevel=" ):] == "ERROR":
				tracelevel = logging.ERROR
			elif arg[len( "-tracelevel=" ):] == "CRITICAL":
				tracelevel = logging.CRITICAL
	logging.basicConfig( level=tracelevel, format='%(asctime)s %(levelname)s %(message)s' )

	loader = LOL()
	loader.loadConfig( configPath )
	loader.loadData( dataPath )
	if loader is not None:
		del loader


