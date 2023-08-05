# Node Display Manager (NDM):
# A simple X display manager for cluster nodes that also serve as
# access-restricted workstations. An NDM client runs on each node and
# communicates via Twisted's Perspective Broker to a master NDM server, which
# regulates when and how much each user can use his account on any of the
# workstations. The NDM server also dispatches cluster operations to the nodes
# via the NDM clients, unbeknownst to the workstation users.
#
# Copyright (C) 2006 by Edwin A. Suominen, http://www.eepatents.com
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the file COPYING for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

"""
Unit tests for master.database
"""

import time
from datetime import date

from twisted.internet import defer
from twisted.python import failure
from twisted.trial.unittest import TestCase

# import mock
import database


class MockDBMethods(object):
    def __init__(self, transactor):
        self.calls = []

        # Set default values for the times. Note that these are
        # *values*, not *methods, and they are non-private (this
        # is so we can avoid having a multitude of setter method).
        self._openingTimeLeft    = None
        self._accountTimeLeft    = None

        # Reassign several of the transactor's methods.
        transactor.openingTimeLeft = self.mockopeningTimeLeft
        transactor.accountTimeLeft = self.mockaccountTimeLeft

    def mockopeningTimeLeft(self):
        self.calls.append(('openingTimeLeft'))
        return self._openingTimeLeft

    def mockaccountTimeLeft(self, userID):
        self.calls.append(('accountTimeLeft', userID))
        return self._accountTimeLeft


class MockTimeMethods(object):
    def __init__(self, transactor):
        self.transactor             = transactor
        self.calls              = []
        self.today              = None
        self.localtime          = None
        self.sessionStartTime   = None
        
        transactor._today           = self._mock_today
        transactor._localtime       = self._mock_localtime

        transactor.retrieveSessionStartTime = self._mock_retreiveSessionStartTime

    def _mock_today(self):
        self.calls.append(('today'))
        if self.today is not None:
            return self.today
        else:
            return date.today()
            
    def _mock_localtime(self):
        self.calls.append(('localtime'))
        if self.localtime is not None:
            return self.localtime
        else:
            return time.localtime()
    
    def _mock_retreiveSessionStartTime(self,userID):
        # This is a bit cacky as it requires knowledge of the internal
        # implementation of the transactor's retrieveSessionStartTime() method.
        # But it makes testing sessionEnd() much simpler.
        self.calls.append(('retrieveSessionStartTime'))
        if self.sessionStartTime is not None:
            return self.sessionStartTime
        else:
            return self.transactor._activeSessionStartTimes.pop(userID,None)

    
class Mixin:
    def _setupUsers(self):
        users = self.transactor.users
        users.delete().execute()
        users.insert().execute(
            id='alpha',
            password='male',
            enabled=True,
            restricted=True,
            daily_hours=1.2,
            weekly_hours=3.4
            )
        users.insert().execute(
            id='bravo',
            password='awards',
            enabled=True,
            restricted=False
            )
        users.insert().execute(
            id='charlie',
            password='brown',
            enabled=True,
            restricted=True,
            daily_hours=4.5,
            weekly_hours=5.6
           )
        users.insert().execute(
            id='delta',
            password='rocket',
            enabled=True,
            restricted=True,
            daily_hours=5.0,
            weekly_hours=5.0
            )
        users.insert().execute(
            id='echo',
            password='canyon',
            enabled=False,
            restricted=True,
            daily_hours=5.0,
            weekly_hours=5.0
            )
        users.insert().execute(
            id='foxtrot',
            password='submarine',
            enabled=False,
            restricted=True,
            daily_hours=24.0,
            weekly_hours=168.0
            )
        users.insert().execute(
            id='golf',
            password='illinois',
            enabled=False,
            restricted=False,
            daily_hours=24.0,
            weekly_hours=168.0
            )

    def _setupOpenings(self):
        openings = self.transactor.openings
        openings.delete().execute()
        # Add an opening for Sundays from 9am to 6pm.
        openings.insert().execute(
            weekday=6,
            start_hour=9.0,
            end_hour=18.0
            )

    def _setupTimesheet(self):
        timesheet = self.transactor.timesheet
        timesheet.delete().execute()
        # Add some example usage for the user 'alpha'
        timesheet.insert().execute(
            user_id='alpha',
            date=date(2006,07,23),
            start_hour=9.0,
            end_hour=10.0
            )
        timesheet.insert().execute(
            user_id='alpha',
            date=date(2006,07,23),
            start_hour=12.0,
            end_hour=13.0
            )
        # Add some example usage for the user 'charlie'
        timesheet.insert().execute(
            user_id='charlie',
            date=date(2006,07,23),
            start_hour=9.0,
            end_hour=12.0
            )
        # Add some example usage for the user 'delta'
        timesheet.insert().execute(
            user_id='delta',
            date=date(2006,07,22),
            start_hour=9.0,
            end_hour=14.0
            )
        # Add some example usage for the user 'echo'
        timesheet.insert().execute(
            user_id='echo',
            date=date(2006,07,22),
            start_hour=9.0,
            end_hour=12.0
            )


class TestDataSessionStart(TestCase, Mixin):
    def setUp(self):
        url = "sqlite://transactor-sessionstart.db"
        self.transactor = database.UserDataTransactor(url)
        self.mm = MockDBMethods(self.transactor)
        d = self.transactor.startup()
        d.addCallback(lambda _: self.transactor.deferToQueue(self._setupUsers))
        return d
    
    def testNeitherOpeningTimeNorAccountTimeLeft(self):
        """
        'alpha' is a restricted user; here we pretend that 'alpha' has time
        left in the current opening but no time left in the account.
        """
        self.mm.openingTimeLeft=0.0
        self.mm.accountTimeLeft=0.0
        d = self.transactor.sessionStart('alpha')
        d.addCallback(self.failUnlessAlmostEqual, 0.0)
        return d

    def testOpeningTimeButNoAccountTimeLeft(self):
        """
        'alpha' is a restricted user; here we pretend that 'alpha' has time
        left in the current opening but no time left in the account.
        """
        self.mm.openingTimeLeft=2.0
        self.mm.accountTimeLeft=0.0
        d = self.transactor.sessionStart('alpha')
        d.addCallback(self.failUnlessAlmostEqual, 0.0)
        return d

    def testAccountTimeButNoOpeningTimeLeft(self):
        """
        'alpha' is a restricted user; here we pretend that 'alpha' has time
        left in the current opening AND has time left in the account.
        """
        self.mm.openingTimeLeft=0.0
        self.mm.accountTimeLeft=2.0
        d = self.transactor.sessionStart('alpha')
        d.addCallback(self.failUnlessAlmostEqual, 0.0)
        return d

    def testBothAccountTimeAndOpeningTimeLeft(self):
        """
        'alpha' is a restricted user; here we pretend that 'alpha' has time
        left in the current opening AND has time left in the account. The
        return value should be the lesser of the two values.
        """
        self.mm.openingTimeLeft=2.0
        self.mm.accountTimeLeft=4.0
        d = self.transactor.sessionStart('alpha')
        d.addCallback(self.failUnlessAlmostEqual, 2.0)
        return d


class TestDataTransactorTimeLeft(TestCase, Mixin):
    def setUp(self):
        url = "sqlite://transactor-timeleft.db"
        self.transactor = database.UserDataTransactor(url)
        self.mm = MockTimeMethods(self.transactor)
        d = self.transactor.startup()
        d.addCallback(lambda _: self.transactor.deferToQueue(self._setupUsers))
        return d

    def testOpeningTimeLeftOpen(self):
        """
        July 23rd 2006 is a Sunday. Let's pretend it's 10:00am: we should
        therefore have 8 hours until the end of the opening at 18:00.
        """
        start_time        = (2006, 07, 23, 10, 00, 00, 6, 0, 0)
        today             = date(*start_time[0:3])
        self.mm.localtime = start_time
        self.mm.today     = today
        d = self.transactor.deferToQueue(self._setupOpenings)
        d.addCallback(lambda _: self.transactor.openingTimeLeft())
        d.addCallback(self.failUnlessAlmostEqual, 8.0)
        return d

    def testOpeningTimeLeftClosed(self):
        """
        July 23rd 2006 is a Sunday. Let's pretend it's 7:00pm: we are therefore
        *after* the end of the opening at 18:00, so we expect to have no
        opening time left.
        """
        start_time        = (2006, 07, 23, 19, 00, 00, 6, 0, 0)
        today             = date(*start_time[0:3])
        self.mm.localtime = start_time
        self.mm.today     = today
        d = self.transactor.deferToQueue(self._setupOpenings)
        d.addCallback(lambda _: self.transactor.openingTimeLeft())
        d.addCallback(self.failUnlessAlmostEqual, 0.0)
        return d

    def testAccountTimeLeftNoneToday(self):
        """
        Test account time for user 'alpha', who is permissioned for 1.2 hours
        per day and 3.4 hours per week. Alpha has somehow managed to work from
        9-10am and 12-1pm, so should have no time left for today.
        """
        start_time        = (2006, 07, 23, 19, 00, 00, 6, 0, 0)
        today             = date(*start_time[0:3])
        self.mm.localtime = start_time
        self.mm.today     = today
        d1 = self.transactor.deferToQueue(self._setupOpenings)
        d2 = self.transactor.deferToQueue(self._setupTimesheet)
        d = defer.DeferredList([d1,d2])
        d.addCallback(lambda _: self.transactor.accountTimeLeft('alpha'))
        d.addCallback(self.failUnlessAlmostEqual, 0.0)
        return d

    def testAccountTimeLeftSomeToday(self):
        """
        Test account time for user 'charlie', who is permissioned for 4.5 hours
        per day and 5.6 hours per week. Charlie has worked from 9am to 12
        midday (see the rows in _setupTimesheet()), so should have 1.5 hours left
        for today.
        """
        start_time        = (2006, 07, 23, 19, 00, 00, 6, 0, 0)
        today             = date(*start_time[0:3])
        self.mm.localtime = start_time
        self.mm.today     = today
        d1 = self.transactor.deferToQueue(self._setupOpenings)
        d2 = self.transactor.deferToQueue(self._setupTimesheet)
        d = defer.DeferredList([d1,d2])
        d.addCallback(lambda _: self.transactor.accountTimeLeft('charlie'))
        d.addCallback(self.failUnlessAlmostEqual, 1.5)
        return d
    
    def testAccountTimeLeftNoneThisWeek(self):
        """
        Test account time for user 'delta', who is permissioned for 5.0 hours
        per day and 5.0 hours per week. Delta used up all his allowance on
        20060722, so should have no time left for this week despite not having
        used up any in the current session.
        """
        start_time        = (2006, 07, 23, 19, 00, 00, 6, 0, 0)
        today             = date(*start_time[0:3])
        self.mm.localtime = start_time
        self.mm.today     = today
        d1 = self.transactor.deferToQueue(self._setupOpenings)
        d2 = self.transactor.deferToQueue(self._setupTimesheet)
        d = defer.DeferredList([d1,d2])
        d.addCallback(lambda _: self.transactor.accountTimeLeft('delta'))
        d.addCallback(self.failUnlessAlmostEqual, 0.0)
        return d

    def testAccountTimeLeftSomeThisWeek(self):
        """
        Test account time for user 'echo', who is permissioned for 5.0 hours
        per day and 5.0 hours per week. Echo used up 3.0 hours of his
        allowance on 20060722, so should have 2.0 hours left.
        """
        start_time        = (2006, 07, 23, 19, 00, 00, 6, 0, 0)
        today             = date(*start_time[0:3])
        self.mm.localtime = start_time
        self.mm.today     = today
        d1 = self.transactor.deferToQueue(self._setupOpenings)
        d2 = self.transactor.deferToQueue(self._setupTimesheet)
        d = defer.DeferredList([d1,d2])
        d.addCallback(lambda _: self.transactor.accountTimeLeft('echo'))
        d.addCallback(self.failUnlessAlmostEqual, 2.0)
        return d


class TestDataTransactorOther(TestCase, Mixin):
    def setUp(self):
        url = "sqlite://transactor-other.db"
        self.transactor = database.UserDataTransactor(url)
        self.mm = MockTimeMethods(self.transactor)
        d = self.transactor.startup()
        d.addCallback(lambda _: self.transactor.deferToQueue(self._setupUsers))
        d.addCallback(lambda _: self.transactor.deferToQueue(self._setupOpenings))
        return d

    def testSessionAuthorizedBecausePasswordOK(self):
        """
        Test that different users have authorized sessions when their unique
        passwords are supplied correctly.
        """
        d1 = self.transactor.sessionAuthorized('alpha',   'male')
        d2 = self.transactor.sessionAuthorized('charlie', 'brown')
        dl = defer.DeferredList([d1,d2])
        dl.addCallback(self.failUnlessEqual, [(True,True),(True,True)])
        return dl

    def testSessionUnauthorizedBecausePasswordBogus(self):
        """
        Test that different users do not get authorized sessions when their
        unique passwords are supplied incorrectly and, in some cases, mixed up
        with each other.
        """
        # Both these users and passwords exist, but passwords belong to other
        # users:
        d1 = self.transactor.sessionAuthorized('alpha',   'brown')
        d2 = self.transactor.sessionAuthorized('charlie', 'male')
        # These users exist, but the passwords are (1) wrong and (2) do not
        # belong to other users:
        d3 = self.transactor.sessionAuthorized('bravo', 'sasquatch')
        d4 = self.transactor.sessionAuthorized('delta', 'possum')
        # These users do not exist, but the passwords supplied are the
        # passwords of existing users:
        d5 = self.transactor.sessionAuthorized('drevil', 'brown')
        d6 = self.transactor.sessionAuthorized('darthvader', 'rocket')
        # Neither these users nor passwords exist:
        d7 = self.transactor.sessionAuthorized('drevil', 'sasquatch')
        d8 = self.transactor.sessionAuthorized('darthvader', 'possum')

        dl = defer.DeferredList([d1,d2,d3,d4,d5,d6,d7,d8])
        dl.addCallback(self.failUnlessEqual,
                       [(True,False),(True,False),(True,False),(True,False),
                        (True,False),(True,False),(True,False),(True,False)])
        return dl

    def testSessionUnauthorizedBecauseUserDisabled(self):
        """
        Test that disabled users, even unrestricted ones, do not get authorized
        sessions, despite the correct password being supplied. This test
        also shows that the enabling is not affected by their hours allowance.
        """
        # User 'echo' is a restricted user with a 'reasonable' daily and weekly
        # allowance, but is not enabled:
        d1 = self.transactor.sessionAuthorized('echo', 'canyon')
        # User 'foxtrot' is a restricted user with an apparently unlimited
        # daily and weekly allowance, but is not enabled:
        d2 = self.transactor.sessionAuthorized('foxtrot', 'submarine')
        # User 'golf' is *not* a restricted user, but is not enabled:
        d3 = self.transactor.sessionAuthorized('golf', 'illinois')
        dl = defer.DeferredList([d1,d2,d3])
        dl.addCallback(self.failUnlessEqual,
                       [(True,False),(True,False),(True,False)])
        return dl

    def testSessionEndLogsTime(self):
        """
        Test that ending a session accurately records the additional time
        used in a session. We do this by spoofing a session start time
        and the current time and calling sessionEnd(). We then check that
        the value returned by accountTimeLeft() has decremented by the
        same amount.
        """
        # Note that the original description was that it should test that
        # ending a session correctly logged the *time*; strictly speaking this
        # isn't possible as the database module doesn't export direct access
        # to the actual rows in 'timesheet'.
        # This is probably a good enough proxy for testing purposes.

        start_time = 10.0
        end_time   = 11.0

        def _compareTime(time_left2, time_left1,ud):
            ud.callback((time_left1-time_left2)-(end_time-start_time))
        
        def _endSession(time_left1,ud):
            self.mm.sessionStartTime = start_time
            d2 = self.transactor.sessionEnd('echo')
            d2.addCallback(lambda _: self.transactor.accountTimeLeft('echo'))
            d2.addCallback(_compareTime,time_left1,ud)

        def _doTest(dummy):
            now = (2006, 07, 23, end_time, 00, 00, 6, 0, 0)
            self.mm.localtime = now
            self.mm.today     = date(*now[0:3])
            ud = defer.Deferred()
            d1 = self.transactor.accountTimeLeft('echo')
            d1.addCallback(_endSession,ud)
            return ud

        d = self.transactor.deferToQueue(self._setupTimesheet)
        d.addCallback(_doTest)
        d.addCallback(self.failUnlessAlmostEqual, 0.0)
        return d

    def testNoConcurrentSessions(self):
        """
        Test that a user cannot get a new session when he already has one
        active. We test for user 'echo' who has 2 hours left of
        his weekly time. We first open a session and after a spoofed
        period of 1 hour attempt to to open another one.
        We expect this to be disallowed (by way of sessionStart()
        returning 0.0 hours).
        """
        start_time = 10.0

        def _checkOther(time_left2, ud):
            ud.callback(time_left2)
        
        def _openAnother(time_left1, ud):
            now = (2006, 07, 23, start_time + 1.0, 00, 00, 6, 0, 0)
            self.mm.localtime = now
            self.mm.today     = date(*now[0:3])
            d2 = self.transactor.sessionStart('echo')
            d2.addCallback(_checkOther, ud)
        
        def _doTest(dummy):
            now = (2006, 07, 23, start_time, 00, 00, 6, 0, 0)
            self.mm.localtime = now
            self.mm.today     = date(*now[0:3])
            ud = defer.Deferred()
            d1 = self.transactor.sessionStart('echo')
            d1.addCallback(_openAnother,ud)
            return ud

        d = self.transactor.deferToQueue(self._setupTimesheet)
        d.addCallback(_doTest)
        d.addCallback(self.failUnlessAlmostEqual, 0.0)
        return d
        
    def testConsecutiveSessions(self):
        """
        Test that a user can get a new session after closing a previously
        active session. We test for user 'echo' who has 2 hours left of
        his weekly time. We first spoof a 1-hour session, close it,
        and try to open another session, expecting to see 1 hour left.
        """
        start_time = 10.0
        end_time   = 11.0
        userID     = 'echo'
        
        def _checkOther(time_left2, ud):
            ud.callback(time_left2)
        
        def _openAnother(dummy, ud):
            d3 = self.transactor.sessionStart(userID)
            d3.addCallback(_checkOther, ud)
        
        def _closeSession(time_left1, ud):
            now = (2006, 07, 23, end_time, 00, 00, 6, 0, 0)
            self.mm.localtime = now
            self.mm.today     = date(*now[0:3])
            d2 = self.transactor.sessionEnd(userID)
            d2.addCallback(_openAnother, ud)
        
        def _doTest(dummy):
            now = (2006, 07, 23, start_time, 00, 00, 6, 0, 0)
            self.mm.localtime = now
            self.mm.today     = date(*now[0:3])
            ud = defer.Deferred()
            d1 = self.transactor.sessionStart(userID)
            d1.addCallback(_closeSession,ud)
            return ud

        d = self.transactor.deferToQueue(self._setupTimesheet)
        d.addCallback(_doTest)
        d.addCallback(self.failUnlessAlmostEqual, 1.0)
        return d

    def testEnabled(self):
        """
        Test the API for enabling a user account.
        
        We test user 'golf', who is initially not enabled. We test that this
        is indeed the case, enable the user, test this, and finally return
        to the disabled state.
        """
        userID = 'golf'
        passwd = 'illinois'

        results = []

        def _checkSession3(auth, ud):
            results.append(auth)
            ud.callback(results)

        def _checkSession2(auth, ud):
            results.append(auth)
            # Re-disable the user.
            d3 = self.transactor.enabled(userID,False)
            d3.addCallback(
                lambda _: self.transactor.sessionAuthorized(userID, passwd))
            d3.addCallback(_checkSession3,ud)
            
        def _checkSession1(auth, ud):
            results.append(auth)
            # Now enable the user.
            d2 = self.transactor.enabled(userID,True)
            d2.addCallback(
                lambda _: self.transactor.sessionAuthorized(userID, passwd))
            d2.addCallback(_checkSession2,ud)
            
        def _doTest(dummy):
            d1 = self.transactor.sessionAuthorized(userID,passwd)
            ud = defer.Deferred()
            d1.addCallback(_checkSession1,ud)
            return ud
        
        d = self.transactor.deferToQueue(self._setupUsers)
        d.addCallback(_doTest)
        d.addCallback(self.failUnlessEqual, [False, True, False])
        return d
    
    def testPasswordNewUser(self):
        """
        Test the API for creating a new user with password.
        """
        userID   = 'hotel'
        password = 'california'

        results = []

        def _userDeleted(result,ud):
            results.append(result)
            ud.callback(results)

        def _userCreated(result,ud):
            results.append(result)
            d3 = self.transactor.deleteUser(userID)
            d3.addCallback(lambda _: self.transactor.userExists(userID))
            d3.addCallback(_userDeleted,ud)

        def _userExists(result,ud):
            results.append(result)
            d2 = self.transactor.password(userID,password)
            d2.addCallback(lambda _: self.transactor.userExists(userID))
            d2.addCallback(_userCreated,ud)

        def _doTest(dummy=None):
            d1 = self.transactor.userExists(userID)
            ud = defer.Deferred()
            d1.addCallback(_userExists,ud)
            return ud

        d = _doTest()
        d.addCallback(self.failUnlessEqual, [False,True,False])
        return d

    def testPasswordUpdateUser(self):
        """
        Test the API for updating an existing user's password. We test
        user 'alpha', first ensuring that the user is authorized with that
        password. We then change the password, and check that (1) the old
        password no longer works, and that (2) the new password does work.
        We finally change the password back to its original value and
        ensure that the original login still works.
        """
        userID   = 'alpha'
        password = 'male'
        newpass  = 'bet'

        results = []

        def _origPassOKAgain(result, ud):
            results.append(result)
            ud.callback(results)
        
        def _newPassOK(result,ud):
            results.append(result)
            # Change the password back to the old value and verify that using
            # the old password works again.
            d4 = self.transactor.password(userID, password)
            d4.addCallback(
                lambda _:self.transactor.sessionAuthorized(userID, password))
            d4.addCallback(_origPassOKAgain, ud)
        
        def _oldPassNotOK(result, ud):
            results.append(result)
            # Verify that the new password works.
            d3 = self.transactor.sessionAuthorized(userID, newpass)
            d3.addCallback(_newPassOK,ud)
        
        def _origPassOK(result, ud):
            results.append(result)
            # Change the password and verify that the old one no longer works.
            d2 = self.transactor.password(userID,newpass)
            d2.addCallback(
                lambda _: self.transactor.sessionAuthorized(userID, password))
            d2.addCallback(_oldPassNotOK,ud)
            
        def _doTest(dummy=None):
            # Check that the original password works.
            d1 = self.transactor.sessionAuthorized(userID, password)
            ud = defer.Deferred()
            d1.addCallback(_origPassOK,ud)
            return ud
        
        d = _doTest()
        d.addCallback(self.failUnlessEqual, [True, False, True, True])
        return d
