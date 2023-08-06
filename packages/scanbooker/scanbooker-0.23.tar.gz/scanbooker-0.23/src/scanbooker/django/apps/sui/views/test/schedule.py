import unittest
from scanbooker.django.apps.sui.views.test.base import AdminSessionViewTestCase
from scanbooker.django.apps.sui.views.schedule import WeekScheduleView2
#from scanbooker.django.apps.sui.views.schedule import WeekScheduleView
#from scanbooker.django.apps.sui.views.schedule import WeekScheduleWidget
import mx.DateTime

def suite():
    suites = [
        unittest.makeSuite(TestWeekScheduleView2),
        #unittest.makeSuite(TestWeekScheduleView),
        #unittest.makeSuite(TestWeekScheduleWidget),
    ]
    return unittest.TestSuite(suites)


class TestWeekScheduleView2(AdminSessionViewTestCase):

    viewClass = WeekScheduleView2

    def test_getDefaultSettings(self):
        settings = self.view.getDefaultSettings()
        self.failUnless(settings, "Settings: '%s'" % settings)
        

#class TestWeekScheduleView(AdminSessionViewTestCase):
#
#    viewClass = WeekScheduleView
#
#    def test_findWeek(self):
#        self.view.timeInWeek = mx.DateTime.now()
#        week = self.view.findWeek()
#        if week:
#            week.delete()
#        self.failIf(self.view.findWeek())
#        self.failUnless(self.view.createWeek())
#        self.failUnless(self.view.findWeek())
#        week = self.view.findWeek()
#        week.delete()
#        self.failIf(self.view.findWeek())
#        
#    def test_getPastHorizon(self):
#        self.view.timeInWeek = mx.DateTime.now()
#        self.view.initialiseWeekTimes()
#        horizon = self.view.getPastHorizon()
#        self.failUnless(horizon < self.view.weekStarts, "%s %s" % (
#            horizon, self.view.weekStarts
#        ))
#    
#    def test_getFutureHorizon(self):
#        self.view.timeInWeek = mx.DateTime.now()
#        self.view.initialiseWeekTimes()
#        horizon = self.view.getFutureHorizon()
#        self.failUnless(horizon > self.view.weekStarts)
#    
#    def test_isWeekVisible(self):
#        self.view.timeInWeek = mx.DateTime.now()
#        self.failUnless(self.view.isWeekVisible())
#        self.view.embargoWeek()
#        self.failIf(self.view.isWeekVisible())
#        self.view.publishWeek()
#        self.failUnless(self.view.isWeekVisible())
#        self.view.embargoWeek()
#        self.failIf(self.view.isWeekVisible())
#
#
#class TestWeekScheduleWidget(AdminSessionViewTestCase):
#
#    viewClass = WeekScheduleWidget
#
#    def test_getResponse(self):
#        super(TestWeekScheduleWidget, self).test_getResponse()
#        self.failIf(self.view.scheduledSessions == None)
#        
#        # In this week...
##        self.weekStarts = mx.DateTime.Date(2005,6,13,0,0,0)
##        # ...schedule should have some fixture sessions.
##        self.view.timeInWeek = self.weekStarts
##        self.view.createScheduleGrid()
##        self.failIf(self.view.scheduledSessions == None)
##        self.failUnless(len(self.view.scheduledSessions))
##
##        # In this very old week...
##        self.weekStarts = mx.DateTime.Date(2002,6,10,0,0,0)
##        # ...schedule should have no sessions.
##        self.view.timeInWeek = self.weekStarts
##        self.view.createScheduleGrid()
##        self.failIf(
##            len(self.view.scheduledSessions),
##            str(self.view.scheduledSessions)
##        )
#
##    def test_createCurrentSchedule(self):
##        self.failUnless(self.view.schedule == None)
##        self.view.createSchedule()
##        self.failIf(self.view.schedule == None)
##
##    def test_createTimeBlockCells(self):
##        self.failUnless(self.view.timeBlocks == None)
##        self.view.createTimeBlocksCells()
##        self.failIf(self.view.timeBlocks == None)
##        self.failUnless(len(self.view.timeBlocks))
##        
##    def test_createDayList(self):
##        self.failUnless(self.view.dayList == None)
##        self.view.createSchedule()
##        self.view.createDayList()
##        self.failIf(self.view.dayList == None)
##        self.failUnless(len(self.view.dayList))
##        self.failUnlessEqual(self.view.dayList[2][0:3], 'Wed')
##
##    def test_createGrid(self):
##        self.failUnless(self.view.grid == None)
##        self.view.createSchedule()
##        self.view.createGrid()
##        self.failIf(self.view.grid == None)
##        
##    def test_getResponse(self):
##        self.view.getResponse()
#    
#
