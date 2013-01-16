#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""
curvesAppearanceChooserDlg.py: 
    A Qt dialog for choosing plot appearance (symbols and lines) 
    for a QwtPlot-derived widget (like Taurusplot)
"""

from taurus.qt import Qt, Qwt5
from ui.ui_CurveStatsDialog import  Ui_CurveStatsDialog
from datetime import datetime
from taurus.qt.qtgui.resource import getIcon, getThemeIcon


class CurveStatsDialog(Qt.QDialog):
    """
    A dialog for configuring and displaying statistics from  curves of a plot
    """
    
    statColumns = ('points','min', 'max', 'mean', 'std', 'rms')
    def __init__(self, parent=None):
        super(CurveStatsDialog,self).__init__(parent)
        self.ui = Ui_CurveStatsDialog()
        self.ui.setupUi(self)
        
        plot = parent
        xIsTime = plot.getXIsTime()
        self.ui.minDTE.setVisible(xIsTime)
        self.ui.maxDTE.setVisible(xIsTime)
        self.ui.minSB.setVisible(not xIsTime)
        self.ui.maxSB.setVisible(not xIsTime)
        
        self.ui.minSB.setMinimum(float('-inf'))
        self.ui.minSB.setMaximum(float('inf'))
        self.ui.maxSB.setMinimum(float('-inf'))
        self.ui.maxSB.setMaximum(float('inf'))
        
        icon = getIcon(':/actions/system-search.svg')
        self.ui.selectMinPB.setIcon(icon)
        self.ui.selectMaxPB.setIcon(icon)
        
        
        self.refreshCurves()
        
        cbs = (self.ui.npointsStatCB, self.ui.minStatCB, self.ui.maxStatCB, 
               self.ui.meanStatCB, self.ui.stdStatCB, self.ui.rmsStatCB)
        self._checkboxToColMap = dict(zip(cbs, xrange(len(self.statColumns))))
        
        self.minPicker = Qwt5.QwtPlotPicker(Qwt5.QwtPlot.xBottom, 
                                         Qwt5.QwtPlot.yLeft,
                                         Qwt5.QwtPicker.PointSelection,
                                         Qwt5.QwtPicker.VLineRubberBand,
                                         Qwt5.QwtPicker.AlwaysOn, plot.canvas())
        
        self.maxPicker = Qwt5.QwtPlotPicker(Qwt5.QwtPlot.xBottom, 
                                         Qwt5.QwtPlot.yLeft,
                                         Qwt5.QwtPicker.PointSelection,
                                         Qwt5.QwtPicker.VLineRubberBand,
                                         Qwt5.QwtPicker.AlwaysOn, plot.canvas())
        
        self.minPicker.setEnabled(False)
        self.maxPicker.setEnabled(False)
        
        #initialize min and max display
        xmin = plot.axisScaleDiv(Qwt5.QwtPlot.xBottom).lowerBound()
        xmax = plot.axisScaleDiv(Qwt5.QwtPlot.xBottom).upperBound()
        
        self.minMarker = Qwt5.QwtPlotMarker()
        self.minMarker.setLineStyle(Qwt5.QwtPlotMarker.VLine)
        self.minMarker.setLinePen(Qt.QPen(Qt.Qt.green, 3))
        self.minMarker.setXValue(xmin)
        self.minMarker.attach(plot)
        self.minMarker.hide()
        
        self.maxMarker = Qwt5.QwtPlotMarker()
        self.maxMarker.setLineStyle(Qwt5.QwtPlotMarker.VLine)
        self.maxMarker.setLinePen(Qt.QPen(Qt.Qt.red, 3))
        self.maxMarker.setXValue(xmax)
        self.maxMarker.attach(plot)
        self.maxMarker.hide()
        
        if xIsTime:
            self.ui.minDTE.setDateTime(self._timestamptToQDateTime(xmin))
            self.ui.minDTE.setDateTime(self._timestamptToQDateTime(xmax))
        else:
            self.ui.minSB.setValue(xmin)
            self.ui.maxSB.setValue(xmax)
        
        curveStatsAction = Qt.QAction(getThemeIcon('view-refresh'), "Refresh available curves", self.ui.statsTW)
        curveStatsAction.setShortcut(Qt.Qt.Key_F5)
        self.connect(curveStatsAction, Qt.SIGNAL("triggered()"), self.refreshCurves)
        self.ui.statsTW.addAction(curveStatsAction)
        
        #connections
        for cb in cbs:
            self.connect(cb, Qt.SIGNAL('toggled(bool)'), self.onStatToggled)
        self.connect(self.ui.calculatePB, Qt.SIGNAL('clicked()'),self.onCalculate)
        self.connect(self.ui.selectMinPB, Qt.SIGNAL('clicked()'),self.onSelectMin)
        self.connect(self.ui.selectMaxPB, Qt.SIGNAL('clicked()'),self.onSelectMax)
        self.connect(self.minPicker, Qt.SIGNAL('selected(QwtDoublePoint)'), self.minSelected)
        self.connect(self.maxPicker, Qt.SIGNAL('selected(QwtDoublePoint)'), self.maxSelected)
        self.connect(self.ui.minSB, Qt.SIGNAL('valueChanged(double)'), self.onMinChanged)
        self.connect(self.ui.minDTE, Qt.SIGNAL('dateTimeChanged(QDateTime)'), self.onMinChanged)
        self.connect(self.ui.maxSB, Qt.SIGNAL('valueChanged(double)'), self.onMaxChanged)
        self.connect(self.ui.maxDTE, Qt.SIGNAL('dateTimeChanged(QDateTime)'), self.onMaxChanged)
        self.connect(self.ui.minCB, Qt.SIGNAL('toggled(bool)'), self.onMinChanged)
        self.connect(self.ui.maxCB, Qt.SIGNAL('toggled(bool)'), self.onMaxChanged)
        
    def _timestamptToQDateTime(self, ts):
        dt = datetime.fromtimestamp(ts)
        return Qt.QDateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond/1000)
    
    def _QDateTimeToTimestamp(self, qdt):
        return qdt.toTime_t() + qdt.time().msec()/1000.
    
    def onSelectMin(self):
        '''slot called when the user clicks on the selectMin button'''
        plot = self.parent()
        plot.getZoomers()[0].setEnabled(False)
        plot.canvas().setCursor(Qt.Qt.SplitHCursor)
        self.minPicker.setEnabled(True)
        self.hide()
        
    def minSelected(self, pos):
        '''slot called when the user has selected a min value from the plot'''
        self.show()
        self.ui.minCB.setChecked(True)
        self.minPicker.setEnabled(False)
        plot = self.parent()
        xmin = pos.x()
        if plot.getXIsTime():
            self.ui.minDTE.setDateTime(self._timestamptToQDateTime(xmin)) #this triggers a call to onMinChanged()
        else:
            self.ui.minSB.setValue(xmin) #this triggers a call to onMinChanged()
        self.restorePlot(keepMarkers=True)
        
    def onMinChanged(self, x):
        '''slot called when the min value is changed''' 
        plot = self.parent()     
        if isinstance(x, bool):
            self.minMarker.setVisible(x)
        else:
            if isinstance(x, Qt.QDateTime):
                x = self._QDateTimeToTimestamp(x)
            self.minMarker.setXValue(x)
        plot.replot()
        
    def onSelectMax(self):
        '''slot called when the user clicks on the selectMax button'''
        self.minPicker.setEnabled(False)
        plot = self.parent()
        plot.getZoomers()[0].setEnabled(False)
        plot.canvas().setCursor(Qt.Qt.SplitHCursor)
        self.maxPicker.setEnabled(True)
        self.hide()
        
    def maxSelected(self, pos):
        '''slot called when the user has selected a min value from the plot'''
        self.show()
        self.ui.maxCB.setChecked(True)
        self.maxPicker.setEnabled(False)
        plot = self.parent()
        xmax = pos.x()
        if plot.getXIsTime():
            self.ui.maxnDTE.setDateTime(self._timestamptToQDateTime(xmax)) #this triggers a call to onMaxChanged()
        else:
            self.ui.maxSB.setValue(xmax) #this triggers a call to onMaxChanged()
        self.restorePlot(keepMarkers=True)
                             
    def onMaxChanged(self, x):
        '''slot called when the max value is changed'''
        plot = self.parent()     
        if isinstance(x, bool):
            self.maxMarker.setVisible(x)
        else:
            if isinstance(x, Qt.QDateTime):
                x = self._QDateTimeToTimestamp(x)
            self.maxMarker.setXValue(x)
        plot.replot()
        
    def onStatToggled(self, checked):
        '''slot called when any of the stat checkboxes is toggled'''
        cb = self.sender()
        col = self._checkboxToColMap[cb]
        if checked:
            self.ui.statsTW.showColumn(col)
        else: 
            self.ui.statsTW.hideColumn(col)
        
    def refreshCurves(self):
        '''resets the table re-reading the curves from the plot'''
        plot = self.parent()
        self.ui.statsTW.clear()
        self.ui.statsTW.setColumnCount(len(self.statColumns))
        self.ui.statsTW.setHorizontalHeaderLabels(self.statColumns)
        self.curveNames = plot.getCurveNamesSorted()
        self.ui.statsTW.setRowCount(len(self.curveNames))
        for row,name in enumerate(self.curveNames):
            title = plot.getCurveTitle(name)
            item = Qt.QTableWidgetItem(title)
            self.ui.statsTW.setVerticalHeaderItem(row, item)
    
    def getSelectedRows(self):
        '''returns a list of row numbers corresponding to the selected rows of the table'''
        selected = []
        for rg in self.ui.statsTW.selectedRanges():
            for row in xrange(rg.topRow(), rg.topRow()+rg.rowCount()):
                selected.append(row)
        return selected
        
    def onCalculate(self):
        '''
        slot called when the calculate button is pressed. Performs the
        calculation of stats in the current limits for the currently selected
        curves (or for all if none selected) and fills the table.
        '''
        plot = self.parent()
        table = self.ui.statsTW
        
        xmin,xmax = None,None
        if self.ui.minCB.isChecked():
            if plot.getXIsTime():
                xmin = self.ui.minDTE.dateTime().toTime_t() + self.ui.minDTE.time().msec()/1000.
            else:
                xmin = self.ui.minSB.value()
        if self.ui.maxCB.isChecked():
            if plot.getXIsTime():
                xmax = self.ui.maxDTE.dateTime().toTime_t() + self.ui.maxDTE.time().msec()/1000.
            else:
                xmax = self.ui.maxSB.value()
        limits = xmin,xmax
        
        selectedRows = self.getSelectedRows()
        if len(selectedRows) == 0:
            selectedRows = range(len(self.curveNames))
        selectedCurves = [self.curveNames[i] for i in selectedRows]
        statsdict = plot.getCurveStats(limits=limits, curveNames=selectedCurves)
    
        for row, name in zip(selectedRows,selectedCurves):
            stats = statsdict[name]
            minx,miny = stats['min']
            maxx,maxy = stats['max']
            if plot.xIsTime:
                minx = datetime.fromtimestamp(minx).isoformat()
                maxx = datetime.fromtimestamp(maxx).isoformat()
                table.setItem(row,self.statColumns.index('min'), Qt.QTableWidgetItem("t=%s \ny=%g"%(minx,miny)))
                table.setItem(row,self.statColumns.index('max'), Qt.QTableWidgetItem("t=%s \ny=%g"%(maxx,maxy)))
            else:
                table.setItem(row, self.statColumns.index('min'), Qt.QTableWidgetItem("x=%g\ny=%g"%(minx,miny)))
                table.setItem(row, self.statColumns.index('max'), Qt.QTableWidgetItem("x=%g\ny=%g"%(maxx,maxy)))           
            
            for s in ('points', 'mean', 'std', 'rms'):
                table.setItem(row, self.statColumns.index(s), Qt.QTableWidgetItem("%g"%stats[s]))
        table.resizeColumnsToContents()
    
    def restorePlot(self, keepMarkers=False):
        '''leaves the parent plot in its original state'''
        plot = self.parent()
        plot.canvas().setCursor(Qt.Qt.CrossCursor)
        plot.getZoomers()[0].setEnabled(plot.getAllowZoomers())
        if not keepMarkers:
            self.minMarker.detach()
            self.maxMarker.detach()
        plot.replot()
        
    def closeEvent(self, event):
        '''See :meth:`Qwidget.closeEvent`'''
        plot = self.parent()
        self.restorePlot()
        plot.curveStatsAction.setEnabled(True)
        
    def showEvent(self, event):
        '''See :meth:`Qwidget.showEvent`'''
        plot = self.parent()
        self.minMarker.attach(plot)       
        self.maxMarker.attach(plot)        
        plot.replot()
            
        
                

