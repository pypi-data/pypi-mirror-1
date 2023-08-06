#!/usr/bin/env python

# NOTE: ok, but I would put some doctest in datamatrix.py anyway, to illustrate its usage
import datamatrix
import unittest
from StringIO import StringIO

def toUpper(string):

    "Simple function required for tests. Returns an uppercase string."

    return string.upper()

def concatenate(sequence):

    "Function needed to test matrixApply. Concatenates sequences by '-'."

    return '-'.join(sequence)

def isNumber(number):

    "Checks if a number is an int. Used to test filterMatrix."

    if isinstance(number, int):
        return True
    else:
        return False

class DataMatrixTests(unittest.TestCase):

    def setUp(self):

        matrixFile = StringIO('Name surname\nAlbert Einstein\nGroucho Marx')
        self.matrix = datamatrix.DataMatrix(matrixFile, header=True,
                delimiter=" ")
        self.skippedMatrix = datamatrix.DataMatrix(matrixFile, header=True,
                                                   delimiter= " ", skip=1)
        self.skippedMatrixNoHeader = datamatrix.DataMatrix(matrixFile,
                                                           header=False,
                                                           delimiter=" ",
                                                           skip=1)

    def testBasics(self):

        "Test length of rows and columns"

        self.assertEqual(len(self.matrix),2)
        self.assertEqual(len(self.matrix.columns),2)

    def testRowSkip(self):

        "Test row skipping when reading a file"

        value = self.skippedMatrix.getRow(1)
        self.assertEqual(value, ['1','Groucho', 'Marx'])

    def testRowSkipNoHeader(self):

        "Test row skipping when reading a file with no header"

        value = self.skippedMatrixNoHeader.getRow(1)
        self.assertEqual(value,['1', 'Albert', 'Einstein'])

    def testIndexing(self):

        "Test indexing and __contains__ special method"

        self.assertEqual(self.matrix["Name"],
                ['Albert', 'Groucho'])
        self.assertEqual(self.matrix["surname"],
                ['Einstein', 'Marx'])
        self.assert_("Name" in self.matrix)
        self.assert_("nonexistent" not in self.matrix)

    def testGetColumns(self):

        "Test getColumns with and without column name"

        self.assertEqual(self.matrix.columns,["Name","surname"])
        value = self.matrix["Name"]
        self.assertEqual(value,['Albert', 'Groucho'])

    def testColumnList(self):

        "Test columns output"

        self.assertEqual(self.matrix.columns,["Name","surname"])

    def testGetRows(self):

        "Test getRow with all, a subset of columns and without row name"

        row = self.matrix.getRow(1)
        self.assertEqual(row,["1","Albert","Einstein"])
        row = self.matrix.getRow(1,columns=["surname"])
        self.assertEqual(row,["1","Einstein"])
        row = self.matrix.getRow(1, row_name = False)
        self.assertEqual(row, ["Albert", "Einstein"])

    def testGetRowsByID(self):

        "Test getRowByID with all and a subset of columns"

        row = self.matrix.getRowByID("1")
        self.assertEqual(row,["1","Albert","Einstein"])
        row = self.matrix.getRowByID("1",columns=["surname"])
        self.assertEqual(row,["1","Einstein"])

    def testAppend(self):

        "Test appending, both rows and columns"

        data = ["Isaac","Asimov"]
        self.matrix.appendRow(data,"3")
        row = self.matrix.getRow(3)
        self.assertEqual(row, ["3","Isaac","Asimov"])
        column = ["scientist", "comedian", "writer"]
        self.matrix.append(column, "Profession")
        self.assertEqual(self.matrix["Profession"],
                [ "scientist", "comedian","writer"])

    def testInsert(self):

        "Test insertion of rows and columns"

        data = ["Isaac","Asimov"]
        self.matrix.insertRow(data,"3",1)
        row = self.matrix.getRow(2)
        self.assertEqual(row, ["3","Isaac","Asimov"])
        column = ["scientist", "writer", "comedian"]
        self.matrix.insert(column, "Profession",1)
        self.assertEqual(self.matrix["Profession"],
        ["scientist", "writer","comedian"])

    def testPop(self):

        "Test pop() function"

        pop = self.matrix.pop()
        self.assertEqual(pop,["2","Groucho","Marx"])

    def testWriteMatrix(self):

        "Test writeMatrix by writing and reading the result back"

        destination = StringIO()
        datamatrix.writeMatrix(self.matrix,destination, delimiter=" ",
                header=True)
        destination.seek(0)
        value = destination.readline()
        self.assertEqual(value, 'x Name surname\n')

    def testWritePartial(self):

        "Test writeMatrix with a subset of columns"

        destination = StringIO()
        datamatrix.writeMatrix(self.matrix,destination, delimiter=" ",
                header=True, columns = ["Name"])
        destination.seek(0)
        value = destination.readline()
        self.assertEqual(value, 'x Name\n')

    def testApply(self):

        "Test of the apply function to a column"

        datamatrix.apply(self.matrix, toUpper, "Name")
        column = self.matrix["Name"]
        self.assertEqual(column, ["ALBERT", "GROUCHO"])

    def testElementApply(self):

        "Test applying a function to rows and columns"

        result = datamatrix.elementApply(self.matrix, toUpper)
        row = result.getRow(1)
        self.assertEqual(row, ["1", "ALBERT", "EINSTEIN"])

    def testMatrixApply(self):

        "Test concatenating rows or columns with '-' using matrixApply"

        result = datamatrix.matrixApply(self.matrix, concatenate,
                                        what = "rows")
        row = result.getRow(1, row_name=False)
        self.assertEqual(row, ["Albert-Groucho", "Einstein-Marx"])

        result = datamatrix.matrixApply(self.matrix, concatenate,
                                        what = "columns")
        column = result["Function result"]
        self.assertEqual(column, ["Albert-Einstein", "Groucho-Marx"])

    def testFilterMatrix(self):

        "Test filtering matrix only by rows that contain numbers"

        data = [1234, 3456]
        self.matrix.appendRow(data, "3")

        result = datamatrix.filterMatrix(self.matrix, isNumber, "Name")
        self.assertEqual(len(result), 1) # One row only survived the filter
        self.assertEqual(result.getRow(1, row_name = False), data)

    def testRbind(self):

        "Test joining two matrices by rows"

        matrixFile = StringIO('Name surname\nIsaac Asimov\nJohn Watson')
        matrix = datamatrix.DataMatrix(matrixFile, header=True, 
                delimiter=" ")
        new_matrix = datamatrix.rbind(self.matrix, matrix)
        self.assertEqual(new_matrix.getRow(3), ["3","Isaac", "Asimov"])
        self.assertEqual(len(new_matrix), 4)
        self.assertEqual(new_matrix.getRowByID("4"), ["4", "John", "Watson"])

    def testCbind(self):

        "Test joining two matrices by columns"

        matrixFile = StringIO(
            'Job Skills\nscientist relativity\ncomedian humor'
        )
        matrix = datamatrix.DataMatrix(matrixFile, header=True, 
                delimiter=" ")
        new_matrix = datamatrix.cbind(self.matrix, matrix)
        self.assertEqual(new_matrix["Job"], ["scientist", "comedian"])
        self.assertEqual(new_matrix.getRow(2), 
                         ["2", "Groucho", "Marx", "comedian", "humor"])


def runTests():

    suite = unittest.TestLoader().loadTestsFromTestCase(DataMatrixTests)
    unittest.TextTestRunner(verbosity=2).run(suite)

