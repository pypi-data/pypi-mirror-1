import unittest
from scanbooker.dom.testunit import TestCase
import mx.DateTime

def suite():
    suites = [
        unittest.makeSuite(TestReport),
    ]
    return unittest.TestSuite(suites)


class TestReport(TestCase):

    reportTitle = 'Test Example Report'
    reportAgainst = 'ScanningSession'

    def setUp(self):
        self.createReport()
        self.createScanningSessions()

    def createReport(self):
        self.report = self.registry.reports.create(
            title=self.reportTitle,
            against=self.reportAgainst,
        )

    def createScanningSessions(self):
        self.sessions = []
        self.sessions.append(self.registry.scanningSessions.create(
            starts=mx.DateTime.DateTime(2008, 1, 1, 9, 0, 0),
            ends=mx.DateTime.DateTime(2008, 1, 1, 10, 0, 0),
        ))
        self.sessions.append(self.registry.scanningSessions.create(
            starts=mx.DateTime.DateTime(2008, 1, 1, 10, 0, 0),
            ends=mx.DateTime.DateTime(2008, 1, 1, 11, 0, 0),
        ))
        self.sessions.append(self.registry.scanningSessions.create(
            starts=mx.DateTime.DateTime(2008, 1, 1, 11, 0, 0),
            ends=mx.DateTime.DateTime(2008, 1, 1, 12, 0, 0),
        ))

    def tearDown(self):
        self.report.delete()
        for s in self.sessions:
            s.delete()
    
    def test_attributes(self):
        self.failUnlessEqual(self.report.title, self.reportTitle)
        self.failUnlessEqual(self.report.against, self.reportAgainst)
    
    def test_columns(self):
        self.report.columns.create(name='id')
        self.failUnlessEqual(self.report.listColumns()[0].name, 'id')
        self.failUnlessEqual(self.report.listColumns()[0].qual, 'label')

    def test_filters(self):
        self.report.filters.create(name='id')
        self.failUnlessEqual(self.report.listFilters()[0].name, 'id')
        self.failUnlessEqual(self.report.listFilters()[0].mode, 'equal to')

    def test_generateDataEmpty(self):
        data = self.report.generateData()
        self.failUnlessEqual(data, [['Please add some column names.']])

    def test_generateDataOneColumnNoFilter1(self):
        self.report.columns.create(name='id')
        data = self.report.generateData()
        reqd = [['#%s' % s.id] for s in self.sessions]
        self.failUnlessEqual(data, reqd)

    def test_generateDataOneColumnNoFilter2(self):
        self.report.columns.create(name='starts')
        data = self.report.generateData()
        reqd = [[s.asDictLabels()['starts']] for s in self.sessions]
        self.failUnlessEqual(data, reqd)

    def test_generateDataOneColumnNoFilter3(self):
        self.report.columns.create(name='starts', qual='value')
        data = self.report.generateData()
        reqd = [[s.asDictValues()['starts']] for s in self.sessions]
        self.failUnlessEqual(data, reqd)

    def test_generateDataOneColumnOneFilter1(self):
        self.report.filters.create(name='id')
        self.report.columns.create(name='starts', qual='value')
        data = self.report.generateData()
        reqd = [[s.asDictValues()['starts']] for s in self.sessions]
        self.failUnlessEqual(data, reqd)

