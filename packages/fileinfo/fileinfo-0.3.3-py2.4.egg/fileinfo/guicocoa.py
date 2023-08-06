#!/usr/bin/env pythonw
# _*_ coding: UTF-8 _*_

###
### NOTE:  This is no longer the recommended way to build applications
### using the pyobjc bridge under with OS X.  In particular, applications
### work much better if they are constructed in a proper app wrapper.
###
### This app does demonstrate that it is possible to build full
### featured Cocoa apps without InterfaceBuilder.
###

import sys

import objc
from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper


ascImg = NSImage.imageNamed_("NSAscendingSortIndicator")
descImg = NSImage.imageNamed_("NSDescendingSortIndicator")
altCols = NSColor.controlAlternatingRowBackgroundColors()

# for c in altCols:
#     print c.colorUsingColorSpaceName_("NSCalibratedRGBColorSpace")


class AppDelegate(NSObject):

    def applicationDidFinishLaunching_(self, aNotification):
        self.sortColumn = None
        self.sortOrder = "Ascending"
        self.indexes = []


    def setTable(self, HEADER, TABLE, FOOTER):
        self.HEADER = HEADER
        self.TABLE = TABLE
        self.FOOTER = FOOTER


    def sayHello_(self, sender):
        print "Hello again, World!"


    def doubleClick_(self, sender):
        # double-clicking a column header causes clickedRow() to return -1
        print "doubleClick!", sender.clickedColumn(), sender.clickedRow()


    # NSTableView data source methods

    def numberOfRowsInTableView_(self, aTableView):
        return len(self.TABLE) + len(self.FOOTER)


    def tableView_objectValueForTableColumn_row_(
            self, aTableView, aTableColumn, rowIndex):
        col = int(aTableColumn.identifier())
        return (self.TABLE+self.FOOTER)[rowIndex][col]


    def tableView_setObjectValue_forTableColumn_row_(
            self, aTableView, anObject, aTableColumn, rowIndex):
        col = int(aTableColumn.identifier())
        (self.TABLE+self.FOOTER)[rowIndex][col] = anObject


    # NSTableView delegate methods

    def tableView_willDisplayCell_forTableColumn_row_(
            self, aTableView, aCell, aTableColumn, rowIndex):
        if rowIndex >= len(self.TABLE):
            aCell.setBackgroundColor_(NSColor.headerColor())
        else:
            aCell.setBackgroundColor_(altCols[rowIndex % 2])
        
    def tableView_didClickTableColumn_(self, aTableView, aTableColumn):
        col = int(aTableColumn.identifier())
        
        if self.sortColumn == None:
            self.sortColumn = col
            sortColumChanged = True
        elif self.sortColumn == col:
            sortColumChanged = False
        elif self.sortColumn != col:
            sortColumChanged = True
            self.sortColumn = col

        if not sortColumChanged:
            self.sortOrder = {
                "Ascending":"Descending", 
                "Descending":"Ascending"}[self.sortOrder]
        
        # memorize selected line if present
        if len(self.FOOTER) == 2:
            SELECTED = self.FOOTER[1]
            
        # add temp. columns, sort and reverse if needed
        tab = []
        for i, row in enumerate(self.TABLE):
            tab.append([row[col]] + row + [i in self.indexes])
        tab.sort()
        for tc in aTableView.tableColumns():
            aTableView.setIndicatorImage_inTableColumn_(None, tc)
        if self.sortOrder == "Descending":
            tab.reverse()
            aTableView.setIndicatorImage_inTableColumn_(descImg, aTableColumn)
            # aTableColumn.headerCell().drawSortIndicatorWithFrame_inView_ascending_priority_(aTableView, False, 0)
        elif self.sortOrder == "Ascending":
            aTableView.setIndicatorImage_inTableColumn_(ascImg, aTableColumn)

        # restore selected rows after sorting
        # (not clear how to build an NSIndexSet...)
        # aTableView.selectRowIndexes_byExtendingSelection_(anNSIndexSet, False)
        aTableView.selectAll_(self)
        selectedIndexes = [row[-1] for row in tab]
        for j, idx in enumerate(selectedIndexes):
            if not selectedIndexes[j]:
                aTableView.deselectRow_(j)

        # strip off temporary columns
        self.TABLE = [row[1:-1] for row in tab]

        # restore selected line if present
        if len(self.FOOTER) == 2:
            self.FOOTER[1] = SELECTED

        aTableView.reloadData()
        aTableView.setNeedsDisplay_(True)


    def tableView_shouldSelectRow_(self, aTableView, rowIndex):
        if rowIndex >= len(self.TABLE):
            return False
        return True


    def tableView_shouldEditTableColumn_row_(self, aTableView, aTableColumn, rowIndex):
        # only allow cells in the second column in odd rows to be edited
        return False # (rowIndex % 2) and aTableColumn.identifier() == "col_2"


    def tableViewSelectionDidChange_(self, notification):
        tableView = notification.object()
        
        indexSet = tableView.selectedRowIndexes()
        # indexSet.getIndexes_maxCount_inIndexRange_(indexSet.count(), None)
        newIndexes = []
        for i in range(indexSet.count()):
            if i == 0:
                idx = indexSet.firstIndex()
            else:
                idx = indexSet.indexGreaterThanIndex_(idx)
            newIndexes.append(idx)
        
        if newIndexes == []:
            self.FOOTER = self.FOOTER[:1]
        # elif [] == self.indexes != newIndexes:
        #     SELECTED = [["XXX"] * len(self.FOOTER[0])]
        #     self.FOOTER += SELECTED
        elif [] == self.indexes != newIndexes:
            SELECTED = []
            for colNum, col in enumerate(tableView.tableColumns()):
                if col.headerCell().stringValue() != "file":
                    val = sum([self.TABLE[i][colNum] for i in newIndexes])
                else:
                    val = "selected"
                SELECTED.append(val)
            self.FOOTER += [SELECTED]
        elif [] != self.indexes != newIndexes:
            SELECTED = []
            for colNum, col in enumerate(tableView.tableColumns()):
                if col.headerCell().stringValue() != "file":
                    val = sum([self.TABLE[i][colNum] for i in newIndexes])
                else:
                    val = "selected"
                SELECTED.append(val)
            del self.FOOTER[-1]
            self.FOOTER += [SELECTED]
            
        if newIndexes != self.indexes:
            tableView.reloadData()
        
        self.indexes = newIndexes

    # NSWindow delegate methods
    
    def windowShouldClose_(self, sender):
        app = NSApplication.sharedApplication().terminate_(sender)
        # return False

    # def windowDidResize_(self, sender):
    #     win = sender.object()
    #     sview = win.contentView().subviews()[0]
    #     print sview.autohidesScrollers() # verticalScroller()


def main(HEADER, TABLE, FOOTER):
    app = NSApplication.sharedApplication()

    # we must keep a reference to the delegate object ourselves,
    # NSApp.setDelegate_() doesn't retain it. A local variable is
    # enough here.
    delegate = AppDelegate.alloc().init()
    delegate.setTable(HEADER, TABLE, FOOTER)
    NSApp().setDelegate_(delegate)

    # create window
    
    win = NSWindow.alloc()
    wframe = ((200.0, 300.0), (500.0, 300.0))
    mask = NSTitledWindowMask | NSClosableWindowMask | \
            NSMiniaturizableWindowMask | NSResizableWindowMask
    win.initWithContentRect_styleMask_backing_defer_(
        wframe, mask, NSBackingStoreBuffered, False)
    win.setTitle_('Table results')
    win.setMinSize_((200, 150))
    win.setLevel_(NSNormalWindowLevel) # NSFloatingWindowLevel

    # create table view
    
    # frame = ((0, 50), (wframe[1][0], wframe[1][1]-50))
    frame = ((0, 0), wframe[1])
    tview = NSTableView.alloc().initWithFrame_(frame)
    win.contentView().addSubview_(tview)
    tview.setDelegate_(delegate)
    tview.setTarget_(delegate)
    # tview.setAction_("sayHello:")
    # tview.setDoubleAction_("doubleClick:")
    # tview.setAutosaveName_("TableView")
    # tview.setNeedsDisplay_(True)
    tview.setAutosaveTableColumns_(True)
    tview.setDataSource_(delegate)
    tview.setAllowsMultipleSelection_(True)
    tview.setAllowsEmptySelection_(True)
    tview.setGridStyleMask_(NSTableViewSolidVerticalGridLineMask)
    tview.setUsesAlternatingRowBackgroundColors_(True)
    for col in range(len(HEADER)):
        tcol = NSTableColumn.alloc().initWithIdentifier_(col)
        tcol.setWidth_(100)
        tcol.headerCell().setStringValue_(HEADER[col])
        tcol.headerCell().setDrawsBackground_(True)
        tcol.headerCell().setBackgroundColor_(NSColor.headerColor())
        # tcol.headerCell().setHighlighted_(True)
        # tcol.headerCell().setAction_("sayHello:")
        tcol.headerCell().setTarget_(delegate)
        tview.addTableColumn_(tcol)

    # create scroll view and put table view inside
    
    sview = NSScrollView.alloc().initWithFrame_(frame)
    win.contentView().addSubview_(sview)
    sview.window().setDelegate_(delegate)
    sview.setHasVerticalScroller_(True)
    sview.setHasHorizontalScroller_(True)
    sview.setAutohidesScrollers_(True)
    sview.setBorderType_(NSNoBorder)
    sview.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)
    sview.setDocumentView_(tview)
    
    win.makeFirstResponder_(sview)

    if False:
        print tview.numberOfColumns(), tview.numberOfRows()
        print tview.tableColumns()
        print tview.tableColumnWithIdentifier_("size")
        print tview.subviews()

    if False:
        # create quit button
            
        bye = NSButton.alloc().initWithFrame_(((10, 10), (80.0, 30.0)))
        win.contentView().addSubview_(bye)
        bye.setBezelStyle_(NSThickerSquareBezelStyle)
        bye.setTarget_(app)
        bye.setAction_('stop:')
        bye.setEnabled_(True)
        bye.setTitle_('Quit')

    # display it all
    win.display()
    win.orderFrontRegardless() ## but this one does
    # win.makeMainWindow()
    # win.makeKeyWindow()
   
    AppHelper.runEventLoop()
    

def test():
    TABLE = """\
    size;file(fake)
    608;crons
    8;ex.csv
    0;fonts
    123;imm.dat
    593;imm.license
    8417;profile1.xml.odt
    4240;UserDefaults.txt
    9999;total"""
    
    TABLE = [line.split(";") for line in TABLE.split("\n")]
    
    HEADER = TABLE[0]
    FOOTER = [TABLE[-1]]
    TABLE = TABLE[1:-1]
        
    main(HEADER, TABLE, FOOTER)


if __name__ == '__main__':
    try:
        TABLE = open(sys.argv[1]).read().strip()
    except IndexError:
        TABLE = """\
    size;file(fake)
    608;crons
    8;ex.csv
    0;fonts
    123;imm.dat
    593;imm.license
    8417;profile1.xml.odt
    4240;UserDefaults.txt
    9999;total"""
    
    TABLE = [line.split(";") for line in TABLE.split("\n")]
    
    HEADER = TABLE[0]
    FOOTER = [TABLE[-1]]
    TABLE = TABLE[1:-1]
        
    main(HEADER, TABLE, FOOTER)
