#!/usr/bin/env python

# ---------------------------------------------------------------------------
# (C) 2008 Luca Beltrame (einar at heavensinferno dot net)
# (C) 2008 Giovanni Marco Dall'Olio (dalloliogm at gmail dot com)
# This program is distributed under the terms of the GNU General Public
# License (GPL), version 2. See the file COPYING for details.
# ---------------------------------------------------------------------------

"Module providing a Pythonic implementation of a data.frame."

from __future__ import division

import os
import csv
import copy

__author__ = "Luca Beltrame"
__copyright__ = "Copyright 2008, Luca Beltrame, Giovanni Marco Dall'Olio"
__license__ = "GPL (v2)"
__version__ = "0.8"
__status__ = "Development"

class DataMatrix(object):

    """Pythonic implementation of R's data.frame structure.
    This class loads a file or a file-like structure then it
    transforms it into a dictionary of (row name, value) tuples for
    each column. Optionally only column values can be retrieved and
    at the same time single lines can be queried.
    Missing values are inputted as NAs.

    The column used for row names (row_names) can be specified,
    otherwise rows are numbered sequentially. If the file has
    an header (default True), it is used to name the fields, otherwise the
    fields are numbered sequentially, with the first field
    being "x" (like R does).

    If you are loading a text object saved by R using row.names=TRUE, the
    topmost, leftmost record will be blank. To parse such files, specify fixR as
    True in the initializer options.

    Other options include the delimiter, line terminator and quoting,
    and they are passed directly to the csv DictReader instance which will
    read the file. See the csv module documentation for more details.

    Notable methods are:
        - getRow - returns a specific row
        - view - Outputs a tab-delimited view of a number of
            lines. Start line and how much to show are configurable.
        - append - adds a column (of the same length and with the same
            identifiers) to the matrix, kind of equivalent to R's cbind.
        - appendRow - adds a row at the end of the matrix, of the same length as
            the columns. It can be seen as similar to R's rbind.
        - insert - inserts a column at a specified index
        - insertRow - similar to insert, but works with rows
        - iterRows - cycle through rows
        - getRowByID - get a row with a specified row name
    """

    def __init__(self,fh=None,row_names=None,header=True, delimiter="\t",
                quoting=csv.QUOTE_MINIMAL, fixR=False):

        self._records = dict()
        self.rownames = list()

        if not hasattr(fh,"read"):
            # Check for the existence of the read method
            raise TypeError(unicode("File-like object expected"))

        if hasattr(fh, "name"):
            self.filename = os.path.basename(fh.name)
            # this is False for filehandlers like StringIO
        else:
            self.filename = ''

        self.identifier = None
        self.has_header = header

        # Check if row_names actually exists before doing any math with it
        if row_names:
            row_names = row_names - 1

        # Since csv.DictReader doesn't return fieldnames
        # if auto-detected before the first iteration, and
        # we need them before iterating, we get the first line
        # of the file

        fh.seek(0) # to make sure

        if header:
            heading = fh.next()
            #FIXME: Possibly unsafe in certain situations
            heading = heading.strip()
            heading = heading.split(delimiter)
            # Work around R's broken table saving
            # It cannot be auto-detected, though
            if fixR:
                heading.insert(0,"x")
        else:
            heading = fh.next()
            heading = heading.strip()
            heading = heading.split(delimiter)
            heading = ["Column " + str(index[0]+1)
                       for index in enumerate(heading)]
            fh.seek(0)

        self.columns = copy.copy(heading)
        count = 1

        if row_names is not None:
            self.identifier = heading[row_names]
            self.columns.remove(self.identifier)

        for field in self.columns:
            self._records[field] = list()

        reader = csv.DictReader(fh,fieldnames=heading,
                    delimiter=delimiter,quoting=quoting,
                    restval="NA")

        for row in reader:
            if self.identifier is not None:
                row_id = row[self.identifier]
                self.rownames.append(row_id)
            else:
                self.rownames.append(str(count))
            for field in self.columns:
                if self.identifier is not None:
                    self._records[field].append((row_id,row[field]))
                else:
                    self._records[field].append((str(count),row[field]))
            count += 1

   # Special methods
    def __str__(self):

        if self._records:
            column_no = "No. of columns: %d" % len(self._records)
            columns = ', '.join(self.columns)
            columns = ' '.join(("Columns:",columns))
            names = self.identifier if self.identifier is not None else \
                        "None (numeric)"
            row_name = "Column with identifier names: %s" % names
            rows = "No. of rows: %d" % len(self)
            name = ' '.join(("File name:", self.filename))
            output = os.linesep.join((name, row_name, rows, column_no,
                        columns))
            return output

    def __getitem__(self, key):

        if key not in self._records:
            raise KeyError, unicode("No such column")
        
        column_data = list()

        for record in self._records[key]:
            column_data.append(record[1])
        return column_data

    def __iter__(self):

        for column in self.columns:
            yield column

    def __contains__(self, key):

        if key in self._records:
            return True
        else:
            return False

    def __len__(self):
        return len(self.rownames)

    def __delitem__(self, key):

        if key not in self._records:
            raise KeyError(unicode("No such column"))

        del self._records[key]
        self.columns.remove(key)

    def __setitem__(self, key, item):

        if len(item) != len(self):
            raise ValueError(unicode(
                    "Attempted addition of an item of unequal length"))

        self._records[key] = item

    def iterRows(self,**kwargs):
        """Iterate over a matrix's rows.

        >>> from StringIO import StringIO
        >>> matrixfile = StringIO(
        ... '''a b c d
        ... 3 3 3 3
        ... 2 2 2 2''')

        >>> matrix =  DataMatrix(matrixfile)
        >>> for row in matrix.iterRows():
        ...     print row
        ['1', '3 3 3 3']
        ['2', '2 2 2 2']

        """

        for row_no, row in enumerate(self.rownames):
            yield self.getRow(row_no+1,**kwargs)

    # Other methods

    def getColumn(self, key, column_name=False):

        """Gets a specific column, without the
        identifier. The result is returned as a list.
        Optionally the column name can be printed.
        DEPRECATED: Use datamatrix[colname] instead."""

        if key not in self._records:
            raise KeyError(unicode("No such column"))

        column_data = list()

        if column_name:
            column_data.append(key)

        for record in self._records[key]:
            column_data.append(record[1])
        return column_data

    def getRow(self, row_number,columns = "all", row_name = True):

        """Returns a specific row, identified from the
        row number, as a list. You can specify how many
        columns are outputted (default: all) with the columns parameter."""

        row = list()

        # We use self.columns instead of self._records.keys() to keep
        # the column order
        records = self.columns if columns == "all" else columns
        # row_name = self._records[self.columns[0]][row_number-1]
        row_id = self.rownames[row_number-1]
        #row_name = row_name[0] # Get the identifier out of the tuple
        if row_name:
            row.append(row_id)
        for record in records:
            value = self._records[record][row_number-1][1]
            row.append(value)

        return row

    def getRowByID(self,rowId,**kwargs):

        """Fetches a specific row basing on the identifier. If there is no
        match, a ValueError is raised."""
        #FIXME: It only works for the first match
        if rowId not in self.rownames:
            raise ValueError(unicode("No such row"))

        for index, rowName in enumerate(self.rownames):
            if rowId == rowName:
                return self.getRow(index+1, **kwargs)

    def view(self, lines=10, start_at=1, *args, **kwargs):

        """Method used to print on-screen the table.
        The number of lines, and the starting line can be
        configured via the start_at and lines parameters.
        Optional parameters can be sent to getRow to
        select which columns are printed."""

        if start_at != 1:
            value = self.getRow(1, *args, **kwargs)
            value = " ".join(value)
            print value

        # Check if we have less lines than default
        # Also, range does not count end so we have to increment by 1
        if len(self) < lines:
            end_at = start_at + len(self)
        else:
            end_at = start_at + lines + 1

        for row in range(start_at, end_at):
            value = self.getRow(row, *args, **kwargs)
            value = " ".join(value)
            print value

    def append(self, other, column_name):

        """Method to append a column. It needs a sequence (tuple or list) and
        a column name to be supplied. The sequence must be of the same length
        as the other columns."""

        # Is it a sequence?
        try:
            test = iter(other)
        except TypeError:
            raise TypeError(unicode(
                "You must supply a sequence object to this method"))

        if len(other) != len(self):
            print "Other", other
            raise ValueError(unicode("The column must be of the same length"))
        column_data = list()
        for index,item in enumerate(other):
            data = (self.rownames[index], item)
            column_data.append(data)
        self[column_name] = column_data
        self.columns.append(column_name)

    def appendRow(self, other, row_name):

       """Appends a row to the end of the matrix. The row must encompass all
       the columns (i.e., it should be as long as to cover all the columns).
       The row name is specified in the mandatory parameter row_name."""

       if len(other) != len(self.columns):
           raise ValueError(unicode("Row length mismatch"))

       for index, column in enumerate(self.columns):
           data = self._records[column]
           values = (row_name, other[index])
           data.append(values)
       self.rownames.append(row_name)

    def insert(self,other, column_name, column_no):

        "Method to insert a column at a specified column index."

        if len(other) != len(self):
            raise ValueError(unicode("The column must be of the same length"))

        # If we specify a column number greater than the number of columns,
        # we append the result

        if column_no >= len(self):
            self.append(other, column_name)
            return

        self.columns.insert(column_no,column_name)

        column_data = list()

        for index,item in enumerate(other):
           data = (self.rownames[index], item)
           column_data.append(data)

        self[column_name] = column_data

    def insertRow(self, other, row_name, lineno):

        "Method that inserts a row at a specified line number."

        if len(other) != len(self.columns):
           raise ValueError(unicode("Row length mismatch"))

        # Append if the line number is greater than the row names

        if lineno >= len(self.rownames):
            self.appendRow(other, row_name)
            return

        self.rownames.insert(lineno, row_name)

        for index, column in enumerate(self.columns):
           data = self._records[column]
           values = (row_name, other[index])
           data.insert(lineno,values)

    def pop(self, index=-1):

        """Method analogous to the pop method of lists, with the difference
        that this one removes rows and returns the removed item. If no index
        (a.k.a. row number) is supplied, the last item is removed."""

        index = index-1 if index != -1 else index
        row_number = len(self) if index == -1 else index
        popped_value = self.getRow(row_number)

        for column in self.columns:
            data = self[column]
            data.pop(index)
        self.rownames.pop(index)

        return popped_value

    def replace(self, other, colName):

        "Replace a column with another."

        if colName not in self:
            raise KeyError(unicode("Unknown column"))

        if len(self) != len(other):
            raise ValueError(unicode("Column length mismatch"))

        colData = list()
        for index, item in enumerate(other):
            element = (self.rownames[index], item)
            colData.append(element)

        self[colName] = colData

def elementApply(matrix, func):

    """Applies a function to each element of rows or columns, and outputs a new
    matrix as result. If the function requires any type conversion, that must be done
    by the user."""

    assert isinstance(matrix, DataMatrix)

    resultMatrix = EmptyMatrix(columns = matrix.columns,
            identifier=matrix.identifier)
    for row in matrix.iterRows():
        newRow = [func(item) for item in row[1:]]
        resultMatrix.appendRow(newRow,row[0])

    return resultMatrix

def matrixApply(matrix, func, what="rows", resultName="Function result"):

    """Apply a user-specified function to all rows or all columns. If the
    function requires any type conversion, that must be done by the user. The
    function must process the row (or the column) and return a single value.
    The final result is a DataMatrix instance containing one row (or one
    column) with the function results. The name of the column (or row) can be
    changed with the resultName parameter.
    """

    assert isinstance(matrix, DataMatrix)

    if what == "rows":
        resultMatrix = EmptyMatrix(columns = matrix.columns,
                identifier=matrix.identifier)
        result = list()

        for column in matrix:
            columnData = matrix[column]
            resultData = func(columnData)
            result.append(resultData)
            
        resultMatrix.appendRow(result,resultName)

    elif what == "columns":
        resultMatrix = EmptyMatrix(identifier=matrix.identifier,
                row_names=matrix.rownames)
        result = list()
        for row in matrix.iterRows():
            functionData = func(row[1:])
            result.append(functionData)

        resultMatrix.append(result, resultName)

    return resultMatrix

def filterMatrix(matrix, func, column):

    """Function which returns a DataMatrix with a column that satisfies specified
    criteria. In particular, "func" must be a function applied to the each row
    (on the column of interest) and should return
    True if the row needs to be included, and False otherwise."""

    assert isinstance(matrix, DataMatrix)

    resultMatrix = EmptyMatrix(identifier=matrix.identifier, columns =
        matrix.columns)

    columnData = matrix[column]

    for index,row in enumerate(matrix.iterRows()):

        value = columnData[index]

        if func(value):
            # We need the whole row, not just the selection  
            rowData = row[1:] # Get the ID iout
            resultMatrix.appendRow(rowData, row[0])
        else:
            continue

    return resultMatrix

def writeMatrix(data_matrix,fh = None,delimiter = "\t",
                lineterminator = os.linesep,quoting = csv.QUOTE_MINIMAL,
                header = False, row_names = True, *args, **kwargs):

    """Function that saves DataMatrix objects to files or file-like
    objects. A file handle is a mandatory parameter, along with the data
    matrix object you want to use. You can optionally pass more parameters to
    getRows to select which columns are saved."""

    assert isinstance(data_matrix,DataMatrix)

    writer = csv.writer(fh,lineterminator=lineterminator,
                    delimiter=delimiter,quoting=quoting)
    if header:
        heading = copy.copy(data_matrix.columns)

        if "columns" in kwargs and kwargs["columns"] != "all":
            heading = copy.copy(kwargs["columns"])

        if row_names:
            if data_matrix.identifier:
                heading.insert(0,data_matrix.identifier)
            else:
                heading.insert(0,"x")

        writer.writerow(heading)

    for row in range(1,len(data_matrix)+1):
        value = data_matrix.getRow(row, row_name = row_names, *args,**kwargs)
        writer.writerow(value)

def _mean(values):
    values = [float(item) for item in values]
    return sum(values) / len(values)

def _median(values):
    values = ([float(item) for item in values])
    sortedValues = sorted(values)
    length = len(values)
    if length & 1:         # There is an odd number of elements
        return sortedValues[length /2]
    else:
        return (sortedValues[length / 2 - 1] + sortedValues[length / 2]) / 2

def meanColumns(sourceMatrix):

    "Calculates the mean of all columns for each row."

    return matrixApply(sourceMatrix, _mean, resultName="Mean value", what="columns")
        
def meanRows(sourceMatrix):

    "Calculates the mean of all rows for each columns."

    return matrixApply(sourceMatrix, _mean, resultName="Mean value", what="rows")

def transpose(matrix, identifier="x"):

    """Transposes a DataMatrix object: rows become columns and vice versa. The
    optional parameter ``identifier`` is passed as the resulting matrix's
    identifer name."""

    destination = EmptyMatrix(identifier = identifier,
                              row_names = matrix.columns)
    for index in range(0, len(matrix.rownames)):
        row_index = index + 1
        column = matrix.getRow(row_index, row_name=False)
        destination.append(column, matrix.rownames[index])
    
    return destination


class EmptyMatrix(DataMatrix):

    """DataMatrix variant that once instantiated generates an
    empty matrix with specified columns and row names.
    Does not depend upon reading a file.
    Rows and columns, after initialization, can be added with insertRows,
    insert, appendRows and append methods, respectively."""

    def __init__(self, identifier = None, row_names = None, columns = None):

        self.rownames = row_names if row_names else list()
        self._records = dict()
        self.columns = list() if not columns else columns
        self.identifier = identifier

        for column in self.columns:
            self._records[column] = list()

def _test():
    import doctest
    doctest.testfile('../tutorial.txt')
    doctest.testmod()
    import test_datamatrix
    test_datamatrix.runTests()

if __name__ == '__main__':
    _test()
