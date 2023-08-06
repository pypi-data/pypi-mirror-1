import unittest
from dm.migratetest import TestDomainModelLoader
from dm.migrate import DomainModelLoader

# Todo: Fold this back into the dm.migratetest module, when dm.dom.builder
# has some objects with properties that reference objects of the same type.


def suite():
    suites = [
        unittest.makeSuite(TestDomainModelLoader),
    ]
    return unittest.TestSuite(suites)


class TestDomainModelLoader(TestDomainModelLoader):

    def setUp(self):
        self.reports = []
        self.loader = DomainModelLoader()

    def tearDown(self):
        for report in self.reports:
            report.delete()

    def testLoadDataAsJson(self):
        newReport = self.registry.reports.create()
        newColumn = newReport.columns.create()
        lastReportId = newReport.id
        lastColumnId = newColumn.id
        newReport.delete()
        newColumn.delete()
        reportId1 = lastReportId + 1
        reportId2 = lastReportId + 2
        reportTitle1 = "migrated report 1"
        reportTitle2 = "migrated report 2"
        columnId1 = lastColumnId + 1
        columnId2 = lastColumnId + 2
        columnId3 = lastColumnId + 3
        columnId4 = lastColumnId + 4
        columnName1 = "migrated column 1"
        columnName2 = "migrated column 2"
        columnName3 = "migrated column 3"
        columnName4 = "migrated column 4"
        jsonString = """{
            "Report": {
                "metaData": {"title": "String"},
                "%s": {"title": "%s"},
                "%s": {"title": "%s"}
            },
            "ReportColumn": {
                "metaData": {"name": "String", "report": "Report"},
                "%s": {"name":"%s","previous":%s,"next":%s,"report":%s},
                "%s": {"name":"%s","previous":%s,"next":%s,"report":%s},
                "%s": {"name":"%s","previous":%s,"next":%s,"report":%s},
                "%s": {"name":"%s","previous":%s,"next":%s,"report":%s}
            }
        }""" % (
            reportId1, reportTitle1,
            reportId2, reportTitle2,
            columnId1, columnName1, "null", columnId2, reportId1,
            columnId2, columnName2, columnId1, columnId4, reportId1,
            columnId3, columnName3, columnId4, "null", reportId1,
            columnId4, columnName4, columnId2, columnId3, reportId1
        )
        self.loader.loadDataAsJson(jsonString)
        r = self.registry.reports
        c = self.registry.reportColumns

        r1 = r[reportId1]
        r2 = r[reportId2]
        self.failUnlessEqual(r1.title, reportTitle1)
        self.failUnlessEqual(r2.title, reportTitle2)
        r1c = r1.listColumns()
        c1 = c[columnId1]
        c2 = c[columnId2]
        c3 = c[columnId3]
        c4 = c[columnId4]

        self.failUnlessEqual(c4.name, columnName4)
        self.failUnless(c4.previous, c4)
        self.failUnlessEqual(c4.previous.id, columnId2)
        self.failUnless(c4.next, c4)
        self.failUnlessEqual(c4.next.id, columnId3)

        self.failUnlessEqual(len(r1c), 4, r1c)
        self.failUnlessEqual(r1c[0], c1, r1c)
        self.failUnlessEqual(r1c[1], c2, r1c)
        self.failUnlessEqual(r1c[2], c4, r1c)
        self.failUnlessEqual(r1c[3], c3, r1c)

        self.failUnlessEqual(c1.name, columnName1)
        self.failIf(c1.previous, c1)
        self.failUnless(c1.next, c1)
        self.failUnlessEqual(c1.next.id, columnId2)

        self.failUnlessEqual(c2.name, columnName2)
        self.failUnless(c2.previous, c2)
        self.failUnlessEqual(c2.previous.id, columnId1)
        self.failUnless(c2.next, c2)
        self.failUnlessEqual(c2.next.id, columnId4)

        self.failUnlessEqual(c3.name, columnName3)
        self.failUnless(c3.previous, c3)
        self.failUnlessEqual(c3.previous.id, columnId4)
        self.failIf(c3.next, c3)


 
