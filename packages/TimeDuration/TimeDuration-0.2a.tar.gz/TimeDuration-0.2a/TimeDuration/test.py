#!/usr/bin/python
import unittest
import os
import sys
import glob
from distutils import sysconfig

PYTHONLIB = os.path.join(sysconfig.get_python_lib(standard_lib=1, prefix=''), os.getcwd())

from TimeDuration import TimeDuration

import pdb

class TestTimeDuration (unittest.TestCase) :

    def testInstance (self) :
        a = TimeDuration()
        self.assertEqual(isinstance(a, TimeDuration), True)

    def testNormalized_1 (self) :
        b = TimeDuration()
        self.assertEqual(b.normalized('12-13-14'), "12:13:14.00")

    def testNormalized_2 (self) :
        c = TimeDuration("1d 15:12")
        self.assertEqual(c.normalized(), "1 D 15:12:0.00") 
        time_string = [
            "5 dd, 3 hh, 42 minutes and 7 seconds",             # 0
            "6 days, 21 hours, 40 minutes and 17.8 seconds",    # 1
            "7 days, 40 minutes and 17.8 seconds",              # 2
            "8 days, 21 hours and 17.8 seconds",                # 3
            "9 days, 21 hours and 40 minutes",                  # 4
            "4 dd, 3 hh, 42 mm",                                # 5
            "3 hh and 72 minutes",                              # 6
            "4 d 12:23:14.5",                                   # 7
            "13 days, 17:38",                                   # 8
            "0m18.370s",                                        # 9
            "7 days, 12 hours and 35 minutes"                   #10
        ]
        for i in range(len(time_string)) :
            t = TimeDuration(time_string[i], True)
            if i == 0 :
                self.assertEqual(t.normalized(), "5 D 03:42:7.00")
            elif i == 1 :
                self.assertEqual(t.normalized(), "6 D 21:40:17.80")
            elif i == 2 :
                self.assertEqual(t.normalized(), "7 D 00:40:17.80")
            elif i == 3 :
                self.assertEqual(t.normalized(), "8 D 21:00:17.80")
            elif i == 4 :
                self.assertEqual(t.normalized(), "9 D 21:40:0.00")
            elif i == 5 :
                self.assertEqual(t.normalized(), "4 D 03:42:0.00")
            elif i == 6 :
                self.assertEqual(t.normalized(), "04:12:0.00")
            elif i == 7 :
                self.assertEqual(t.normalized(), "4 D 12:23:14.50")
            elif i == 8 :
                self.assertEqual(t.normalized(), "13 D 17:38:0.00")
            elif i == 9 :
                self.assertEqual(t.normalized(), "00:00:18.37")
            elif i == 10 :
                self.assertEqual(t.normalized(), "7 D 12:35:0.00")

    def testNormalized_3 (self) :
        time_array = [ "12 hours, 35 minutes and 12 seconds",
                "4 hh, 17 min, 17.3 sec",
                "1 day, 14 minutes",
                "120 hours, 85 seconds",
                "3:34:45.1"
             ]
        td_array = []
        for i in range(len(time_array)) :
            t = TimeDuration(time_array[i], True)
            if i == 0 :
                self.assertEqual(t.normalized(), "12:35:12.00")
                td_array.append(t)

            if i == 1 :
                self.assertEqual(t.normalized(), "04:17:17.30")
                td_array.append(t)

            if i == 2 :
                self.assertEqual(t.normalized(), "1 D 00:14:0.00")
                td_array.append(t)
        
            if i == 3 :
                self.assertEqual(t.normalized(), "120:01:25.00")
                td_array.append(t)

            if i == 4 :
                self.assertEqual(t.normalized(), "03:34:45.10")
                td_array.append(t)

            td_array.sort()
            for i in range(len(td_array)) :
                if i == 4 :
                    #pdb.set_trace()
                    self.assertEqual( str(td_array[i]), str(TimeDuration("120:01:25.0").normalized()) ) 


    def testFromSeconds (self) :
        sec_string = "1987"
        t = TimeDuration(sec_string)
        self.assertEqual(t.from_seconds(), "00:33:7.00")


    def testToMinutes (self) :
        string1 = "1 D 23:30:12.2"
        s1 = TimeDuration(string1, True)
        self.assertEqual(s1.to_minutes() - 2850.20 < 0.01, True)

    def testToMinutes_2 (self) :
        a_string = "7 days, 12 hours and 35 minutes"
        td_0 = TimeDuration(a_string, True)
        min = td_0.to_minutes()
        self.assertEqual(min - 10835 < 0.01, True)


    def testToHours (self) :
        ts = "12hours, 13 min, 12.2 sec"
        ts1 = TimeDuration(ts, True)
        self.assertEqual(ts1.to_hours() - 12.2214 < 0.01, True) 

    def testLessThan (self) :
        string2 = "34:21:12.2"
        string3 = "21:15:22.5"
        s2 = TimeDuration(string2)
        s3 = TimeDuration(string3)
        self.assertEqual(s2 < s3, False)
    
    def testLessThanEqual (self) :
        string4 = "1 D 34:21:12.2"
        string5 = "3 weeks, 4 days 21:15:22"
        s4 = TimeDuration(string4, True)
        s5 = TimeDuration(string5, True)
        self.assertEqual(s4 <= s5, True)

    def testEqual (self) :
        string6 = "5 days, 14:21:12.2"
        string7 = "4 days, 38:21:12.2"
        s6 = TimeDuration(string6, True)
        s7 = TimeDuration(string7, True)
        self.assertEqual(s6 == s7, True)
   
    def testEqual (self) :
        string6 = "5 days, 14:21:12.2"
        string7 = "4 days, 38:21:12.2"
        s6 = TimeDuration(string6, True)
        s7 = TimeDuration(string7, True)
        self.assertEqual(s6 == s7, True)

    def testNotEqual (self) :
        string9 = "3 weeks, 7 days, 12 hours"
        string10 = "3 weeks, 7 days, 12 hours and 45 minutes"
        s9 = TimeDuration(string9, True)
        s10 = TimeDuration(string10, True)
        self.assertEqual( s9 != s10, True)


    def testGreaterThan (self) :
        string11 = "1d 22:34:00"
        string12 = '1d 22:34:00.01'
        s11 = TimeDuration(string11, True)
        s12 = TimeDuration(string12, True)
        self.assertEqual(s12 > s11, True)

    def testAddition (self) :
        s13 = TimeDuration("5:10:10.0", True)
        s14 = TimeDuration("4:01:01.0", True)
        temp = TimeDuration("0:00:00", True)
        temp = s13 + s14
        self.assertEqual(str(temp), "09:11:11.00")

    def testCmp (self) :
        time_durations = []
        t1 = TimeDuration("11:12:13.0")
        t2 = TimeDuration("13:14:15.0")
        t3 = TimeDuration("12:13:14.0")
        time_durations.append(t1)
        time_durations.append(t2)
        time_durations.append(t3)
        time_durations.sort()
        for i in range(len(time_durations)) :
            if i == 0 :
                self.assertEqual(time_durations[i], t1)
            if i == 1 :
                self.assertEqual(time_durations[i], t3)
            if i == 2 :
                self.assertEqual(time_durations[i], t2)


        
    def testFloatSeconds (self) :
        td_1 = TimeDuration("1:14.5")
        self.assertEqual( ( td_1.to_seconds() - 74.5 )  < 0.001, True)

    
if __name__ == "__main__" :

	unittest.main()

# vim:ts=4:sw=4
