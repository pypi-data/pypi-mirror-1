xtab.py
Crosstabulate data in a text file.

xtab.py is a Python module and command-line program that rearranges data from
a normalized format to a crosstabulated format.

Contents
======================

  Installation
  Capabilities
  Required and Optional Arguments
  Notes
  Copyright and License


Installation
======================

You can install the program either manually or using Python's installation tools.


Manual Installation
--------------------

Because the functionality of the xtab program is contained in a single
Python script, you can simply extract the xtab.py script from the zipped
package file, and put the script wherever you want.  This may be in the
standard location for Python scripts, or in any other location from which you
want to execute it.


Automated Installation
-----------------------

The automated installation process uses Python's standard setup tool to place
the program in the standard location for third-party scripts (e.g., 
C:\Python\Scripts or C:\Program Files\Python\Scripts).  Follow these steps to 
perform an automated installation:

1. Unzip the package file.  The file can be unzipped in a temporary location,
   such as C:\Temp.  The contents of the package will be placed in a
   subdirectory named for the program and release version.
2. Open a command window in the subdirectory containing the unzipped files and
   type the following command at the prompt:

		python setup.py install

If you want to install to a non-standard location, instructions for a
customized installation can be found at
http://docs.python.org/install/index.html#inst-alt-install.



Capabilities
======================

You can use the xtab program to:

  * Rearrange data exported from a database to better suit its 
    subsequent usage in statistical, modeling, graphics, or other
    software, or for easier visual review and table preparation.
  * Convert a single file (table) of data to a SQLite database.
  * Check for multiple rows of data in a text file with the same
    key values.


Required and Optional Arguments
================================

Required Arguments
-------------------

-i <filename>
    The name of the input file from which to read data. This must be a text file,
    with data in a normalized format. The first line of the file must contain
    column names.

-o <filename>
    The name of the output file to create. The output file will be created as
    a .csv file. 

-r <column_name1> [column_name2 [...]]
    One or more column names to use as row headers (space delimited). Unique
    values of these columns will appear at the beginning of every output line.

-c <column_name1> [column_name2 [...]]
    One or more column names to use as column headers in the output (space
    delimited). A crosstab column (or columns) will be created for every unique
    combination of values of these fields in the input.

-v <column_name1> [column_name2 [...]]
    One or more column names with values to be used to fill the cells of the
    cross-table. If n columns names are specified, then there will be n columns
    in the output table for each of the column headers corresponding to values
    of the -c argument. The column names specified with the -v argument will
    be appended to the output column headers created from values of the -c
    argument. There should be only one value of the -v column(s) for each
    combination of the -r and -c columns; if there is more than one, a warning
    will be printed and only the first value will appear in the output.
    (That is, values are not combined in any way when there are multiple values
    for each output cell.) 


Optional Arguments
-------------------

-d
    Prints output column headers in two rows. The first row contains values
    of the columns specified by the -h argument, and the second row contains
    the column names specified by the -v argument. If this is not specified,
    output column headers are printed in one row, with elements joined by
    underscores to facilitate parsing by other programs.

-f
    Use a temporary (sqlite) file instead of memory for intermediate storage.

-k  Keep (i.e., do not delete) the sqlite file. Only useful with the "-f" option.
    Unless the "-t" option is also used, the table name will be "src".

-t <tablename>
    Name to use for the table in the intermediate sqlite database. Only useful
    with the "-f" and "-k" options.

 -e [filename]
    Log all error messages, to a file if the filename is specified or to the
    console (stderr) if the filename is not specified.

 -q <filename>
    Log the sequence of SQL commands used to extract data from the input file
    to write the output file, including the result of each command.

 -h
    Print a summary of the command-line arguments and exit. 


Notes
======================

  * Multiple data values can be crosstabbed, in which case the output
    will contain multiple sets of similar columns.
  * Either one or two rows of headers can be produced in the output file.
    One row is the default, and is most suitable when the output file will
    be further processed by other software.  Two rows facilitate readability
    when the output contains multiple sets of similar columns.
  * The xtab program does not carry out any summarization or
    calculation on the data values, and therefore there should be
    no more than one data value to be placed in each cell of the output
    table. More than one value per cell is regarded as an error, and in
    such cases only one of the multiple values will be put in the cell.
  * Error messages can be logged to either the console or a file.  If no
    error logging option is specified, then if there are multiple values
    to be put in a cell (the most likely data error), a single message
    will be printed on the console indicating that at least one error of
    this type has occurred. If an error logging option is specified,
    then the SQL for all individual cases where there are multiple values
    per cell will be logged.
  * The SQL commands used to extract data from the input file for each
    output table cell can be logged to a file.
  * As an intermediate step in the crostabbing process, data are converted
    to a SQLite table. By default, this table is created in memory.  
    However, it can optionally be created on disk, and preserved so that
    it is available after the crosstabulation is completed.
  * There are no inherent limits to the number of rows or columns in the
    input or output files. (So the output may exceed the limits of some
    other software.)
  * Input and output file names, and column names in the input file that
    are to be used for row headings, column headings, and cell values are
    all required as command-line arguments.  If any required arguments are
    missing, an exception will be raised, whatever the error logging option.


Copyright and License
======================

Copyright (c) 2008, R.Dreas Nielsen

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details. The GNU General Public License is available at
http://www.gnu.org/licenses/.
