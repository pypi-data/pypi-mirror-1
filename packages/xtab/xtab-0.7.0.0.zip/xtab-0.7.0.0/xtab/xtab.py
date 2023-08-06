#!python
"""xtab.py

Purpose
========
   Read a table (from a text file) of data in normalized form and cross-tab it,
   allowing multiple data columns to be crosstabbed.

Author
=======
	R. Dreas Nielsen (RDN)

Copyright and License
=======================
	Copyright (c) 2007, R.Dreas Nielsen
	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.
	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.
	The GNU General Public License is available at <http://www.gnu.org/licenses/>

Notes
======
	1. As of version 0.5.0.0 this code can be used either as a module or as
		a stand-alone script.
	2. The sole function intended to be used by callers of this module is 'xtab()'.
	3. When there are multiple values in the input that should go into a single
		cell of the output, only the first of these is written into that cell
		('first' is indeterminate).  The 'xtab()' function allows logging of
		the data selection statement (SQL) used to obtain the data for each cell,
		and the result(s) obtained, and thus to determine which cell(s) have
		multiple values.

History
=========
	----------	------------------------------------------------------------------------------
	 Date        Revisions
	----------  ------------------------------------------------------------------------------
	9/12/2007   Created; incomplete.  RDN.
	10/27/2007	Finished full functionality of 'xtab()'.  Usable as module or script.  RDN.
	10/28/2007	Cleaned up code and documentation.  Improvements to be made:
				1. Implement a class to wrap csv reader and writer objects
					to ensure appropriate closure of underlying file objects
					on error.
				2. Implement a class (object) for the input file to simplify
					format evaluation and opening (i.e., reduce multiple opens).
				3. Provide a default log-writing handler, and possibly an additional
					command-line argument consisting of an output filename for
					the log.
				4. Implement error-checking of the column names in the command
					line arguments prior to calling 'xtab()' (do #2 above first).
				5. Add more specific error traps throughout.
				RDN.
	1/13/2008	Revised to use the csv module's format sniffer instead of custom
				code in this module.  This addresses item 2 in the 10/28/2007 list.
				Revised so that the sqlite db is created in memory by default, and a
				temporary file is created only if specified by the (new) '-f'
				command-line option.  RDN.
	6/14/2008	Doubled apostrophes in string data values.  RDN.
	12/20/2008	Added options to keep the sqlite file, to specifiy the sqlite table
				name, and to log both error messages and SQL commands.  Bumped version
				number to 0.7.  RDN.
=====================================================================================
"""

#=====================================================================================
# TODO:
#	* Implement a class to wrap csv reader and writer objects
#	  to ensure appropriate closure of underlying file objects
#	  on error.  (Or use 'with' in 2.6/3.0)
#	* Implement error-checking of the column names in the command
#	  line arguments prior to calling 'xtab()'.
#	* Add more specific error traps throughout.
#=====================================================================================


_version = "0.7.0.0"
_vdate = "2008-12-20"

import sys
import os
import os.path
import csv
import sqlite3
import copy
import logging

_errmsg_noinfile = "No input filename specified."
_errmsg_badinfile = "Input file does not exist."
_errmsg_nooutfile = "No output filename specified."
_errmsg_norowheaders = "No row header columns specified."
_errmsg_nocolumheaders = "No column header columns specified."
_errmsg_nocellcolumns = "No cell value columns specified."
_errmsg_baderrlogfile = "Only one error log file name should be specified."
_errmsg_badsqllogfile = "Only one SQL log file name should be specified."

__help_msg = """Required Arguments:
   -i <filename>
      The name of the input file from which to read data.
      This must be a text file, with data in a normalized format.
      The first line of the file must contain column names.
   -o <filename>
      The name of the output file to create.
      The output file will be created as a .csv file.
   -r <column_name1> [column_name2 [...]]
      One or more column names to use as row headers.
      Unique values of these columns will appear at the beginning of every
      output line.
   -c <column_name1> [column_name2 [...]]
      One or more column names to use as column headers in the output.
      A crosstab column (or columns) will be created for every unique
      combination of values of these fields in the input.
   -v <column_name1> [column_name2 [...]]
      One or more column names with values to be used to fill the cells
      of the cross-table.  If n columns names are specified, then there will
      be n columns in the output table for each of the column headers
      corresponding to values of the -c argument.  The column names specified
      with the -v argument will be appended to the output column headers
      created from values of the -c argument.  There should be only one value
      of the -v column(s) for each combination of the -r and -c columns;
      if there is more than one, a warning will be printed and only the first
      value will appear in the output.  (That is, values are not combined in
      any way when there are multiple values for each output cell.)
Optional Arguments:
   -d
      Prints output column headers in two rows.  The first row contains values
      of the columns specified by the -c argument, and the second row contains
      the column names specified by the -v argument. If this is not specified,
      output column headers are printed in one row, with elements joined by
      underscores to facilitate parsing by other programs.
   -f
      Use a temporary (sqlite) file instead of memory for intermediate
      storage.
   -k
      Keep (i.e., do not delete) the sqlite file.  Only useful with the
      "-f" option.  Unless the "-t" option is also used, the table name will
      be "src".
   -t <tablename>
      Name to use for the table in the intermediate sqlite database.  Only
      useful with the "-f" and "-k" options.
   -e [filename]
      Log all error messages, to a file if the filename is specified or to the
      console if the filename is not specified.
   -q <filename>
      Log the sequence of SQL commands used to extract data from the input
      file to write the output file, including the result of each command.
   -h
      Print this help and exit.
Notes:
   1. Column names should be specified in the same case as they appear in the
      input file.
   2. The -f option creates a temporary file in the same directory as the
      output file.  This file has the same name as the input file, but an
      extension of '.sqlite'.
   3. There are no inherent limits to the number of rows or columns in the
      input or output files.
   4. Missing required arguments will result in an exception rather than an
      error message, whatever the error logging option.  If no error logging
      option is specified, then if there are multiple values per cell (the
      most likely data error), a single message will be printed on the console.
Copyright:
   Copyright (c) 2008, R.Dreas Nielsen
   Licensed under the GNU General Public License version 3."""


def xtab(infilename, rownames, xtab_colnames, xtab_datanames, outfilename,
		 dualheader=False, file_db=False, keep_file_db=False, tablename="src",
		 error_reporter=None, sql_reporter=None):
	"""Cross-tab data in the specified input file and write it to the output file.
	Arguments:
		infilename: string of the input file name.  Some diagnosis of file format
			(CSV or tab formatted) will be performed.
		rownames: list of strings of column names in the input file that will be used
			as row headers in the output file.
		xtab_colnames: list of strings of column names in the input file that will be
			used as primary column headers in the output file.
		xtab_datanames: list of strings of column names in the input file that will be
			crosstabbed in the output file.  These column names will also be used as
			secondary column names in the output file.
		outfilename: string of the output file name.  This file will all be written as CSV.
		dualheader: boolean controlling whether or not there will be one or two header
			rows in the output file.  If a single header row is used, then the primary and
			secondary column headers will be joined in each column header.  If two column
			headers are used, then the primary column headers will be used on the first
			line of headers, and the secondary column headers will be used on the second
			line of headers.
		file_db: boolean controlling whether or not the sqlite db is created as a disk file
			(if True) or in memory (if False, the default).
		keep_file_db: boolean controlling whether or not a sqlite disk file is retained
			(if True) or deleted after it has been used.
		error_reporter: logging.Logger object to report nonfatal errors (specifically, the presence
			of more than one value for a cell).
		sql_reporter: logging.Logger object to report the sqlite queries executed and their
			results.
	When multiple column headers in the input file are used as a single column header in
	the output file, the column names are joined with an underscore.  This is to facilitate
	any subsequent parsing to be done by other programs (e.g., R).
	"""
	multiple_vals = False		# A flag indicating whether or not multiple values were found for a single crosstab cell
	outfile = open(outfilename, "wb")	# The csv module adds an extra <CR> if "wt" is specified
	csvout = csv.writer(outfile)
	
	# Move the data into sqlite for easy random access.
	if file_db:
		inhead, intail = os.path.split(infilename)
		sqldbname = os.path.join(inhead, os.path.splitext(intail)[0] + ".sqlite")
		try:
			os.unlink(sqldbname)
		except:
			pass
	else:
		sqldbname = None
	if tablename == None:
		tablename = "src"
	sqldb = copy_to_sqlite(infilename, sqldbname, tablename)

	# Get list of unique values for 'xtab_colnames' columns
	sqlcmd = "select distinct %s from %s;" % (",".join(xtab_colnames), tablename)
	xtab_vals = sqldb.execute(sqlcmd).fetchall()

	# Write output headers
	if dualheader:
		extra_cols = len(xtab_datanames) - 1
		# Write header row 1/2
		outstrings = ['' for n in rownames]
		for n in xtab_vals:
			hdr = " ".join(n)
			outstrings.append(hdr.replace("'", "''"))
			for i in range(extra_cols):
				outstrings.append('')
		csvout.writerow(outstrings)
		# Write header row 2/2
		outstrings = [n for n in rownames]
		for n in xtab_vals:
			for i in xtab_datanames:
				outstrings.append(i.replace("'", "''"))
		csvout.writerow(outstrings)
	else:
		outstrings = [n for n in rownames]
		for n in xtab_vals:
			for i in xtab_datanames:
				outstrings.append("%s_%s" % ("_".join(n), i.replace("'", "''")))
		csvout.writerow(outstrings)

	# Write output data
	# For each unique combination of row headers
	#	Initiate a new output line
	#	Get the row headers
	#		For every item in the xtab_vals
	#			Select the 'xtab_datanames' columns from sqlite for the row headers and xtab_vals
	#			Append the first result (set warning if >1) to the output line
	#	Write the output line
	#
	# Get a list of unique combinations of row headers
	sqlcmd = "SELECT DISTINCT %s FROM %s;" % (",".join(rownames), tablename)
	row_hdr_vals = sqldb.execute(sqlcmd).fetchall()
	row_counter = 0

	for l in row_hdr_vals:
		row_counter = row_counter + 1
		col_counter = 0
		outstrings = []
		# Add the row headers to the list of outstrings
		for rn in range(len(l)):
			outstrings.append(l[rn].replace("'", "''"))
		# Make a list of WHERE conditions for the row header variables
		sqlcond = ["%s='%s'" % (rownames[i], l[i].replace("'", "''")) for i in range(len(rownames))]
		for n in xtab_vals:
			col_counter = col_counter + 1
			# Add the WHERE conditions for the crosstab values
			selcond = copy.deepcopy(sqlcond)
			for cn in range(len(xtab_colnames)):
				selcond.append("%s='%s'" % (xtab_colnames[cn], n[cn].replace("'", "''")))
			# Create and execute the SQL to get the data values
			sqlcmd = "SELECT %s FROM %s WHERE %s" % (",".join(xtab_datanames), tablename, " AND ".join(selcond))
			if sql_reporter:
				sql_reporter.log(logging.INFO, "%s" % sqlcmd)
			# <Debugging>
			#print(sqlcmd)
			#return
			# </Debugging>
			data_vals = sqldb.execute(sqlcmd).fetchall()
			if sql_reporter:
				for r in data_vals:
					sql_reporter.log(logging.INFO, "\t%s" % "\t".join(r))
			if len(data_vals) > 1:
				multiple_vals = True
				if error_reporter:
					error_reporter.log(logging.WARNING, "Multiple result rows for the command '%s'--only the first is used." % (sqlcmd))
			if len(data_vals) == 0:
				for n in range(len(xtab_datanames)):
					outstrings.append('')
			else:
				data = data_vals[0]
				for n in range(len(xtab_datanames)):
					outstrings.append(data[n])
		csvout.writerow(outstrings)
	sqldb.close()
	if file_db and not keep_file_db:
		try:
			os.unlink(sqldbname)
		except:
			pass
	outfile.close()
	if multiple_vals and not error_reporter:
		msg = "Warning: multiple data values found for at least one crosstab cell; only the first is displayed."
		print(msg)
		if error_reporter:
			error_reporter(msg)


def unquote(str):
	"""Remove quotes surrounding a string."""
	if len(str) < 2:
		return str
	c1 = str[0]
	c2 = str[-1:]
	if c1==c2 and (c1=='"' or c1=="'"):
		return str[1:-1].replace("%s%s" % (c1, c1), c1)
	return str


def quote_str(str):
	"""Add single quotes around a string."""
	if len(str) == 0:
		return "''"
	if len(str) == 1:
		if str == "'":
			return "''''"
		else:
			return "'%s'" % str
	if str[0] != "'" or str[-1:] != "'":
		return "'%s'" % str.replace("'", "''")
	return str


def quote_list(l):
	"""Add single quotes around all strings in the list."""
	return [quote_str(x) for x in l]


def quote_list_as_str(l):
	"""Convert a list of strings to a single string of comma-delimited, quoted tokens."""
	return ",".join(quote_list(l))

	
def copy_to_sqlite(data_fn, sqlite_fn=None, tablename="src"):
	"""Copies data from a CSV file to a sqlite table.
	Arguments:
		data_fn: a string of the data file name with the data to be read.
		sqlite_fn: a string of the name of the sqlite file to create, or None if 
			sqlite is to use memory instead.
		tablename: the name of the sqlite table to create
	Value:
		The sqlite connection object.
	"""
	dialect = csv.Sniffer().sniff(open(data_fn, "rt").readline())
	inf = csv.reader(open(data_fn, "rt"), dialect)
	column_names = inf.next()
	if sqlite_fn == None:
		conn = sqlite3.connect(":memory:")
	else:
		try:
			os.unlink(sqlite_fn)
		except:
			pass
		conn = sqlite3.connect(sqlite_fn)
	if tablename == None:
		tablename = "src"
	colstr = ",".join(column_names)
	try:
		conn.execute("drop table %s;" % tablename)
	except:
		pass
	conn.execute("create table %s (%s);" % (tablename, colstr))
	for l in inf:
		sql = "insert into %s values (%s);" % (tablename, quote_list_as_str(l))
		conn.execute(sql)
		conn.commit()
	return conn


def print_help():
	"""Print a program description and brief usage instructions to the console."""
	print "xtab %s %s -- Cross-tabulates data." % (_version, _vdate)
	print __help_msg

	
def get_opts(arglist):
	"""Returns a dictionary of command-line arguments.  This custom 'getopt' routine is used
	to allow multiple column names for the -r, -c, and -v arguments with only one use of each
	flag.
	"""
	argdict = {}
	nargs = len(arglist)
	argno = 1
	currarg = None
	currargitems = []
	while argno < nargs:
		arg = arglist[argno]
		if len(arg) > 0:
			if arg[0] == '-':
				if currarg:
					argdict[currarg] = currargitems
				currarg = arg
				currargitems = []
			else:
				if currarg:
					currargitems.append(arg)
				else:
					argdict[arg] = []
		argno += 1
	if currarg:
		argdict[currarg] = currargitems
	return argdict


def main():
	"""Read and interpret the command-line arguments and options, and carry out
	the appropriate actions."""
	args = get_opts(sys.argv)
	if len(args) == 0 or args.has_key('-h'):
		print_help()
		sys.exit(0)
	if args.has_key('-i'):
		if len(args['-i']) == 0:
			raise ValueError, _errmsg_noinfile
		infilename = args['-i'][0]
		if not os.path.exists(infilename):
			raise ValueError, "%s (%s)" % (_errmsg_badinfile, infilename)
	else:
		raise ValueError, _errmsg_noinfile
	#
	if args.has_key('-o'):
		if len(args['-o']) == 0:
			raise ValueError, _errmsg_nooutfile
		outfilename = args['-o'][0]
	else:
		raise ValueError, _errmsg_nooutfile
	#
	if args.has_key('-r'):
		if len(args['-r']) == 0:
			raise ValueError, _errmsg_norowheaders
		rowheaders = args['-r']
	else:
		raise ValueError, _errmsg_norowheaders
	#
	if args.has_key('-c'):
		if len(args['-c']) == 0:
			raise ValueError, _errmsg_nocolumheaders
		columnheaders = args['-c']
	else:
		raise ValueError, _errmsg_nocolumheaders
	#
	if args.has_key('-v'):
		if len(args['-v']) == 0:
			raise ValueError, _errmsg_nocellcolumns
		cellvalues = args['-v']
	else:
		raise ValueError, _errmsg_nocellcolumns
	#
	doubleheaders = args.has_key('-d')
	file_db = args.has_key('-f')
	keep_file_db = args.has_key('-k')
	tablename = 'src'
	if args.has_key('-t'):
		if len(args['-t']) == 1:
			tablename = args['-t'][0]
	#
	# Set up logging
	#logging.basicConfig(level=logging.INFO, filemode="w", filename='')
	err_logger = None
	sql_logger = None
	if args.has_key('-e'):
		err_logger = logging.getLogger("err")
		err_logger.setLevel(logging.WARNING)
		if len(args['-e']) == 0:
			err_logger.addHandler(logging.StreamHandler())
		else:
			if len(args['-e']) > 1:
				raise ValueError, _errmsg_baderrlogfile
			err_logger.addHandler(logging.FileHandler(args['-e'][0], "w"))
	if args.has_key('-q'):
		if len(args['-q']) <> 1:
			raise ValueError, _errmsg_badsqllogfile
		sql_logger = logging.getLogger("sql")
		sql_logger.setLevel(logging.INFO)
		sql_logger.addHandler(logging.FileHandler(args['-q'][0], "w"))
	#
	xtab(infilename, rowheaders, columnheaders, cellvalues, outfilename, doubleheaders,
	 file_db, keep_file_db, tablename,
	 err_logger, sql_logger)


if __name__=='__main__':
	main()

