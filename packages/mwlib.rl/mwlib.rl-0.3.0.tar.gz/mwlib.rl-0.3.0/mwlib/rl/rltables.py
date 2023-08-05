#! /usr/bin/env python
#! -*- coding:utf-8 -*-

# Copyright (c) 2007, PediaPress GmbH
# See README.txt for additional licensing information.

from __future__ import division

import re

from reportlab.platypus.paragraph import Paragraph
from reportlab.lib import colors
from customflowables import Figure
import debughelper
from pdfstyles import pageWidth, pageHeight, pageMarginHor, table_p_style, table_p_style_small


def checkData(data):
    """
    check for cells that contain only list items - this breaks reportlab -> split list items in separate table rows
    """
    gotData = False # return [] if table contains no data
    onlyListItems = True
    maxCellContent = []
    maxCols = 0
    for row in data:
        _maxCellContent =0
        maxCols = max(maxCols,len(row))
        for cell in row:
            _maxCellContent = max(_maxCellContent,len(cell))
            for item in cell:
                gotData=True
                if not isinstance(item,Paragraph) or (isinstance(item,Paragraph) and item.style.name != 'li_style'):
                    onlyListItems = False
        maxCellContent.append(_maxCellContent)
    return (gotData, onlyListItems, maxCellContent, maxCols)


def splitData(data, maxCellContent):
    newData = []
    rowOffset = 0
    for (rowCount, row) in enumerate(data):
        for i in range(maxCellContent[rowCount]):
            newData.append(['']*len(row))
        for (colNum,cell) in enumerate(row):
            for (rowNum,item) in enumerate(cell):
                newData[rowNum+rowOffset][colNum] = [item]
        rowOffset += maxCellContent[rowCount]
    return newData            


def checkSpans(data):
    """
    use colspan and rowspan attributes to build rectangular table data array
    """
    styles = []
    rowspans = []
    maxCols = 0

    for (i,row) in enumerate(data):
        added_cells = 0
        for (j,cell) in enumerate(row):
            colspan = cell.get('colspan', 1)
            rowspan  = cell.get('rowspan', 1)
            if rowspan > (len(data) - i):  # check for broken rowspans
                rowspan = len(data) - i       
            if colspan > 1:
                styles.append( ('SPAN',(j,i), (j+colspan-1,i)) ) 
                for cols in range(colspan-1):
                    data[i].insert(j + 1,{'content':'','inserted':'colspan'})
            if rowspan > 1:
                styles.append( ('SPAN',(j,i),(j + colspan-1,i+rowspan-1)) )
                for row_offset in range(rowspan-1):
                    for c in range(colspan):
                        data[i+row_offset+1].insert(j,{'content':'', 'inserted':'rowspan'})

        maxCols = max(maxCols, len(data[i]))

    d = []
    for row in data: # extract content from cells
        newRow = [cell['content'] for cell in row] 
        while len(newRow) < maxCols: # make sure table is rectangular
            newRow.append('')
        d.append(newRow)

    return (d, styles)


def style(styles):
    """
    extract the style info and return a reportlab style list
    """
    borderBoxes = [u'prettytable', u'metadata', u'wikitable', u'infobox', u'toccolours', u'navbox']
    styleList = []
    hasBorder = False
    hasFrame = False
    if styles:
        #print "-"*20
        #print styles
        if styles.get('border',0) > 0:
            hasBorder = True
        if styles.get('background-color',0) >0: #fixme: this is probably not very accurate...
            hasFrame = True
        classes = set([ c.strip() for c in styles.get('class','').split()])
        if len(set(borderBoxes).intersection(classes)) > 0:
            hasBorder = True
        bs = styles.get('border-spacing',None)
        if bs:
            bs_val = re.match('(?P<bs>\d)',bs)
            if bs_val and int(bs_val.groups('bs')[0]) > 0:
                hasBorder = True

    styleList.append( ('VALIGN',(0,0),(-1,-1),'TOP') )
    if hasBorder:
        styleList.extend([ ('INNERGRID',(0,0),(-1,-1),0.25,colors.black),
                           ('BOX',(0,0),(-1,-1),0.25,colors.black),
                           ])
    elif hasFrame:
        styleList.extend([ ('BOX',(0,0),(-1,-1),0.25,colors.black),
                           ])        
    return styleList

def splitText(data):
    for row in data:
        for cell in row:
            for (i,e) in enumerate(cell):
                if isinstance(e, Paragraph):
                    # replace slashes and hyphens but dont't touch tags
                    newText = re.sub("\b(?P<leading>[^-\/<]*?)(?P<sep>[-\/])(?P<rest>[^-\/>]*?)\b","\g<leading> \g<sep> \g<rest>", e.text) 
                    cell[i] = Paragraph(newText, table_p_style_small) # FIXME: new Paragraph object needed. otherwise para isnt rendered again.
                if isinstance(e,Figure): # scale image to half size
                    cell[i] = Figure(imgFile = e.imgPath, captionTxt=e.captionTxt, captionStyle=e.cs, imgWidth=e.imgWidth/2.0,imgHeight=e.imgHeight/2.0, margin=e.margin, padding=e.padding,align=e.align)

            
def getColWidths(data, recursionDepth=0, nestingLevel=0):
    """
    the widths for the individual columns are calculated. if the horizontal size exceeds the pagewidth
    the fontsize is reduced 
    """

    if nestingLevel > 0:
        splitText(data)

    availWidth = pageWidth - pageMarginHor * 2
    minwidths  = [ 0 for x in range(len(data[0]))]
    summedwidths = [ 0 for x in range(len(data[0]))]
    maxbreaks = [ 0 for x in range(len(data[0]))]
    for row in data:        
        for (j,cell) in enumerate(row):
            cellwidth = 0
            for e in cell:
                minw, minh = e.wrap(0,pageHeight)
                maxw, maxh = e.wrap(availWidth,pageHeight)
                minw += 6  # FIXME +6 is the implicit cell padding we are using
                cellwidth += minw
                if maxh > 0:
                    rows = minh / maxh - 0.5 # approx. #linebreaks - smooted out - 
                else:
                    rows = 0
                minwidths[j] = max(minw, minwidths[j])
                maxbreaks[j] = max(rows,maxbreaks[j])
            summedwidths[j] = max(cellwidth, summedwidths[j])

    if nestingLevel > 0:
        return minwidths

    remainingSpace = availWidth - sum(summedwidths)
    if remainingSpace < 0 : 
        remainingSpace = availWidth - sum(minwidths)
        if remainingSpace < 0:
            if recursionDepth == 0:
                splitText(data)
                return getColWidths(data, recursionDepth=1, nestingLevel=nestingLevel)
            else:
                return None
        else:
            _widths = minwidths
    else:
        _widths = summedwidths
        
    totalbreaks = sum(maxbreaks)
    if totalbreaks == 0:
        return minwidths
    else:
        widths = [ _widths[col] + remainingSpace*(breaks/totalbreaks) for (col,breaks) in enumerate(maxbreaks) ]
        return widths
    

def splitCellContent(data):
    # FIXME: this is a hotfix for tables which contain extremly large cells which cant be handeled by reportlab
    import math
    n_data = []
    splitCellCount = 14 # some arbitrary constant...: if more than 14 items are present in a cell, the cell is split into two cells in two rows
    for row in data:
        maxCellItems = 0
        for cell in row:
            maxCellItems = max(maxCellItems,len(cell))
        if maxCellItems > splitCellCount:
            for splitRun in range(math.ceil(maxCellItems / splitCellCount)):
                n_row = []
                for cell in row:
                    if len(cell) > splitRun*splitCellCount:
                        n_row.append(cell[splitRun*splitCellCount:(splitRun+1)*splitCellCount])
                    else:
                        n_row.append('')                   
                n_data.append(n_row)                    
        else:
            n_data.append(row)
    return n_data
