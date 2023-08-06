This is my foray into Python development.  Coming from C, C++ and Perl, Python is a refreshing
language with a ton of great tools that make it a joy.  

But you already know that.

I had a problem -- I needed a way to pull race times off a spreadsheet and I couldn't find any
off-the-shelf solutions, so I created my own and decided to distribute it.

If you find it useful, great!

Let me know if you have any suggestions for fixes, improvements, use-cases
etc.


-- A.L.



The TimeDuration module provides a Pure Python interface to the creation, manipulation and comparison
of time duration string.  E.g. if 3:21:45.3 and 3:22:30.1 represent stopwatch times, I don't want
to represent or store them as datetime objects but I do want to be able to compare them and
do simple calculations on such string such as find the average of a tuple of TimeDuration objects.
I'd also like to be able to say something like "3 weeks, 5 days 12 hours and 32 minutes" and be
able to convert that to minutes, seconds or hours and be able to convert strings that look like
durations of time to a normalized format.


After running setup.py, run test.py

There are examples of usage in the example.py file


Author Andrew Lee, fiacre.patrick@gmail.com



