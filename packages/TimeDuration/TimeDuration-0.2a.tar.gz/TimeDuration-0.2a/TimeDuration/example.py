from TimeDuration import TimeDuration as TD

import pdb

time1 = TD("5:10:10.0")
time2 = TD("4:01:01.0")
temp = time1 + time2
print "sum of 5:10:10.0 and 4:01:01.0 is " +  str(temp)
time3 = TD("7 days, 12 hours and 35 minutes")
print "7 days, 12 hours and 35 minutes is ",
print str(time3.to_seconds()) + " seconds",
print " or " + str(time3.to_minutes()) + " minutes",
print " or " + str(time3.to_hours()) + " hours"
print "10,230 seconds is " + str(TD("10230").normalized())
time_array = [ "12 hours, 35 minutes and 12 seconds",
                "4 hh, 17 min, 17.3 sec",
                "1 day, 14 minutes"
                "120 hours, 85 seconds",
                "3:34:45.1"
             ]

td_array = []
for i in range(len(time_array)) :
    td_array.append( TD(time_array[i]) )


    
#pdb.set_trace()
print TD("1 day, 14 minutes").normalized()

