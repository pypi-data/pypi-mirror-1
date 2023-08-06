"""This module that  will get data out of *.evt-files
This module is coypright 2009 Stefan Christensen and released under 
Description of the logentries kan be found here:
http://www.codeproject.com/KB/string/EventLogParser.aspx
Though there is a slight error in the EntryID-part,
 it's only a 16bit value.
"""
# store the sort priority in a list.
# To change sortpriority, get new tuple from user, and change the tuples in the list to new ordering.


from struct import unpack               # To convert the bytestream into numbers
from time import gmtime,strftime        # To convert epochtime to humanreadable datetime
from os.path import isfile              # To verify that the file exist


class WinLogReader:
    """Call this class with the name of the file.
    You'll then get a object back containg all logentries from given file."""

    def _get_entry_header(self,s):
        """Takes a string of bytes and returns the header as a dict."""
        d = dict()
        vals = unpack('I',s[-8:-4])
        if vals[0] < 56 or len(s) < 56: return d
        vals += unpack('<IIIHHHHHHIIIIII',s[0:48])
        for i in range(len(self._entry_header_keys)):
            d[self._entry_header_keys[i]] = vals[i]
        for i in ('TimeGenerated','TimeWritten'):
            d[i] = strftime('%Y_%m_%d_%H:%M:%S_UTC',gmtime(d[i]))
        return d

    def _verify_file_header(self,l):
        """Returns True if first element in the list is the LSB-value of 48."""
        return l[0] == '0\x00\x00\x00'

    def _verify_header(self,d,length):
        """Returns True if this seems to be a valid header."""
        return 'Recordlength' in d and d['Recordlength'] >= 56 and length + 4 == d['Recordlength']

    def _insert_entry(self,d):
        t = tuple()
        for i in self._current_tuple:
            t+=(d[i],)
        self._original_list.append(t)

    def _add_entry_values(self,d,s):
        """Takes the dictionary, and the string that corresponds to the header
        loaded into the dictionary."""
        assert d['Recordlength'] == len(s) + 4
        temp = s[56:d['UserSidOffset']].split('\x00\x00')
        for i in range(2):
            d[self._entry_variable_keys[i]] = temp[i].replace('\x00','')
        d['UserSid'] = s[d['UserSidOffset']:d['UserSidLength'] + d['UserSidOffset']]
        temp = s[d['StringOffset']:d['DataOffset']].split('\x00\x00')
        t = tuple()
        for item in temp:
            temp2 = item.replace('\x00','')
            if temp2.isdigit():
                temp2 = int(temp2)
            t += (temp2,)
        d['Description'] = t
        t = tuple()
        temp = s[d['DataOffset']:d['DataOffset'] + d['DataLength']].split('\x00\x00')
        for item in temp:
            temp2 = item.replace('\x00','')
            if temp2.isdigit():
                temp2 = int(temp2)
            t += (temp2,)
        d['Data'] = t

    def __init__(self,filename,full_dump=False):
        self._original_list = list()
        self._filtered_list = list()
        self._current_list = self._original_list
        self._entry_header_keys = ('Recordlength', 'RecordNumber',
            'TimeGenerated', 'TimeWritten', 'EventID','Unknown1', 'EventType',
            'NumStrings', 'EventCategory', 'ReservedFlags',
            'ClosingRecordNumber', 'StringOffset', 'UserSidLength',
            'UserSidOffset', 'DataLength', 'DataOffset')
        self._file_header_keys = ('Recordlength', 'MagicNumber', 'Unknown1',
            'Unknown2', 'Unknown3', 'NextEntryToRecord', 'NextEntry',
            'Unknown4', 'Unknown5', 'Unknown6', 'Unknown7', 'Unknown8')
        self._entry_variable_keys = ('SourceName', 'Computername', 'UserSid',
            'Description', 'Data')
        if full_dump:
            self._current_tuple = self._entry_header_keys + self._entry_variable_keys
        else:
            self._current_tuple = ('TimeGenerated', 'EventID', 'EventCategory',
                'SourceName', 'Computername', 'UserSid', 'Description', 'Data')

        if isfile(filename):
            f = open(filename,'rb')
            s = f.read()
            byte_list = s.split('LfLe')
            f.close()
            del(s)
            if self._verify_file_header(byte_list):
                del byte_list[0] # Remove the 2 first entries since that is the header.
                del byte_list[0]
                for item in byte_list:
                    d = self._get_entry_header(item)
                    if self._verify_header(d,len(item)):
                        self._add_entry_values(d,item)
                        self._insert_entry(d)
            else:
                print "File: " + filename + " is not a windows logfile."
            del(byte_list)
        else:
            print "File: " + filename + " does not exist."

    def __len__(self):
        return len(self._current_list)

    def __str__(self):
        return str(self._current_list)

    def __repr__(self):
        return repr(self._current_list)

    def __iter__(self):
        return iter(self._current_list)

    def __reversed__(self):
        return self._current_list.__reversed__()

    def __getitem__(self,i):
        return self._current_list[i]

    def __getslice__(self,i,j):
        return self._current_list[i:j]

    def _translate_to_new_tuple(self,new_tuple,old_tuple):
        d = dict()
        for i in range(len(self._current_tuple)):
            d[self._current_tuple[i]] = old_tuple[i]
        t = tuple()
        for i in new_tuple:
            t += (d[i],)
        return t

    def sort(self):
        """Sorts the list according to the sortorder."""
        self._current_list.sort()

    def reverse(self):
        self._current_list.reverse()

    def count(self,value):
        return self._current_list.count(value)

    def getsortorder(self):
        """Returns the sortorder."""
        return self._current_tuple

    def setsortorder(self,new_tuple=None):
        """Takes a tuple to change the sort priority.
        You only need to supply the values that you need to sort by."""
        if new_tuple != self._current_tuple:
            for i in self._current_tuple:
                if i not in new_tuple:
                    new_tuple += (i,)
            if len(self._filtered_list) > 0: # If filters are enabled
                for i in xrange(len(self._filtered_list)):
                    self._filtered_list[i] = self._translate_to_new_tuple(new_tuple,self._filtered_list[i])
            for i in xrange(len(self._original_list)):
                self._original_list[i] = self._translate_to_new_tuple(new_tuple,self._original_list[i])
            self._current_tuple = new_tuple

    def clearfilter(self):
        """This will remove all filters that are set."""
        self._filtered_list = list()
        self._current_list = self._original_list

    def addfilter(self,field,test):
        """This will add a filter based on the numeric fieldnumber, and the test supplied.
        The test should be a string to be evaluated. e.g. '<= 11', '== 11'"""
        assert field < len(self._current_tuple)
        self._filtered_list = [item for item in self._current_list if eval(repr(item[field]) + test)]
        self._current_list = self._filtered_list

    def addfilterfunction(self,field,function):
        """This will add a filter based on a function that you pass in that evaluates to a boolean."""
        assert field < len(self._current_tuple)
        self._filtered_list = [item for item in self._current_list if function(item[field])]
        self._current_list = self._filtered_list

    def runtransformfunction(self,field,function):
        """This will transform the data in one of the fields based on the function passed."""
        assert field < len(self._current_tuple)
        for i in xrange(len(self._current_list)):
            t = tuple()
            for j in range(len(self._current_list[i])):
                if j == field:
                    t += function(l[i][j])
                else:
                    t += l[i][j]
                self._filtered_list[i] = t

