"""This module provides the TimeSeq class.
"""

import logging, csv, copy

from Transforms import SeqXform

class TimeSeq:
    """A class for representing data indexed by time.
    """
    
    def __init__(self,columnNames,data):
        self.__colIndexByName = {}        
        self.__columnNames = list(columnNames)        
        self.__ResetNameForColumnDict()
        self.data =map(list,data) #convert from list of tuples to list of lists

        assert 0==len(self.data) or (
            len(self.data[0])==len(self.__columnNames)),"""
            Wrong number of columnNames for data. """

    def __ResetNameForColumnDict(self):
        """
        This function recreates the __colIndexByName dictionary. The
        __colIndexByName dictionary maps names to column indexes and is used
        by the GetColIndex function quickly look up the index for a
        column name
        """
        self.__colIndexByName = {}
        for i in range(len(self.__columnNames)):
            self.__colIndexByName[self.__columnNames[i]] = i

    def RemoveAllFieldsExcept(self,fieldsToKeep):
        """Remove all columns except for ones with the given indexes.
        
        INPUTS:
        
        -- fieldsToKeep:        List of integer columns to keep.
        
        -------------------------------------------------------
        
        PURPOSE:        Removes all fields except the ones given.
        
        """
        fieldsToKeep = sorted([(
            f if isinstance(f, (int, long)) else self.GetColIndex(f))
                               for f in fieldsToKeep])
        oldColumnNames = self.__columnNames
        self.__columnNames = []
        for i in fieldsToKeep:
            self.__columnNames.append(oldColumnNames[i])

        oldData = self.data
        self.data = [None]*len(oldData)
        append = self.data.append
        for row in range(len(oldData)):
            oldRow = oldData[row]
            self.data[row] = []
            append = self.data[row].append
            for i in fieldsToKeep:
                append(oldRow[i])

        del oldData
        del oldColumnNames
        self.__ResetNameForColumnDict()

    def RemoveFieldsNamed(self,fieldsToRemove):
        """Remove columns with the given names.
        
        INPUTS:
        
        -- fieldsToRemove:      List of strings representing columns to remove.
        
        -------------------------------------------------------
        
        PURPOSE:        Removes the given columns as shown in the following
                        example:

>>> exampleQ = TimeSeq(['day','qnt','price','dm'],[[1,2,2,4],[2,5,5,6]])
>>> print exampleQ.data
[[1, 2, 2, 4], [2, 5, 5, 6]]
>>> exampleQ.RemoveFieldsNamed(['qnt','dm'])
>>> print exampleQ.GetColumnNames()
['day', 'price']
>>> print exampleQ.data
[[1, 2], [2, 5]]
        
        """
        fieldsToRemove = set(fieldsToRemove)
        fieldsToKeep = [i for i in range(len(self.__columnNames))
                        if self.__columnNames[i] not in fieldsToRemove]
        return self.RemoveAllFieldsExcept(fieldsToKeep)

    @classmethod
    def ReadFromSimpleCSVFile(
        cls, filename):
        """
        Creates a TimeSeq object by reading data from a simple format
        CSV file.

        The format of the file is simply one line of header, and the
        rest are data.  There is no blank line between the header and
        the data.

        INPUTS:
        -- fileName; string name of CSV file to read

        RETURNS:
        -- a TimeSeq object.
        """

        fd = open(filename, "r")
        reader = csv.reader(fd)
        fields = reader.next()
        rows = []
        for line in reader:
            if len(line) == 0:
                continue
            if len(line) < len(fields):
                line.extend([None]*(len(fields)-len(line)))
            rows.append(line)

        return TimeSeq(fields, rows)

    def WriteToSimpleCSVFile(self, filename):
        """Writes a TimeSeq object to a simple CSV file format

        The format of the file is simply one line of header, and the
        rest are data.  There is no blank line between the header and
        the data.

        INPUTS:
        -- fileName; string name of CSV file to write to.

        """

        fd = open(filename, "w")
        writer = csv.writer(fd)
        writer.writerow(self.GetColumnNames())
        for line in self.data:
            writer.writerow(line)

    def AddFields(self,transformList,lines=None):
        """
        
        INPUTS:
        
        -- transformList:       A list of SeqXform objects to add
                                to this sequence.

        -- lines:               A generator indicating which lines of
                                of self.data to process. If this is None,
                                then all lines in self.data are processed.

        -------------------------------------------------------
        
        PURPOSE: Add the fields corresponding to the transforms in
                 transformList to this sequence. Specifically, this function
                 adds columns to this sequence corresponding to the outputFields
                 for the transfomrs in transformList and then populates these
                 fields by calling the transforms sequentially on every row.
                 Only those lines indicating by lines are processed.

                 Note that you can have later transforms refer to earlier
                 transforms.

    The following example illustrates usage how the lines argument can
    be combined with a generator such as the WeeklyDateJumper to process
    data on a weekly level:

>>> import datetime
>>> import Sequence
>>> from Transforms import SeqXform
>>> exampleQ = Sequence.TimeSeq(['day','price','quantity'],
... [[datetime.date(2000,1,1)+datetime.timedelta(i),i,i+1] for i in range(5)])
>>> class ExampleTransform(SeqXform):
...     def ProcessRow(self,args): return [args['price'] * args['quantity']]
... 
>>> exampleQ.AddFields([ExampleTransform([],['product_v2'])],
... (num for (num, line) in enumerate(exampleQ.data) if line[0].weekday() == 1))
>>> print '\\n'.join(map(str,exampleQ.data))
[datetime.date(2000, 1, 1), 0, 1, None]
[datetime.date(2000, 1, 2), 1, 2, None]
[datetime.date(2000, 1, 3), 2, 3, None]
[datetime.date(2000, 1, 4), 3, 4, 12]
[datetime.date(2000, 1, 5), 4, 5, None]

        """
        transformList = [t for t in transformList
                         if not getattr(t,'doNotProcess',False)]
        if (len(transformList)==0): return
        self.ComplainAboutNonTransforms(transformList)
        logging.debug('Applying transforms: %s.' %
                      ', '.join([str(t) for t in transformList]))
        nameList = sum([t.outputFields for t in transformList],[])
        adderList =sum([[str(t)]*len(t.outputFields) for t in transformList],[])
        self.AddBlankColumns(nameList,adderList)
        txRange = range(len(transformList))
        txSlice = []
        for transform in transformList:
            startCol = self.GetColIndex(transform.outputFields[0])
            endCol = self.GetColIndex(transform.outputFields[-1])
            assert startCol is not None and endCol is not None
            txSlice.append(slice(startCol,endCol+1))

        for t in transformList: t.Startup(self)
        numCols = len(self.__columnNames)
            
        if (None == lines): lines = xrange(len(self.data))
        for i in lines:
            args = {}
            for field in range(numCols):
                args[self.__columnNames[field]] = self.data[i][field]
            for txNum in txRange:
                result = SeqXform.ProcessTransformList(
                    [transformList[txNum]],args,self,i)
                self.data[i][txSlice[txNum]] = result

        for t in transformList: t.Shutdown(self)

    @staticmethod
    def ComplainAboutNonTransforms(transformList):
        "Complain about things in input list not instances of SeqXform"
        bads = [(i,t) for (i,t) in enumerate(transformList)
                if not isinstance(t, SeqXform)]
        if (bads):
            raise TypeError('''
            The following elements were not SeqXform instances:\n%s
            ''' % '\n'.join(['element %i: %s' % (i, t) for (i,t) in bads]))
        
    def _regr_test_AddFields(self):
        """
>>> import datetime
>>> from Transforms import SeqXform
>>> from Sequence import *
>>> exampleQ = TimeSeq(['day','price','quantity'],
... [[datetime.date(2000,1,1)+datetime.timedelta(i),i,i+1] for i in range(11)])
>>> class ExampleTransform(SeqXform):
...     def ProcessRow(self,args): return [args['price'] * args['quantity']]
>>> exampleQ.AddFields([ExampleTransform([],['product'])])
>>> print '\\n'.join(map(str,exampleQ.data))
[datetime.date(2000, 1, 1), 0, 1, 0]
[datetime.date(2000, 1, 2), 1, 2, 2]
[datetime.date(2000, 1, 3), 2, 3, 6]
[datetime.date(2000, 1, 4), 3, 4, 12]
[datetime.date(2000, 1, 5), 4, 5, 20]
[datetime.date(2000, 1, 6), 5, 6, 30]
[datetime.date(2000, 1, 7), 6, 7, 42]
[datetime.date(2000, 1, 8), 7, 8, 56]
[datetime.date(2000, 1, 9), 8, 9, 72]
[datetime.date(2000, 1, 10), 9, 10, 90]
[datetime.date(2000, 1, 11), 10, 11, 110]
>>> exampleQ.AddFields([ExampleTransform([],['product_v2'])],[0,2])
>>> print '\\n'.join(map(str,exampleQ.data))
[datetime.date(2000, 1, 1), 0, 1, 0, 0]
[datetime.date(2000, 1, 2), 1, 2, 2, None]
[datetime.date(2000, 1, 3), 2, 3, 6, 6]
[datetime.date(2000, 1, 4), 3, 4, 12, None]
[datetime.date(2000, 1, 5), 4, 5, 20, None]
[datetime.date(2000, 1, 6), 5, 6, 30, None]
[datetime.date(2000, 1, 7), 6, 7, 42, None]
[datetime.date(2000, 1, 8), 7, 8, 56, None]
[datetime.date(2000, 1, 9), 8, 9, 72, None]
[datetime.date(2000, 1, 10), 9, 10, 90, None]
[datetime.date(2000, 1, 11), 10, 11, 110, None]
>>> exampleQ.AddFields([ExampleTransform([],['product_v3'])],
... lines=(n for (n, line) in enumerate(exampleQ.data) if line[0].weekday()==1))
>>> print '\\n'.join(map(str,exampleQ.data))
[datetime.date(2000, 1, 1), 0, 1, 0, 0, None]
[datetime.date(2000, 1, 2), 1, 2, 2, None, None]
[datetime.date(2000, 1, 3), 2, 3, 6, 6, None]
[datetime.date(2000, 1, 4), 3, 4, 12, None, 12]
[datetime.date(2000, 1, 5), 4, 5, 20, None, None]
[datetime.date(2000, 1, 6), 5, 6, 30, None, None]
[datetime.date(2000, 1, 7), 6, 7, 42, None, None]
[datetime.date(2000, 1, 8), 7, 8, 56, None, None]
[datetime.date(2000, 1, 9), 8, 9, 72, None, None]
[datetime.date(2000, 1, 10), 9, 10, 90, None, None]
[datetime.date(2000, 1, 11), 10, 11, 110, None, 110]
        """

    def GetColIndex(self,name):
        """
        INPUTS:
        
        -- name:        String representing name of a column to lookup.
        
        RETURNS:        Integer representing index for the named column or
                        None if the column is not present.
        """
        simpleCol = self.__colIndexByName.get(name,None)

        return simpleCol

    def NameForColumn(self,index):
        "self.NameForColumn(index) returns the name of the column at index."
        return self.__columnNames[index]

    def GetColumnNames(self):
        "GetColumnNames(self): Returns names of columns in this sequence."
        return copy.deepcopy(self.__columnNames)

    def AddBlankColumns(self,nameList,adderList=None,default=None,
                        startingPos=-1):
        """Add blank columns to this sequence.
        
        INPUTS:
        
        -- nameList:    List of names for the columns to add.

        -- adderList:   List of strings (one for each element in nameList)
                        indicating who is adding the given name. This is
                        optional and can be left as None.

        -- default:     Value to add for new columns.
                        
        -- startingPos: Integer indicating the column number at which
                        to insert the new columns:
                          -1 indicates the last column.
                          0 indicates the first column.

                        For example, inserting 'NewColumn' to a columnList of
                        ['event_date', 'val1'] and at startingPos of 0 makes
                        the column List ['NewColumn', 'event_date', 'val1']
                        
        -------------------------------------------------------
        
        RETURNS:        List of indexes for the new columns.
        
        -------------------------------------------------------
        
        PURPOSE:        This function is useful if you want to add new
                        columns of data. First you call this to create the
                        columns and then you can set the values accordingly.

        The following illustrates example usage:

>>> exampleQ = TimeSeq(['day','qnt','price'],[[1,2,4],[8,5,9],[7,0,6]])
>>> exampleQ.AddBlankColumns(['foo','bar'])
[3, 4]
>>> print exampleQ.GetColumnNames()
['day', 'qnt', 'price', 'foo', 'bar']
>>> print exampleQ.data[-1]
[7, 0, 6, None, None]
>>> exampleQ.AddBlankColumns(['test1', 'test2'], startingPos = 1)
[1, 2]
>>> print exampleQ.GetColumnNames()
['day', 'test1', 'test2', 'qnt', 'price', 'foo', 'bar']
>>> print exampleQ.data[-1]
[7, None, None, 0, 6, None, None]
        """
        if (None == adderList): adderList = ['unknown']*len(nameList)
        numNames = len(nameList)
        if (numNames != len(set(nameList))): # duplicates exist in nameList
            for i in range(len(nameList)):
                if (nameList[i] in nameList[(i+1):]):
                    dupInd = nameList[(i+1):].index(nameList[i])
                    raise Exception(
                        "Name %s added at i=%i by %s and at i=%i by %s." % (
                        nameList[i],i,adderList[i],dupInd,adderList[dupInd]))
            raise Exception("Duplicate indexes in nameList.")
                        
        for name in nameList:
            assert not isinstance(name,(tuple,list)),'Names should be strings.'
            index = self.GetColIndex(name)
            if (None != index):
                raise Exception(
                    "Column %s can't be added; it already exists at index %i."
                    % (name,index))

        assert startingPos in [-1] + range(len(self.__columnNames))

        if startingPos == -1:
            startingPos = len(self.__columnNames)
        for name in nameList:
            self.__columnNames.insert(startingPos, name)
            for line in self.data:
                line.insert(startingPos, default)
            startingPos+=1

        self.__ResetNameForColumnDict()     # reset the column name dict

        return range(startingPos- len(nameList), startingPos)            

    def RenameColumns(self,oldNames,newNames):
        """Rename columns.
        
        INPUTS:
        
        -- oldNames:    List of old names for columns.
        
        -- newNames:    List of new names for columns.
        
        -------------------------------------------------------
        
        PURPOSE:        For each i, this function renames column oldNames[i]
                        to have the name newNames[i] as illustrated below:

>>> import Sequence
>>> exampleQ = Sequence.TimeSeq(['x','y','z'],[[0,1,2]])
>>> exampleQ.RenameColumns(['x','z'],['a','b'])
>>> print exampleQ.GetColumnNames()
['a', 'y', 'b']

        """
        if (len(oldNames)!=len(newNames)):
            raise Exception("oldNames and newNames must have the same length")
        if (len(oldNames) != len(set(oldNames))):
            raise Exception("oldNames list contains duplicates")
        if (len(newNames) != len(set(newNames))):
            raise Exception("newNames list contains duplicates")        
            
        indexes = [self.GetColIndex(n) for n in oldNames]
        if (None in indexes):
            raise Exception("No column named %s."%oldNames[indexes.index(None)])

        for i in range(len(indexes)):
            if (not isinstance(newNames[i],str)):
                raise Exception('Name %s is not a string.' % str(newNames[i]))
            self.__columnNames[indexes[i]] = newNames[i]

        self.__ResetNameForColumnDict()     # reset the column name dict

    def CopyColumns(self,oldNames,newNames):
        """Copy columns.
        
        INPUTS:
        
        -- oldNames:    List of old names for columns.
        
        -- newNames:    List of new names for columns.
        
        -------------------------------------------------------
        
        PURPOSE:        For each i, this function copies column oldNames[i]
                        into a new column named newNames[i] as shown below:

>>> import Sequence
>>> exampleQ = Sequence.TimeSeq(['x','y','z'],[[0,1,2],[3,4,5]])
>>> exampleQ.CopyColumns(['x','z'],['a','b'])
>>> print exampleQ.GetColumnNames()
['x', 'y', 'z', 'a', 'b']
>>> print exampleQ.data
[[0, 1, 2, 0, 2], [3, 4, 5, 3, 5]]

        """
        if (len(oldNames)!=len(newNames)):
            raise Exception("oldNames and newNames must have the same length")
        if (len(oldNames) != len(set(oldNames))):
            raise Exception("oldNames list contains duplicates")
        if (len(newNames) != len(set(newNames))):
            raise Exception("newNames list contains duplicates")        
            
        indexes = [self.GetColIndex(n) for n in oldNames]
        if (None in indexes):
            raise Exception("No column named %s."%oldNames[indexes.index(None)])

        for name in newNames:
            assert not isinstance(name,(tuple,list)),'Names should be strings.'
            index = self.GetColIndex(name)
            if (None != index):
                raise Exception(
                    "Column %s can't be added; it already exists at index %i."
                    % (name,index))
        self.__columnNames.extend(newNames) # add the new names
        self.__ResetNameForColumnDict()     # reset the column name dict
        self.data = [line + [line[i] for i in indexes] for line in self.data]
        



def _test():
    "Test docstrings in module."
    import doctest
    doctest.testmod()

if __name__ == "__main__":    
    _test()
    print 'Test finished.'
