from __future__ import with_statement

import os
import pickle
import sys
import unittest
import logging

APP_ROOT = os.getenv('APP_ROOT')

sys.path.insert(0, '%s/pypatterns/src' % APP_ROOT)
sys.path.insert(0, '%s/currypy/src' % APP_ROOT)
import currypy

import pypatterns.filter as FilterModule
import pypatterns.relational as RelationalModule

sys.path.insert(0,"../data")

class TestCase(unittest.TestCase):

    COLUMNS = ['column1', 'column2', 'column3']

    PICKLE_PATH = os.path.sep + os.path.join('tmp', 'TestRelationalPickle.pickle')

    def setUp(self):
        return
    
    def tearDown(self):
        if os.path.exists(TestCase.PICKLE_PATH):
            os.unlink(TestCase.PICKLE_PATH)
        return
    
    
    def testTable(self):
        columns = TestCase.COLUMNS
        table = RelationalModule.createTable('test',columns)

        rowValuesList = [
            [1,2,3],
            [1,'2','3'],
            [None,None,[]]
        ]
        for rowValues in rowValuesList:
            row = table.addRow()
            map(row.setColumn, columns, rowValues)

        self.assertPickleable(table)

        return
    
    
    def testRow(self):
        columns = TestCase.COLUMNS
        table = RelationalModule.createTable('test',columns)

        expectedValues = [1,2,3]
        row1 = table.addRow()
        map(row1.setColumn, columns, expectedValues)
        for column, expectedValue in zip(columns, expectedValues):
            assert row1.getColumn(column) == expectedValue
            pass

        self.assertPickleable(row1)
        
        return



    def assertPickleable(self, objectToPickle):
        with open(TestCase.PICKLE_PATH, 'w') as f:
            pickle.dump(objectToPickle, f)

        with open(TestCase.PICKLE_PATH, 'r') as f:
            newObject = pickle.load(f)
        return



    # END class TestCase
    pass





def main():
    suite = unittest.makeSuite(TestCase,'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
    return

if __name__=="__main__":
    main()

