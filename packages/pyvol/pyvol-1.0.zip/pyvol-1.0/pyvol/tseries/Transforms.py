"""This module contains classes to transform inputs in a sequence.

For example, see the SeqXform class.
"""

class SeqXform:
    """
    The SeqXform class provides a way to modify or transform results
    of a TimeSeqSequence. Instances of SeqXform can be passed
    to the AddField method of the TimeSeq class.

    The interface for the SeqXform class is as follows:

       Constructor: The constructor takes the lists inputFields, outputFields
                    which specify the fields the transform will use and the
                    fields it will generate or replace. The inputFields are
                    mainly used to tell the transform what fields it will
                    operate on.

       Startup:     This method takes in the sequence to process and will be
                    called before processing starts. This is useful for
                    initializing various things.

       Shutdown:    This method takes in the sequence that has been processed
                    and is called after processing finishes.

       ProcessRow:  This is the main operation that a transform will implement.
                    It will be called with a dictionary where the keys are
                    columns that exist in the original sequence and the values
                    are the values for those fields for the current row. This
                    function should process the current row and return a
                    list of results corresponding to the outputFields.

       ProcessRowInSeq:   This is an alternative function to call instead of
                          ProcessRow. It will be called with the args
                          dictionary given to ProcessRow as well as the integer
                          line number for the current row and the query object
                          itself. As with ProcessRow, this function should
                          process the current row and return a list of results
                          corresponding to the outputFields. This function
                          should NOT modify query directly.

    ----- Any sub-class must implement functions above this point -----------
    ----- Functions below this point do not need to be overrideen -----------

       Update:      This method updates some internal data structures. It
                    shall be called for each row the transform operates on
                    before the ProcessRow/ProcessRowInSeq method. You
                    probably do not need to change this in your sub-class
                    but can use it to provide new kinds of SeqXform
                    classes to inherit from which track various data about
                    a sequence.

       PrepareIndexesAtStartup: Causes Startup method to lookup various indexes.
                    
    """

    def __init__(self,inputFields,outputFields,onlyIf=None):
        """
        
        INPUTS:
        
        -- inputFields: List of names describing input fields.
        
        -- outputFields: List of names describing output fields.
        
        -- onlyIf=None: Either None, or a callable object that takes two
                        arguments: a transform and the args dictionary
                        containing data for a given row and returns True
                        if and only if that row should be processed. If
                        False is returned, we don't even call transform.Update
                        for that transform. This is useful in filtering
                        what data a given transform or set of transforms
                        uses.

                        NOTE: You can also set self.onlyIf later.

                        NOTE: You can use QueryTransform.NoNAValuesInInputs
                              for onlyIf.
        
        """
        RequireListOrTupleOfStrings(inputFields,'inputFields')
        RequireListOrTupleOfStrings(outputFields,'outputFields')
        for item in ['history','histories','inputFields','outputFields',
                     'onlyIf']:
            assert not hasattr(self,item), """
            QueryTransform.__init__ sets %s; Do not set it before.""" % item
        self.inputFields = list(inputFields)
        self.outputFields = list(outputFields)
        self.histories = []
        self.historyFields = []
        self.onlyIf = ReturnTrue() if (None == onlyIf) else onlyIf
        self._started = False

        self._namesToSetup = None  # Set by PrepareIndexesAtStartup if desired
        self._inputIndexes = None  # Set by PrepareIndexesAtStartup if desired
        self._outputIndexes = None # Set by PrepareIndexesAtStartup if desired

    def PrepareIndexesAtStartup(self,inputNames,outputNames):
        """Tell Startup to prepare indexes for given names.
    
        INPUTS:
        
        -- inputNames:        List of names to put into self._inputIndexes.
        
        -- outputNames:       List of names to put into self._outputIndexes. 
        
        -------------------------------------------------------
        
        PURPOSE:        Make Startup prepare given indexes. See Startup.__doc__
                        for more details.
        
        """
        self._namesToSetup = [inputNames, outputNames]

    def Startup(self,query):
        """Prepare transform at startup.
        
        INPUTS:
        
        -- query:        QueryResult object to run transform on.
        
        -------------------------------------------------------
        
        PURPOSE:        If self._namesToSetup[0] is not None, it is
                        interpreted as a list of names to lookup in query
                        and put into self._inputIndexes. The same is done
                        for self._namesToSetup[1] and self._outputIndexes.

        SEE ALSO:       PrepareIndexesAtStartup sets up self._namesToSetup
                        
        Note: This method should not change the structure of the input query,
            for example, removing a column might screw up the column indicied
            we marked for stitching back the results from ProcessRow.
        """
        self._started = True
        if (self._namesToSetup is not None):
            inputNames, outputNames = self._namesToSetup
            if (inputNames is not None):
                self._inputIndexes = [query.GetColIndex(n) for n in inputNames]
            if (outputNames is not None):
                self._outputIndexes =[query.GetColIndex(n) for n in outputNames]
                
    
    def Shutdown(self,query):
        """Shutdown the transform after processing is finished.
        
        INPUTS:
        
        -- query:        Input sequence to work on.
        
        """
        _ignore = query # we ignore, but subclasses may want it
        self._started = False
        self._inputIndexes = None
        self._outputIndexes = None

    def Update(self, args):
        """Do whatever is required to update a transform before processing.
        
        INPUTS:

        -- args:        Dictionary where keys are string names of arguments
                        and values are the values for the current row.

        -------------------------------------------------------
        
        PURPOSE:        This method shall be called prior to ProcessRow
                        or ProcessRowInSeq for every line that the transform
                        operates on.

                        This makes it a useful hook for code that should
                        be run on every line. For example, if you want to
                        make a transform class that tracks the running sum
                        of something, you can use Update for that. Subclasses
                        could then override ProcessRow and still get the
                        running sum automatically calculated via Update.
        
        """
        # default version does nothing.
        _ignore = self, args

    def SetInputNames(self, nameList):
        """Set Input Names.   This function allows you to change
        the input field names of this transform.
        INPUTS:
        nameList:  a list of strings.  
        """
        if len(nameList) != len(self.inputFields):
            raise Exception(
                'Going from %d inputs to %d inputs\n',
                len(self.inputFields), len(nameList))
        self.inputFields = list(nameList)

    def SetOutputNames(self, nameList):
        """Set output names.  This function allows you to change
        the output field names of this transform.
        INPUTS:
        nameList:  a list of strings.
        """
        if len(nameList) != len(self.outputFields):
            raise Exception(
                'Going from %d outputs to %d outputs\n',
                len(self.outputFields), len(nameList))
        self.outputFields = list(nameList)
        
    def ProcessRow(self,args):
        """Method to process a row of data.
        
        INPUTS:
        
        -- args:        Dictionary where keys are string names of arguments
                        and values are the values for the current row.
        
        -------------------------------------------------------
        
        RETURNS:        List of results corresponding to self.outputFields.
        
        -------------------------------------------------------
        
        PURPOSE:        Process the current row. See comment in class docstring.
        
        """
        _ignore = self, args
        raise Exception('You must override ProcessRow or ProcessRowInSeq.')

    def ProcessRowInSeq(self,args,query,line):
        """Method to process a row of data.
        
        INPUTS:
        
        -- args:        Same as for ProcessRow.
        
        -- query:       The QueryResult object we are working on.
        
        -- line:        Integer indicating which row of query.data we are
                        working on.
        
        -------------------------------------------------------
        
        RETURNS:        Same as ProcessRow.
        
        -------------------------------------------------------
        
        PURPOSE:        This method has the same purpose as ProcessRow, but
                        also gets query and line as arguments. This makes
                        it easier to do computations which may depend on
                        past and future data.
        """
        # If user has not overridden this, then just call ProcessRow method.
        _ignore = query, line
        return self.ProcessRow(args)

    @staticmethod
    def ProcessTransformList(transformList,args,query,line):
        """
        
        INPUTS:
        
        -- transformList:       List of QueryTransform objects.
        
        -- args:                Dictionary of arguments for a given row.
        
        -------------------------------------------------------
        
        RETURNS:        List of results from all transforms in transformList.
        
        -------------------------------------------------------
        
        PURPOSE:        Update and process all the transforms in
                        transformList. One reason that this is a static
                        method is so that other things like MultiTransform
                        can process a bunch of transforms on a given row.
        """
        fullResult = []
        transformsToProcess = [t for t in transformList
                               if (not hasattr(t,'doNotProcess'))]
        for transform in transformsToProcess:
            if (transform.onlyIf(transform,args)):
                transform.Update(args)
                result = transform.ProcessRowInSeq(args,query,line)
                if (not isinstance(result, list)):
                    raise TypeError('Expected result of %s to be list; got %s'
                                    % (transform, result))
                assert len(result) == len(transform.outputFields), """
                Transform claims %i outputFields %s,\nbut returned %i : %s.
                """ % (len(transform.outputFields),transform.outputFields,
                       len(result),result)                
            else:
                result = [None]*len(transform.outputFields)
            for nameIndex in range(len(transform.outputFields)):
                args[transform.outputFields[nameIndex]] = result[nameIndex]
            fullResult.extend(result)
        return fullResult

def RequireListOrTupleOfStrings(arg,name=None,allowNone=False):
    """Complain if input is not a list/tuple of strings.
    
    INPUTS:
    
    -- arg:        Argument to check.
    
    -- name=None:  String name of variable we are checking. Only used to
                   create exception messages.
    
    -- allowNone=False:        Whether None is allowed or if we should
                               raise an exception on seeing it. 
    
    """
    if (allowNone and (None == arg)): return
    if (name == None):
        name = '(unnamed)'
    if ( (list == type(arg) or tuple == type(arg)) and
         ([str]*len(arg) == map(type,arg) or
          [unicode]*len(arg) == map(type,arg) ) ):
        pass
    else:
        raise TypeError("""
        Expected variable '%s' to be a list/tuple of strings, but it is
        a '%s' which is of %s.""" %(name,`arg`,type(arg)))


class ReturnTrue:
    "Class to represent function which always returns true"

    def __init__(self):
        pass

    @staticmethod
    def __call__(*args):
        "Return true"
        _ignore = args
        return True
