#!/usr/bin/env python2.5
# coding: utf-8
import os
from os import path
import csv

import logging
logger = logging.getLogger()

class DataFile( object ):

	def __init__( self ):
		self.rows = []

	def load( self, filePath ):
		if path.exists( filePath ) == False:
			raise IOError, filePath + " is not found at " + os.getcwdu()
		else:
			logger.info( filePath + " is found at " + os.getcwdu() )
		dataFile = None
		dataFile = open( filePath )
		if dataFile is not None:
			for row in csv.reader( dataFile ):
				columns = []
				for col in row:
					columns.append( unicode( col ) )
				self.rows.append( columns )
		dataFile.close()

	def getRows( self ):
		return self.rows

	def __del__( self ):
		if self.rows is not None:
			del self.rows