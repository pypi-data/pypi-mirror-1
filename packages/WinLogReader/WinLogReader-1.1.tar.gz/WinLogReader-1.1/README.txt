This module contains a class that lets you easily view, sort and filter
Windows logentries. It is written by Stefan Christensen while being
employed by The Computer Center at the University of Tromsø.
University of Tromsø can be found here: http://uit.no


-----------
USAGE:

import WinLogReader
test = WinLogReader.WinLogReader('AppEvent.Evt')

Now you have an object with the file loaded in a list. Will give further
details about the methods later in this file.


-----------
Methods:(those marked with * are generally list-methods)

getsortorder()                          : Gives you the current sort-order.

setsortorder(tuple)                     : Takes a tuple with the wanted
                                          sort-order. Need not be the
                                          entire tuple

sort()*                                 : Obviously sorts the list.

addfilter(fieldnumber,test)             : Takes the numbered field, and
                                          evaluates the test.

clearfilter()                           : Clears the filters set.

addfilterfunction(field,function)       : Takes the numbered field and a
                                          function the evaluates the field
                                          to either True or False.

runtransformfunction(field,function)    : Takes the numbered field and a
                                          function that will transform the
                                          data in the field.

reverse()*                              : Reverses the list IN PLACE.

count(value)*                           : Counts the occurence of Value in the list.

-----------
Properties:
These will change in a future versions when I get a better API.
l               : The unfiltered list. The only method that changes this is
                  sort()
f               : The filtered list. All methods operates on this.

-----------
TODO:
    - Add the possibility to set filters based on the field-name.
    - Make a Python 3.* compatible version.


-----------
Examples:

test.addfilter(4,'== 1221')
    - Will add a filter to only show the EventID's corresponding to
      Exchange online defrag results.

test.setsortorder(('EventID','Description'))
    - Will change the primary sort order to EventID, and then on
      Description, further it keeps the old sortorder.


