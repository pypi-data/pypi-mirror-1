#!/usr/bin/env python2.5
# coding: utf-8

import logging
logger = logging.getLogger()

class Loader( object ):

	def __init__( self ):
		self.database = None
		self.dataConfig = None
		self.dataFile = None
	
	def load( self, database, dataConfig, dataFile ):
		self.database = database
		self.dataConfig = dataConfig
		self.dataFile = dataFile
		self.database.connect()
		logger.info( "load start" )
		# 追加／更新処理
		logger.info( "  inset/upadate start" )
		for dataRow in dataFile.getRows():
			sql = self.generateSelectCompareByKeySQL( dataRow )
			dbRows = self.database.query( sql ).fetchall()
			if len( dbRows ) == 0:
				sql = self.generateInsertSQL( dataRow )
				logger.info( "insert " + dataRow.__repr__() )
				self.database.execute( sql )
			elif len( dbRows ) == 1:
				if dbRows[0] <> self.createCompareTuple( dataRow ):
					sql = self.generateUpdateSQL( dataRow )
					logger.info( "update " + dataRow.__repr__() )
					self.database.execute( sql )
		# 削除処理
		logger.info( "  delete start" )
		sql = self.generateSelectKeyForAllSQL()
		logger.info( sql )
		for dbRow in self.database.execute( sql ).fetchall():
			toDelete = True
			for dataRow in dataFile.getRows():
				if dbRow == self.createKeyTuple( dataRow ):
					toDelete = False
			if toDelete == True:
				sql = self.generateDeleteSQL( dbRow )
				logger.info( "delete " + dbRow.__repr__() )
				self.database.execute( sql )
		self.database.commit()
		self.database.close()

	def createCompareTuple( self, dataRow ):
		compareColumns = []
		for compareColumn in self.dataConfig.getCompareColumns():
			compareColumns.append( dataRow[compareColumn["fileColumns"]] )
		return tuple( compareColumns )

	def createKeyTuple( self, dataRow ):
		keyColumns = []
		for keyColumn in self.dataConfig.getKeyColumns():
			keyColumns.append( dataRow[keyColumn["fileColumns"]] )
		return tuple( keyColumns )

	def generateSelectCompareByKeySQL( self, dataRow ):
		sql = "select "
		columnIndex = 0
		for columnConfig in self.dataConfig.getCompareColumns():
			sql = sql + str( columnConfig["dbColumns"] ) + ", "
			columnIndex = columnIndex + 1
		if sql[len( sql ) - len( ", " ):] == ", ":
			sql = sql[0:len( sql ) - len( ", " )]
		sql = sql +" from " + self.dataConfig.getTable() + " where ( "
		columnIndex = 0
		for col in dataRow:
			columnConfig = None
			columnConfig = self.dataConfig.getColumn( columnIndex )
			if columnConfig["key"] == True:
				sql = sql + "( " + str( columnConfig["dbColumns"] ) + " = '" + str( col ) + "' ) and "
			columnIndex = columnIndex + 1
		if sql[len( sql ) - len( "and " ):] == "and ":
			sql = sql[0:len( sql ) - len( "and " )] 
		sql = sql + ");"
		if columnIndex == 0:
			sql = None
		return sql

	def generateSelectKeyForAllSQL( self ):
		sql = "select "
		columnIndex = 0
		for columnConfig in self.dataConfig.getKeyColumns():
			sql = sql + str( columnConfig["dbColumns"] ) + ", "
			columnIndex = columnIndex + 1
		if sql[len( sql ) - len( ", " ):] == ", ":
			sql = sql[0:len( sql ) - len( ", " )]
		sql = sql +" from " + self.dataConfig.getTable() + ";"
		if columnIndex == 0:
			sql = None
		return sql

	def generateInsertSQL( self, dataRow ):
		sql = "insert into " + self.dataConfig.getTable() + " ( "
		columnSql = ""
		valueSql = ""
		columnIndex = 0
		for col in dataRow:
			columnConfig = None
			columnConfig = self.dataConfig.getColumn( columnIndex )
			columnSql = columnSql + str( columnConfig["dbColumns"] ) + ", "
			if str( columnConfig["type"] ) <> "timestamp":
				valueSql = valueSql + "'" + str( col ) + "', "
			else:
				valueSql = valueSql + "'" + str( col ) + "', "
			columnIndex = columnIndex + 1
		if columnSql[len( columnSql ) - len( ", " ):] == ", ":
			columnSql = columnSql[0:len( columnSql ) - len( ", " )] 
		if valueSql[len( valueSql ) - len( ", " ):] == ", ":
			valueSql = valueSql[0:len( valueSql ) - len( ", " )] 
		sql = sql + columnSql + " ) values ( " + valueSql + " );"
		return sql

	def generateUpdateSQL( self, dataRow ):
		sql = "update " + self.dataConfig.getTable() + " set "
		columnIndex = 0
		for col in dataRow:
			columnConfig = None
			columnConfig = self.dataConfig.getColumn( columnIndex )
			sql = sql + str( columnConfig["dbColumns"] ) + " = " 
			if str( columnConfig["type"] ) <> "timestamp":
				sql = sql + "'" + str( col ) + "', "
			else:
				sql = sql + "'" + str( col ) + "', "
			columnIndex = columnIndex + 1
		if sql[len( sql ) - len( ", " ):] == ", ":
			sql = sql[0:len( sql ) - len( ", " )] 
		sql = sql + " where ( "
		columnIndex = 0
		for col in dataRow:
			columnConfig = None
			columnConfig = self.dataConfig.getColumn( columnIndex )
			if columnConfig["key"] == True:
				sql = sql + "( " + str( columnConfig["dbColumns"] ) + " = '" + str( col ) + "' ) and "
			columnIndex = columnIndex + 1
		if sql[len( sql ) - len( "and " ):] == "and ":
			sql = sql[0:len( sql ) - len( "and " )] 
		sql = sql + ");"
		if columnIndex == 0:
			sql = None
		return sql

	def generateDeleteSQL( self, dbRow ):
		if self.dataConfig.isLogicalDeletion() == True:
			sql = "update " + self.dataConfig.getTable() + " set "
			columnConfig = None
			for columnConfig in self.dataConfig.getDeletionColumns():
				sql = sql + columnConfig["dbColumns"] + " = "
				if "invalidRecordFunction" in columnConfig:
					sql = sql + columnConfig["invalidRecordFunction"] + ", "
				elif "invalidRecordValue" in columnConfig:
					if str( columnConfig["type"] ) <> "timestamp":
						sql = sql + "'" + columnConfig["invalidRecordValue"] + "', "
					else:
						sql = sql + "'" + columnConfig["invalidRecordValue"] + "', "			
			if sql[len( sql ) - len( ", " ):] == ", ":
				sql = sql[0:len( sql ) - len( ", " )] 
			sql = sql + " where ( "
			columnIndex = 0
			for column in self.dataConfig.getKeyColumns():
				sql = sql + "( " + str( column["dbColumns"] ) + " = '" + dbRow[columnIndex] + "' ) and "
				columnIndex = columnIndex + 1
			if sql[len( sql ) - len( "and " ):] == "and ":
				sql = sql[0:len( sql ) - len( " and " )]
			sql = sql + " );"
			if columnIndex == 0:
				sql = None
		else:
			sql = "delete from " + self.dataConfig.getTable() + " where ( "
			columnIndex = 0
			for column in self.dataConfig.getKeyColumns():
				sql = sql + "( " + str( column["dbColumns"] ) + " = '" + dbRow[columnIndex] + "' ) and "
				columnIndex = columnIndex + 1
			if sql[len( sql ) - len( "and " ):] == "and ":
				sql = sql[0:len( sql ) - len( " and " )]
			sql = sql + " );"
			if columnIndex == 0:
				sql = None
		return sql

	def __del__( self ):
		if self.database is not None:
			del self.database
		if self.dataConfig is not None:
			del self.dataConfig
		if self.dataFile is not None:
			del self.dataFile

