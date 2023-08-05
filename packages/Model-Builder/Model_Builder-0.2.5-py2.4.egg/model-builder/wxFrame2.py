# -*- coding:iso8859-1 -*-
#-----------------------------------------------------------------------------
# Name:        wxFrame2.py
# Purpose:     Data output frame (wx.grid.Grid)
#
# Author:      <Flávio Codeço Coelho>
#
# Created:     2003/02/04
# RCS-ID:      $Id: wxFrame2.py,v 1.3 2004/01/13 10:51:44 fccoelho Exp $
# Copyright:   (c) 2003 Flávio Codeço Coelho <fccoelho@uerj.br>
# Licence:     This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#-----------------------------------------------------------------------------
#Boa:Frame:wxFrame2

import wx
import wx.grid
from Numeric import *


def create(parent):
    return wxFrame2(parent)

[wxID_WXFRAME2, wxID_WXFRAME2GRID1, wxID_WXFRAME2STATUSBAR1,
 wxID_WXFRAME2TOOLBAR1,
] = [wx.NewId() for _init_ctrls in range(4)]

[wxID_WXFRAME2TOOLBAR1PLOT, wxID_WXFRAME2TOOLBAR1TOOLS0,
] = [wx.NewId() for _init_coll_toolBar1_Tools in range(2)]

class wxFrame2(wx.Frame):
    def _init_coll_statusBar1_Fields(self, parent):
        # generated method, don't edit
        parent.SetFieldsCount(1)

        parent.SetStatusText(number=0, text='Status')

        parent.SetStatusWidths([-1])

    def _init_coll_toolBar1_Tools(self, parent):
        # generated method, don't edit

        parent.AddTool(bitmap= wx.Bitmap('backup_section.png', wx.BITMAP_TYPE_PNG),
              id=wxID_WXFRAME2TOOLBAR1TOOLS0, isToggle=False,
              longHelpString='Save this table', pushedBitmap=wx.NullBitmap,
              shortHelpString='Save As')
        parent.DoAddTool(bitmap= wx.Bitmap('gnuplot.png',
              wx.BITMAP_TYPE_PNG), bmpDisabled=wx.NullBitmap,
              id=wxID_WXFRAME2TOOLBAR1PLOT, kind=wx.ITEM_NORMAL, label='plotSel',
              longHelp='Plot selected column', shortHelp='Plot')
        self.Bind(wx.EVT_TOOL, self.OnToolbar1tools0Tool, id=wxID_WXFRAME2TOOLBAR1TOOLS0)
        self.Bind(wx.EVT_TOOL, self.OnToolBar1Tools1Tool, id=wxID_WXFRAME2TOOLBAR1PLOT)

        parent.Realize()

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_WXFRAME2, name='', parent=prnt,
              pos= wx.Point(616, 397), size= wx.Size(683, 445),
              style=wx.DEFAULT_FRAME_STYLE, title='Output Table')
        self.SetClientSize(wx.Size(683, 445))

        self.statusBar1 = wx.StatusBar(id=wxID_WXFRAME2STATUSBAR1,
              name='statusBar1', parent=self, style=0)
        self._init_coll_statusBar1_Fields(self.statusBar1)
        self.SetStatusBar(self.statusBar1)

        self.toolBar1 = wx.ToolBar(id=wxID_WXFRAME2TOOLBAR1, name='toolBar1',
              parent=self, pos= wx.Point(0, 0), size= wx.Size(84, 42),
              style=wx.TB_HORIZONTAL | wx.NO_BORDER)
        self.toolBar1.SetToolTipString('')
        self.SetToolBar(self.toolBar1)

        self.grid1 =wx.grid.Grid(id=wxID_WXFRAME2GRID1, name='grid1', parent=self,
              pos= wx.Point(0, 0), size= wx.Size(683, 378), style=0)
        self.grid1.SetAutoLayout(True)

        self._init_coll_toolBar1_Tools(self.toolBar1)

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.filename = None

    def OnToolbar1tools0Tool(self, event):
        dlg = wx.FileDialog(self, "Save Data As", ".", "", "*.dat", wx.SAVE)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                f = open(filename,'w')
                for i in range(self.grid1.GetNumberRows()):
                    if i == 0:
                        for k in range(self.grid1.GetNumberCols()):
                            f.write(self.grid1.GetColLabelValue(k)+',')
                        f.write('\n')
                    for j in range(self.grid1.GetNumberCols()):
                        f.write(self.grid1.GetCellValue(i,j)+',')
                    f.write('\n')
                f.close()
        finally:
            dlg.Destroy()




    def OnToolBar1Tools1Tool(self, event):
        """
        Plot Selected columns
        """
        import PlotFigure as PF
        sel = self.grid1.GetSelectedCols()
        data = self.createDataMatrix()
        leg = tuple([self.grid1.GetColLabelValue(i) for i in self.grid1.GetSelectedCols()])
        y = []
        for i in sel:
            y.append(data[:,i])


        p=PF.create(None)
        p.SetTitle('Selected Variables')
        p.plot(data[:,0],y,leg)
        p.Show()


    def createDataMatrix(self):
        """
        create a Numeric array with the contents of the spreadsheet
        """
        rows = self.grid1.GetNumberRows()
        cols = self.grid1.GetNumberCols()
        data = zeros((rows-2,cols),Float)
        for i in range(rows-2):
            for j in range(cols):
                data[i,j] = float(self.grid1.GetCellValue(i+1,j))
        print data, data.shape, data[0,0]
        return data
