"""Module to provide utilities in working with Excel.

You must have windows tools installed for this to work.
"""

import win32com, win32com.client, win32com.client.gencache
import re, logging, tempfile, os, shutil

class ExcelLink:
    """Class to provide utilities in working with Excel.
    
    """

    # Things to potentially lock when editing spreadsheet.
    _propertiesToLock = [
        ('Interactive',False),('DisplayAlerts',False),('ScreenUpdating',None),
        ('Visible',None)
        ]
    
    def __init__(self,visible=True,independent=True):
        """Initializer.
        
	INPUTS:
        
	-- visible=True:	Whether spreadsheet should be visible.
        
	-- independent=True:	Whether to start an independent instance of
                                Excel or connect to an existing instance.
        
	-------------------------------------------------------
        
	PURPOSE:        Initializer.
        
        """
        self._independent = independent
        try:
            win32com.client.gencache.EnsureModule(
                '{00020813-0000-0000-C000-000000000046}', 0, 1, 2)
        except Exception,theException:
            logging.warning('Got exception: %s\nIgnoring.' % str(theException))
        if (independent): # create independent instance of Excel
            self.xl = win32com.client.gencache.GetClassForProgID(
                'Excel.Application')()
        else: # connect to existing instance of Excel if one exists
            self.xl = win32com.client.gencache.EnsureDispatch(
                'Excel.Application')
            
        from win32com.client import constants
        self._constants = constants        
        self._originalPropertyValues = []
        self.xlVersion = self.xl.Version
        self.xlVersion = float(self.xlVersion)
        
        if (None != visible): self.xl.Visible = visible

    def Constants(self):
        """
        A nice way of getting access to all of the excel constants without
        making pylint unhappy.
        """
        return self._constants
    
    def __del__(self):
        if (self._independent):
            self.xl.DisplayAlerts = False
            self.xl.Visible, self.xl.Instance = True,True # so user can close
            self.xl.Quit()
            self.xl = None
        
    def Lock(self,propertiesToLock=None):
        """Lock some properties of the spreadsheet to prevent user interference.

        You can use the Lock method when you want to modify a spreadsheet
        and prevent user interference. For safety, you should probably use
        something like

        try:
                xl.Lock()
                ...
        finally:
                xl.Unlock()

        tp prevent the spreadsheet from locking up if an error occurs.
        """
        if (propertiesToLock is None):
            propertiesToLock = self._propertiesToLock

        # self._originalPropertyValues is a stack because Lock()
        # can be called multiple times in succession.
        self._originalPropertyValues.append([
            getattr(self.xl.Application,n) for n,_v in propertiesToLock])
        for (name,value) in propertiesToLock:
            if (value != None):
                setattr(self.xl.Application,name,value)

    def Unlock(self,propertiesToLock=None):
        """Unlock a spreadsheet locked by the Lock method.
        """
        if (propertiesToLock is None): propertiesToLock = self._propertiesToLock
        assert 0 != len(self._originalPropertyValues), (
            'You must call Lock before calling Unlock!.')
        latestOriginalPropertyValues = self._originalPropertyValues.pop()
        for ((name,_value),original) in zip(
            propertiesToLock,latestOriginalPropertyValues):
            setattr(self.xl.Application,name,original)

    @classmethod
    def CellName(cls,row,col,sheetName=None):
        "Return name of cell at given row and col. "
        if sheetName is None:
            return cls.ColumnString(num=col)+str(row)
        else:
            return sheetName+ '!' +cls.ColumnString(num=col)+str(row)
        
    @classmethod
    def ColumnString(cls,num):
        """Return string representation for given column number.

        INPUTS:

        -- num:	Positive integer represnting the ith column.

        -------------------------------------------------------

        RETURNS:    String representation used by Excel for the ith column.

        -------------------------------------------------------

        PURPOSE:    Convert something like num=27 into something like 'AA' to
                    map integers to Excel column headings.

        """
        assert num > 0, 'Excel starts counting from 1 not %i.' % num
        assert num <= 256, 'Most version of Excel have at most 256 columns.' 
        if (num <= 26): result = chr(num + 64)
        else: result = chr(((num - 1) / 26) + 64) + chr(((num - 1) % 26) + 65)
        return result

    def NewNamedSheet(self,sheetName,after=None,before=None):
        """Create a new sheet with the given name.

        INPUTS:

        -- sheetName:   String name for the new sheet.

        -- after:       String indicating sheet that this should be
                        inserted after.

        -- before:      String indicating sheet that this should be
                        inserted before.
        -------------------------------------------------------

        PURPOSE:    Creates a new sheet with the given sheet name containing
                    the given data as shown below:

        """
        assert len(sheetName) < 32, 'Excel requires names to be < 31 chars.'
        if (None == self.xl.ActiveWorkbook): # no workbook exists
            self.xl.Workbooks.Add()
        worksheets = self.xl.Worksheets
        if (after != None): worksheets.Add(After=self.xl.Sheets(after))
        elif (before != None): worksheets.Add(Before=self.xl.Sheets(before))
        else: worksheets.Add(After=worksheets(worksheets.Count))
            
        sheet = self.xl.ActiveSheet
        sheet.Name = sheetName

    def AllSheetNames(self):
        """
        Returns all the names of the sheets of the active workbook,
        in order
        """
        workbook = self.xl.ActiveWorkbook
        names =[]
        for i in range(workbook.Sheets.Count):
            names.append( workbook.Sheets(i+1).Name)
        return names
            
    def NewNamedChart(self,chartName,after=None,before=None,
                      typeName=None,xlabel=None,ylabel=None,title=None,
                      yMinScale = None):
        """Create a new chart with the given name.

        INPUTS:

        -- chartName:   String name for the new chart.

        -- after:       String indicating chart that this should be
                        inserted after.

        -- before:      String indicating chart that this should be
                        inserted before.
        -------------------------------------------------------

        PURPOSE:    Creates a new chart with the given chart name containing
                    the given data as shown below:

        """
        assert len(chartName) < 32, 'Excel requires names to be < 31 chars.'
        self.xl.Charts.Add()        
        self.xl.ActiveChart.Name = chartName
        chart = self.xl.ActiveChart
        if (None != typeName):
            chart.ChartType = getattr(self._constants,typeName)
        chart.SeriesCollection().NewSeries() # add series to make Excel happy
        if (None != xlabel):
            chart.Axes(self._constants.xlCategory).HasTitle = True        
            chart.Axes(self._constants.xlCategory).AxisTitle.Text = xlabel
        if (None != ylabel):
            chart.Axes(self._constants.xlValue).HasTitle = True        
            chart.Axes(self._constants.xlValue).AxisTitle.Text = ylabel
        if yMinScale is not None:
            chart.Axes(self._constants.xlValue).MinimumScale = yMinScale
        if (None != title):
            chart.HasTitle = True
            chart.ChartTitle.Text = title
        while (chart.SeriesCollection().Count > 0):
            chart.SeriesCollection(1).Delete() # empty the chart

        # Now move to correct location. Can't seem to use Before/After in
        # call to create chart because of weird Excel bugs.
        if (after != None):
            self.xl.Sheets(chartName).Move(After=self.xl.Sheets(after))
        elif (before != None):
            self.xl.Sheets(chartName).Move(Before=self.xl.Sheets(before))
        else: # before or after so move to end of charts
            count = self.xl.Charts.Count
            if (count > 0):
                self.xl.Sheets(chartName).Move(After=self.xl.Charts(count))
            
        return self.xl.ActiveChart

    @staticmethod
    def SetChartProperties(chart,borderLineStyle=None, legendOn=None,
                           interiorColorIndex=None,
                           chartTitleLeftEdge=None,
                           chartTitleHorizAlign=None,
                           chartLegendTopEdge=None,
                           chartPlotAreaWidth=None,):
        """
        function to manipulate various properties of an excel chart.
        Any of the arguments can be left blank, which just means that they
        will not be changed from the current settings.

        Clearly this can be embellished upon to set more properties.

        INPUTS:
        chart:  an excel chart
        borderlineStyle:  sets the style of the line to use for the
                borders.  For example xlDash or xlNone
        legendOn:  boolean to specify whether there should be legend
                in the graph.
        interiorColorIndex: color index of the plot area.
        chartTitleLeftEdge: distance from the left edge of the chart
                title to the chart's left edge
        chartLegendTopEdge: distance from the top edge of the legend
                to the chart's top edge
        chartPlotAreaWidth: width of the chart's plot area.

        """
        if borderLineStyle is not None:
            chart.PlotArea.Border.LineStyle=borderLineStyle

        if legendOn is not None:
            if legendOn == False:
                chart.Legend.Delete()

        if interiorColorIndex is not None:
            chart.PlotArea.Interior.ColorIndex=interiorColorIndex

        if chartTitleLeftEdge is not None:
            chart.ChartTitle.Left = chartTitleLeftEdge

        if chartTitleHorizAlign is not None:
            chart.ChartTitle.HorizontalAlignment = chartTitleHorizAlign

        if chartLegendTopEdge is not None:
            chart.Legend.Top = chartLegendTopEdge
                
        if chartPlotAreaWidth is not None:
            chart.PlotArea.Width = chartPlotAreaWidth

    def SetPageSetup(self,sheetName, PrintAreaRange = None,
                     Orientation = None, FitToPagesWide = None,
                     FitToPagesTall = None):
        """
        Alter the page setup settings for printing purposes
        -------------------------
        INPUTS:
        sheetName: string name of the sheet that we are changing
                   the page setup.
        PrintAreaRange: a string, like 'A4:Z25', representing
                   the print area.
        Orientation: a constant representing landscape or portrait:
                   e.g. xl.Constants().xlLandscape
        FitToPagesWide:  an int.  Tells how many pages wide to let
                   the print out be.
        FitToPagesTall:  an int.  Tells how many pages tall to let
                   the print out be.                   
        """
        pageSetup = self.xl.Sheets(sheetName).PageSetup
        if PrintAreaRange is not None:
            pageSetup.PrintArea = PrintAreaRange
        if Orientation is not None:
            pageSetup.Orientation = Orientation
        if FitToPagesWide is not None:
            pageSetup.FitToPagesWide = FitToPagesWide
            pageSetup.Zoom = False
        if FitToPagesTall is not None:
            pageSetup.FitToPagesTall = FitToPagesTall
            pageSetup.Zoom = False            
        

            
    def InsertRows(self,insertionRowIndex,numRowsToInsert):
        """Insert blank rows.
        
	INPUTS:
        
	-- insertionRowIndex:   Integer index starting from 1 indicating
                                the point to insert new rows at.
        
	-- numRowsToInsert:	Integer number of rows to insert.
        
	-------------------------------------------------------
        
	PURPOSE:        Insert some blank rows into the current sheet.
        
        """
        sheet = self.xl.ActiveSheet
        rangeName = "A%i:A%i" % (insertionRowIndex,
                                 insertionRowIndex+numRowsToInsert-1)
        sheet.Range(rangeName).EntireRow.Insert(Shift=self._constants.xlDown)

    def InsertDataLists(self,dataLists,row=1,col=1):
        """Insert a list of lists into the current active sheet.
        
	INPUTS:
        
	-- dataLists:	A list of lists where dataLists[i][j] goes in
                        row i+1 and column j+1.
        
	-- row=1:	Row to start insertion at.
        
	-- col=1:	Column to start insertion at.

	-------------------------------------------------------

        RETURNS:        The pair (endRow, endCol) indicating the last
                        position for the inserted data.
        
	-------------------------------------------------------
        
	PURPOSE:        Insert a set of data at the given location.
        
        """
        endRow,endCol = None,None

        numRows = len(dataLists)
        numCols = max(map(len,dataLists))
        sheet = self.xl.ActiveSheet
        startCol, endCol = col,col+numCols-1
        startRow, endRow = row, row+numRows-1
        for i in range(len(dataLists)):
            rowNum = i+startRow
            rangeName = self.RangeName(rowNum,startCol,1,numCols)
            rangeData = [d if (d is not None) else '' for d in dataLists[i]]
            assert len(rangeData) == numCols
            safeData = [item if isinstance(item,(int,float,long,str))
                        else (item.encode('UTF-8') if isinstance(item,unicode)
                              else str(item)) for item in rangeData]
            try: # try and insert the full row
                sheet.Range(rangeName).Value = safeData
            except Exception, e:  # Something went wrong. Sometimes you have
                logging.warning(  # to insert things one at a time; so try it.
                'Got exception: %s inserting row to Excel; %s'
                % (str(e),'Trying separately for each col'))
                for colOffset in range(numCols):
                    sheet.Range(self.RangeName(rowNum,startCol + colOffset)
                    ).Value = safeData[colOffset]
                
                    

        return (endRow,endCol)

    def SetFont(self,row,col,bold=None, size=None,
                numRow=1, numCol=1):
        """
        set the font properties
        """
        xlRange = self.xl.Range(self.RangeName(row,col, numRow, numCol))
        
        font = xlRange.Font
        if bold is not None:
            font.Bold = bold
        if size is not None:
            font.Size=size


    def EnterFormula(self,row,col,formula,array=False,highlightIfAbove=None,
                     highlightIfBelow=None,NumberFormat=None,
                     highlightColorIndex=3,comment=None,insertName=None,
                     replaceable=None,extraReplaceable=None,
                     numRow=1, numCol=1):
        # suppress warning about to many args: pylint: disable-msg=R0913
        """Function to help enter a formula into Excel.
        
	INPUTS:
        
	-- row:	Integer row index for the formula (starting from 1)
        
	-- col:	Integer column index for the formula (starting from 1)
        
	-- formula:	String for the formula.
        
	-- array=False:	True if this is an array formula.
        
	-- highlightIfAbove=None:	If this is an integer, then conditional
                                        formatting will be used to highlight
                                        the cell if the value is above this.
        
	-- highlightIfBelow=None:	If this is an integer, then conditional
                                        formatting will be used to highlight
                                        the cell if the value is below this.
        
	-- NumberFormat=None:	String representing number format for the cell.
        
	-- highlightColorIndex=3:	Integer representing highlighting color.
        
	-- comment=None:	String comment for the cell.
        
	-- insertName=None:	String to name the cell.
        
	-- replaceable=None:	List of strings that are "replaceable" in the
                                formula. This is used to cram large array
                                formulas into excel to get around the character
                                limit. See _EnterLongArrayFormula for details.

        -- extraReplaceable:    List of strings to concatenate to replaceable.
                                You should use this if you want to also preserve
                                the replaceable words provided automatically.
        
	-------------------------------------------------------
        
	PURPOSE:        Enter a formula into Excel more conveniantly.
        
        """
        if (extraReplaceable is None): extraReplaceable = []
        xlRange = self.xl.Range(self.RangeName(row,col, numRow, numCol))
        if (array):
            if (len(formula)<170): xlRange.FormulaArray = formula
            else: self._EnterLongArrayFormula(
                xlRange,formula,replaceable,extraReplaceable)
        else: xlRange.Formula = formula
        if (None != highlightIfAbove):
            value,op=highlightIfAbove,self._constants.xlGreater
        elif (None != highlightIfBelow):
            value,op=highlightIfBelow,self._constants.xlLess
        else: value = None
        if (None != value):
            xlRange.FormatConditions.Add(self._constants.xlCellValue,op,value)
            xlRange.FormatConditions(1).Interior.ColorIndex= highlightColorIndex
            xlRange.FormatConditions(1).Interior.Pattern = (
                self._constants.xlPatternSolid)
        if (None != NumberFormat):
            xlRange.Cells.NumberFormat = NumberFormat
        if (None != comment and '' != comment):
            xlRange.Cells.AddComment(comment)
        if (None != insertName):
            self.xl.ActiveSheet.Names.Add(
                Name=insertName,RefersTo=xlRange,Visible=True)

    def _EnterLongArrayFormula(
        self,xlRange,formula,replaceable=None,extraReplaceable=None,
        repPat=None):
        """Get around the character limit in entering long formula into Excel.
        
	INPUTS:
        
	-- xlRange:	A Range object representing where to enter the formula.
        
	-- formula:	String formula to enter.
        
	-- replaceable=None:	List of strings that can be safely replaced.
                                See below for details.

        -- extraReplaceable:    List of strings to concatenate to replaceable.
        
	-- repPat=None:	String representing a pattern that does not appear in
                        formula. Will be chosen automatically if not provided.
        
	-------------------------------------------------------
        
	PURPOSE:        This method finds long words in formula that can
                        be replaced with repPat. The resulting shorter formula
                        is then inserted into Excel and the Replace method is
                        used to correct the formula once it has been entered.

                        For this to work, the words in replaceable must be
                        things that can be replaced with repPat and not
                        trigger Excel to complain about the formula being
                        invalid. For example, Excel doesn't complain if you
                        have a formula with function names that don't exist,
                        but it WILL complain if the formula syntax looks weird.
        """
        if (extraReplaceable is None): extraReplaceable = []
        if (None == replaceable): replaceable = [
            'AVERAGE','SUMPRODUCT'] # sample function names that are replaceable
        replaceable.extend(extraReplaceable)

        candidates = re.findall('(%s)'%(')|('.join(replaceable)),formula)
        candidates = [sorted(c,key=lambda x:-len(x))[0] for c in candidates]
        candidates = sorted(candidates,key=lambda x:-len(x))
        replacements = []
        shorterFormula = str(formula)
        for i in range(len(candidates)):
            repPat = self.__FindReplacementPattern(shorterFormula)
            assert repPat not in shorterFormula,"No safe place holder found."
            if (len(candidates[i]) > len(repPat)):
                shorterFormula = shorterFormula.replace(candidates[i],repPat)
                replacements.append((candidates[i],repPat))
                logging.debug('Replacing %s with %s to shorten Excel formula.'%(
                    candidates[i],repPat))

        xlRange.FormulaArray = shorterFormula
        for (item,repPat) in replacements:
            xlRange.Replace(repPat,item)

    @staticmethod
    def __FindReplacementPattern(chars):
        """Helper function for _EnterLongArrayFormula.
        
	INPUTS:
        
	-- chars:	String to find replacements in.
        
	-------------------------------------------------------
        
	RETURNS:        A two-letter string that does not appear in chars.
                        
        
	-------------------------------------------------------
        
	PURPOSE:        Find a replacement pattern that does NOT appear in
                        chars that we can use as a place-holder.
        
        """
        chars = set(chars)
        letters = ['_']+[chr(65+i) for i in range(26-1,-1,-1)]
        for x in letters:
            for y in letters:
                if (x != y and x not in chars and y not in chars):
                    return x+y
        return None

    def NewWorkbook(self,nameList=('Sheet1',)):
        """Create a new workbook.
        
	INPUTS:
        
	-- nameList=['Sheet1']:	List of strings representing names of sheets
                                the new workbook should contain.
        
        """
        assert len(nameList) > 0, 'Must have at least 1 sheet.'
        self.xl.Workbooks.Add()
        while (self.xl.Sheets.Count > len(nameList)):
            self.xl.ActiveSheet.Delete()
        while (self.xl.Sheets.Count < len(nameList)):
            self.xl.Sheets.Add(After=self.xl.Sheets(self.xl.Sheets.Count))
        for i in range(len(nameList)):
            self.xl.Sheets(i+1).Name = nameList[i]
        


    @classmethod
    def RangeName(cls,startRow,startCol,numRows=1,numCols=1,sheet=None,
                  refType='r'):
        """Create name of a range.
        
	INPUTS:
        
	-- cls:         ExcelLink class (usually provided automatically).
        
	-- startRow:	Integer indicating starting row (starting from row 1).

	-- startCol:	Integer indicating starting col (starting from col 1).
        
	-- numRows=1:	Number of rows in range. If None, means all Rows--
                        range is a column only range
        
	-- numCols=1:	Number of cols in range. If None, means all Cols--
                        range is a row only range
        
	-- sheet=None:	Name of sheet.

        -- refType='a': If 'a', produce an absolute reference (with $ signs).
                        If 'r' produce a reference without $ signs.
        
	-------------------------------------------------------
        
	RETURNS:        String of the form 'sheet!a1:b2' repreenting the
                        desired range in Excel.
        
	-------------------------------------------------------
        
	PURPOSE:        Translate integer coordinates to Excel range.
        
        """
        if (refType == 'a'): dollar = '$'
        elif (refType == 'r'): dollar = ''
        else: raise Exception('Invalid value %s for refType.' % refType)


        if (numRows is None) and (numCols is None):
            raise Exception(
                'Cannot have both numRows and numCols equal to None')
        elif (numRows is not None) and (numCols is not None):
            rangeStart = "%s%s%s%i" % (
                dollar,cls.ColumnString(startCol),dollar,startRow)
            rangeEnd = "%s%s%s%i" % (
                dollar,cls.ColumnString(startCol+numCols-1),
                dollar,startRow+numRows-1)
        elif numRows is None:
            #a purely columns range
            rangeStart = "%s%s" % (dollar, cls.ColumnString(startCol))
            rangeEnd = "%s%s" %(dollar, cls.ColumnString(startCol+numCols-1))
        elif numCols is None:
            #a purely row range
            rangeStart = "%s%i" % (dollar, startRow)
            rangeEnd = "%s%i" %(dollar, startRow + numRows-1)
        
        if (None != sheet): rangeName = '%s!%s:%s' % (
            sheet,rangeStart,rangeEnd)
        else: rangeName = rangeStart +':'+ rangeEnd

        return rangeName

    def SetCalculationToManual(self):
        "Make it so spreadsheet only recomputes formulas when requested."
        
        self.xl.Calculation = self._constants.xlCalculationManual

    def SetCalculationToAuto(self):
        "Make it so spreadsheet automatically recomputes formulas."
                
        self.xl.Calculation = self._constants.xlCalculationAutomatic


    def Close(self):
        "Close this instance of the excel window "

        self.xl.Application.DisplayAlerts = False
        active = self.xl.ActiveWorkbook
        if active is not None: active.Close()
        self.xl.Quit()
        
    def SaveActiveWorkbook(self, fileName):
        """
        Excel on some virtual machines may have trouble writing remote files
        directly. The solution here is to save the active workbook to a local
        temp file then move it to remote location.
        Note the input fileName must have a reasonable extension name to
        indicate the format.
        """
        extName = os.path.splitext(fileName)[1].strip()
        if len(extName) == 0:
            raise Exception(
                'Must provide an extension name in file name %s'%fileName)
        
        fd, localTemp = tempfile.mkstemp(suffix = extName)
        os.close(fd)
        try:
            self.xl.ActiveWorkbook.SaveCopyAs(localTemp)
            MakeDirectoryAndParents(os.path.dirname(os.path.abspath(fileName)))
            shutil.move(localTemp, fileName)
        finally:
            if os.path.exists(localTemp):
                os.remove(localTemp)

def MakeDirectoryAndParents(name):
    "Make directory and parent directories for given name."
    if (name in ['','.','..']):
        raise Exception('Invalid direcotry name "%s".' % name)
    logging.debug('Making directory and parents for %s.' % name)
    parent = os.path.dirname(name)
    if (not os.path.exists(parent)): MakeDirectoryAndParents(parent)
    if (not os.path.exists(name)): os.mkdir(name)

def TimeSeqToExcel(timeSeq, columnList=None,commonColumns=None,xl=None,
                   sheetName='Sheet',makeNewWorkbook=True):
    """Open the given TimeSeq in an Excel Workbook.

    INPUTS:

    -- columnList=None:     List of lists of the form

                   [(<colIndexes_1>,<name_1>),...,<colIndexes_n>,<name_n>]

                            where <colIndexes_i> is a list of integers
                            indicating which columns should go into
                            the sheet named <name_i>. If columnList==None,
                            then we just split the columns across as
                            many sheets as necessary.

    -- commonColumns=None:  List of integers indicating columns that should
                            be shown on each sheet. If this is None and
                            there is a column called 'event_date', then
                            it is used as a common column.

    -- xl=None:             Instance of ExcelLink to use in opening query.
                            Generally, this is None but you can provide
                            it if you want to open in a specific xl.

    -- sheetName='Sheet':   String prefix for sheets to put data into.

    -- makeNewWorkbook=True: Whether to create a new work book to put
                             the data into or work with existing workbook.

    -------------------------------------------------------

    PURPOSE:        Use COM to send the data to Excel for easy analysis.

    """
    if (xl is None):
        xl = ExcelLink(visible=True,independent=False)

    PutInNewSheet(timeSeq, sheetName, xl, commonColumns,
                  columnList, makeNewWorkbook=makeNewWorkbook,
                  makeNamedRanges=False)


def AddDataToOneSheet(timeSeq, columns, sheetName, xl, makeNamedRanges=True):
    """
    Put the data for the specified columns into the specified
    sheet in an xl object.  A named range variable is also added to
    to worksheet for every column.

    INPUTS:

    -- columns:  a list of integers which are indexes to this queries'
                 columns.  These are the columns which will be added
                 to this sheet.
    -- sheetName: the string name of the sheet.
    -- xl: an ExcelLink.ExcelLink object.

    RETURNS:
    -- a dictionary of the form: (column_name: excel_named_range)

    """
    namedRanges = {}
    headers = [[''] + timeSeq.GetColumnNames()]
    propertiesToLock = [('Interactive',False),('ScreenUpdating',True)]
    oldCalcValue = xl.xl.Calculation
    names = [timeSeq.GetColumnNames()[i] for i in columns]
    data =[[row[0]]+[row[index+1] for index in columns] for row in headers]
    data += [ ['' for i in range(1+len(columns))] ] # blank line
    firstRow = len(data)+1
    data += [ ['']+[row[index] for index in columns] for row in timeSeq.data]
    xl.xl.Sheets(sheetName).Activate()
    try:

        xl.xl.Calculation = (
            xl._constants.xlCalculationManual) # pylint: disable-msg=W0212,C0301
        xl.Lock(propertiesToLock)
        xl.InsertDataLists(data)
    finally:
        xl.xl.Calculation=oldCalcValue
        xl.Unlock(propertiesToLock)
    xl.xl.ActiveSheet.Columns.AutoFit()
    if makeNamedRanges:
        for i in range(0,len(names)):
            actualCol = i + 2
            xl.xl.ActiveSheet.Names.Add(
                Name = 'Col_%s'%actualCol,
                RefersTo = '=%s'%xl.RangeName(
                firstRow, actualCol, len(timeSeq.data),1, sheetName,
                refType='a'),
                Visible = True)
            namedRanges[names[i]] = '%s!Col_%s'%(sheetName, actualCol)
    xl.xl.ActiveSheet.Columns.AutoFit()
    xl.xl.ActiveSheet.Range(xl.RangeName(len(headers)+1,3)).Select()
    xl.xl.ActiveWindow.FreezePanes = True
    return namedRanges


def PutInNewSheet(timeSeq,sheetNameBase,xl, 
                  columnList = None,
                  commonColumns = None,
                  makeNewWorkbook=False,
                  makeNamedRanges=True):
    """Put the data in this query into worksheets.  

    INPUTS:

    -- sheetNameBase:   string representing the base string from which
                    the sheetName will be created.  For example, if
                    sheetName = 'data', the sheets will be called
                    'data1', 'data2', 'data3', etc.

    -- xl:   an ExcelLink.ExcelLink object.

    -- columnList=None:     List of lists of the form

                   [(<colIndexes_1>,<name_1>),...,<colIndexes_n>,<name_n>]

                            where <colIndexes_i> is a list of integers
                            indicating which columns should go into
                            the sheet named <name_i>. If columnList==None,
                            then we just split the columns across as
                            many sheets as necessary.

    -- commonColumns=None:  List of integers indicating columns that should
                            be shown on each sheet. If this is None and
                            there is a column called 'event_date', then
                            it is used as a common column.

    -- makeNewWorkbook=False: boolean specifying whether a new workbook
                              should be created before adding the worksheets.

    -------------------------------------------------------

    PURPOSE:        Use COM to send the data to Excel for easy analysis.

    """

    if (commonColumns is None):
        commonColumns = [timeSeq.GetColIndex('event_date')]
        if (commonColumns[0] is None): commonColumns = []        
    if (columnList is None):
        commonColumnsSet = set(commonColumns)
        numCols = len(timeSeq.GetColumnNames())
        colsPerSheet = 255 - len(commonColumns)
        columnList = [([j for j in range(0+i*colsPerSheet,
                                         min(numCols,(i+1)*colsPerSheet))
                        if (j not in commonColumnsSet)],
                       '%s%i'%(sheetNameBase,(1+i)))
                      for i in range(0,1+numCols//colsPerSheet)]
    allNamedRanges = {}
    if makeNewWorkbook:
        xl.NewWorkbook([sheetName for (cols,sheetName) in columnList])

    for (cols,sheetName) in columnList:
        if (not makeNewWorkbook):
            xl.NewNamedSheet(sheetName)

        cols = commonColumns + cols
        namedRanges=AddDataToOneSheet(timeSeq, cols, sheetName, xl,
                                      makeNamedRanges)
        allNamedRanges.update(namedRanges)
    xl.xl.Sheets(columnList[0][1]).Activate()
    return (allNamedRanges,
            [sheetName for (cols, sheetName) in columnList])



def _test():
    "Test docstrings in module."
    import doctest
    doctest.testmod()

if __name__ == "__main__":    
    _test()
    print 'Test finished.'
            
