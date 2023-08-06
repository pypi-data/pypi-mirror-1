#!/usr/bin/env python2.5
# coding: utf-8
import os
from os import path
import yaml

import logging
logger = logging.getLogger()

class DataConfig( object ):

	def __init__( self ):
		self.table = None
		self.columns = []
		self.__isLogicalDeletion = False
	
	def load( self, filePath ):
		fileString = None
		configYAML = None
		if path.exists( filePath ) == False:
			raise IOError, filePath + " is not found at " + os.getcwdu()
		else:
			logger.info( filePath + " is found at " + os.getcwdu() )
		fileString = open( filePath ).read()
		fileString = fileString.decode( "utf8" )
		configYAML = yaml.safe_load( fileString )
		configYAML = configYAML["config"]
		dataYAML = configYAML["data"]		
		self.table = dataYAML["table"]
		self.__isLogicalDeletion = False
		for columnYAML in dataYAML["columns"]:
			column = {}
			column["fileColumns"] = columnYAML["fileColumns"]
			column["dbColumns"] = columnYAML["dbColumns"]
			column["key"] = columnYAML["key"]
			column["compare"] = columnYAML["compare"]
			column["type"] = columnYAML["type"]
			if "invalidRecordFunction" in columnYAML:
				if self.__isLogicalDeletion == False:
					self.__isLogicalDeletion = True
				column["invalidRecordFunction"] = columnYAML["invalidRecordFunction"]
			if "invalidRecordValue" in columnYAML:
				if self.__isLogicalDeletion == False:
					self.__isLogicalDeletion = True
				column["invalidRecordValue"] = columnYAML["invalidRecordValue"]
			self.columns.append( column )

	def getTable( self ):
		return self.table

	def getColumns( self ):
		return self.columns

	def getKeyColumns( self ):
		keyColumns = []
		for column in self.columns:
			if column["key"] == True:
				keyColumns.append( column )
		return keyColumns

	def getCompareColumns( self ):
		compareColumns = []
		for column in self.columns:
			if column["compare"] == True:
				compareColumns.append( column )
		return compareColumns

	def getDeletionColumns( self ):
		deletionColumns = []
		for column in self.columns:
			if "invalidRecordFunction" in column or "invalidRecordValue" in column:
				deletionColumns.append( column )
		return deletionColumns

	def getColumn( self, index ):
		for column in self.columns:
			if column["fileColumns"] == index:
				return column
		return None

	def isLogicalDeletion( self ):
		return self.__isLogicalDeletion

	def __del__( self ):
		if self.columns is not None:
			del self.columns
		if self.table is not None:
			del self.table
		if self.__isLogicalDeletion is not None:
			del self.__isLogicalDeletion
