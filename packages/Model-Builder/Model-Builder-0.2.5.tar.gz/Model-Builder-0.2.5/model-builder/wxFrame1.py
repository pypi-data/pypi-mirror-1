# -*- coding:iso8859-1 -*-
#-----------------------------------------------------------------------------
# Name:        wxFrame1.py
# Purpose:
#
# Author:      <Flavio Codeco Coelho>
#
# Created:     2003/02/04
# RCS-ID:      $Id: wxFrame1.py,v 1.11 2004/01/13 10:51:43 fccoelho Exp $
# Copyright:   (c) 2003 Flavio Codeco Coelho <fccoelho@fiocruz.br>
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
#Boa:Frame:wxFrame1

import wx
import wx.stc
from Numeric import *
from scipy import integrate
from string import *
from RandomArray import *
from MLab import *
import matplotlib
matplotlib.use('WXAgg')
from pylab import *
from matplotlib.cbook import *
import os
import wxFrame2, about

import uncertaintyMiniFrame
import PlotFigure as PF
from Bayes import Melding as meld
from time import *


os.chdir(os.getcwd())

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1, wxID_WXFRAME1CHECKBOX1, wxID_WXFRAME1CHECKBOX2, 
 wxID_WXFRAME1EQNEDIT, wxID_WXFRAME1GAUGE1, wxID_WXFRAME1PAREDIT, 
 wxID_WXFRAME1STATICLINE1, wxID_WXFRAME1STATICTEXT1, 
 wxID_WXFRAME1STATICTEXT10, wxID_WXFRAME1STATICTEXT11, 
 wxID_WXFRAME1STATICTEXT2, wxID_WXFRAME1STATICTEXT3, wxID_WXFRAME1STATICTEXT4, 
 wxID_WXFRAME1STATICTEXT5, wxID_WXFRAME1STATICTEXT6, wxID_WXFRAME1STATICTEXT7, 
 wxID_WXFRAME1STATICTEXT8, wxID_WXFRAME1STATICTEXT9, wxID_WXFRAME1STATUSBAR1, 
 wxID_WXFRAME1TEXTCTRL1, wxID_WXFRAME1TEXTCTRL2, wxID_WXFRAME1TEXTCTRL3, 
 wxID_WXFRAME1TEXTCTRL4, wxID_WXFRAME1TEXTCTRL5, wxID_WXFRAME1TEXTCTRL6, 
 wxID_WXFRAME1TEXTCTRL7, wxID_WXFRAME1TEXTCTRL8, wxID_WXFRAME1TOOLBAR1, 
] = [wx.NewId() for _init_ctrls in range(28)]

[wxID_WXFRAME1MENU1ITEMS0, wxID_WXFRAME1MENU1ITEMS1, wxID_WXFRAME1MENU1ITEMS2, 
 wxID_WXFRAME1MENU1ITEMS3, wxID_WXFRAME1MENU1ITEMS4, 
] = [wx.NewId() for _init_coll_menu1_Items in range(5)]

[wxID_WXFRAME1TOOLBAR1TOOLS0, wxID_WXFRAME1TOOLBAR1TOOLS1, 
 wxID_WXFRAME1TOOLBAR1TOOLS2, 
] = [wx.NewId() for _init_coll_toolBar1_Tools in range(3)]

[wxID_WXFRAME1MENU2ITEMS0] = [wx.NewId() for _init_coll_menu2_Items in range(1)]

[wxID_WXFRAME1MENU3ITEMS0] = [wx.NewId() for _init_coll_menu3_Items in range(1)]

class wxFrame1(wx.Frame):
    def _init_coll_menuBar1_Menus(self, parent):
        # generated method, don't edit

        parent.Append(menu=self.menu1, title='File')
        parent.Append(menu=self.menu2, title='Analysis')
        parent.Append(menu=self.menu3, title='Help')

    def _init_coll_menu3_Items(self, parent):
        # generated method, don't edit

        parent.Append(help='General Information about PyMM',
              id=wxID_WXFRAME1MENU3ITEMS0, kind=wx.ITEM_NORMAL, text='About')
        self.Bind(wx.EVT_MENU, self.OnMenu3items0Menu,
              id=wxID_WXFRAME1MENU3ITEMS0)

    def _init_coll_menu1_Items(self, parent):
        # generated method, don't edit

        parent.Append(help='Open a saved model.', id=wxID_WXFRAME1MENU1ITEMS0,
              kind=wx.ITEM_NORMAL, text='Open')
        parent.Append(help='Save your model.', id=wxID_WXFRAME1MENU1ITEMS1,
              kind=wx.ITEM_NORMAL, text='Save')
        parent.Append(help='Save your model on another file.',
              id=wxID_WXFRAME1MENU1ITEMS2, kind=wx.ITEM_NORMAL, text='Save As')
        parent.Append(help='Close your model.', id=wxID_WXFRAME1MENU1ITEMS3,
              kind=wx.ITEM_NORMAL, text='Close')
        parent.Append(help='Exit PyMM.', id=wxID_WXFRAME1MENU1ITEMS4,
              kind=wx.ITEM_NORMAL, text='Exit')
        self.Bind(wx.EVT_MENU, self.OnMenu1items0Menu,
              id=wxID_WXFRAME1MENU1ITEMS0)
        self.Bind(wx.EVT_MENU, self.OnMenu1items1Menu,
              id=wxID_WXFRAME1MENU1ITEMS1)
        self.Bind(wx.EVT_MENU, self.OnMenu1items2Menu,
              id=wxID_WXFRAME1MENU1ITEMS2)
        self.Bind(wx.EVT_MENU, self.OnMenu1items3Menu,
              id=wxID_WXFRAME1MENU1ITEMS3)
        self.Bind(wx.EVT_MENU, self.OnMenu1items4Menu,
              id=wxID_WXFRAME1MENU1ITEMS4)

    def _init_coll_menu2_Items(self, parent):
        # generated method, don't edit

        parent.Append(help='Enter uncertainty analysis mode',
              id=wxID_WXFRAME1MENU2ITEMS0, kind=wx.ITEM_CHECK,
              text='Uncertainty analysis')
        self.Bind(wx.EVT_MENU, self.OnMenu2items0Menu,
              id=wxID_WXFRAME1MENU2ITEMS0)

    def _init_coll_toolBar1_Tools(self, parent):
        # generated method, don't edit

        parent.AddTool(bitmap=wx.Bitmap('timemanagement_section.png',
              wx.BITMAP_TYPE_PNG), id=wxID_WXFRAME1TOOLBAR1TOOLS0,
              isToggle=False, longHelpString='Start your simulation.',
              pushedBitmap=wx.NullBitmap, shortHelpString='Start')
        parent.AddTool(bitmap=wx.Bitmap('mathematics_section.png',
              wx.BITMAP_TYPE_PNG), id=wxID_WXFRAME1TOOLBAR1TOOLS1,
              isToggle=False, longHelpString='Show typeset Equations',
              pushedBitmap=wx.NullBitmap, shortHelpString='Show equations')
        parent.AddTool(bitmap=wx.Bitmap('spreadsheet_section.png',
              wx.BITMAP_TYPE_PNG), id=wxID_WXFRAME1TOOLBAR1TOOLS2,
              isToggle=False, longHelpString='Show table with results',
              pushedBitmap=wx.NullBitmap, shortHelpString='Results')
        self.Bind(wx.EVT_TOOL, self.OnToolbar1tools0Tool,
              id=wxID_WXFRAME1TOOLBAR1TOOLS0)
        self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolbar1tools0ToolRclicked,
              id=wxID_WXFRAME1TOOLBAR1TOOLS0)
        self.Bind(wx.EVT_TOOL, self.OnToolbar1tools1Tool,
              id=wxID_WXFRAME1TOOLBAR1TOOLS1)
        self.Bind(wx.EVT_TOOL, self.OnToolbar1tools2Tool,
              id=wxID_WXFRAME1TOOLBAR1TOOLS2)

        parent.Realize()

    def _init_coll_statusBar1_Fields(self, parent):
        # generated method, don't edit
        parent.SetFieldsCount(1)

        parent.SetStatusText(number=0, text='Status')

        parent.SetStatusWidths([-1])

    def _init_utils(self):
        # generated method, don't edit
        self.menu1 = wx.Menu(title='File')

        self.menu3 = wx.Menu(title='Help')

        self.menuBar1 = wx.MenuBar()

        self.menu2 = wx.Menu(title='Analysis')

        self._init_coll_menu1_Items(self.menu1)
        self._init_coll_menu3_Items(self.menu3)
        self._init_coll_menuBar1_Menus(self.menuBar1)
        self._init_coll_menu2_Items(self.menu2)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_WXFRAME1, name='', parent=prnt,
              pos=wx.Point(336, 171), size=wx.Size(680, 457),
              style=wx.DEFAULT_FRAME_STYLE, title='Model Builder - ODE')
        self._init_utils()
        self.SetClientSize(wx.Size(680, 457))
        self.SetMenuBar(self.menuBar1)
        self.SetToolTipString('Model Builder')
        self.Bind(wx.EVT_CLOSE, self.OnWxFrame1Close)

        self.statusBar1 = wx.StatusBar(id=wxID_WXFRAME1STATUSBAR1,
              name='statusBar1', parent=self, style=0)
        self.statusBar1.SetSize(wx.Size(80, 19))
        self.statusBar1.SetPosition(wx.Point(-1, -1))
        self._init_coll_statusBar1_Fields(self.statusBar1)
        self.SetStatusBar(self.statusBar1)

        self.toolBar1 = wx.ToolBar(id=wxID_WXFRAME1TOOLBAR1, name='toolBar1',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(144, 42),
              style=wx.TB_HORIZONTAL | wx.NO_BORDER)
        self.toolBar1.SetToolTipString('')

        self.staticText1 = wx.StaticText(id=wxID_WXFRAME1STATICTEXT1,
              label='Differential Equations:', name='staticText1', parent=self,
              pos=wx.Point(8, 44), size=wx.Size(216, 16), style=0)

        self.staticText2 = wx.StaticText(id=wxID_WXFRAME1STATICTEXT2,
              label='Initial values:', name='staticText2', parent=self,
              pos=wx.Point(8, 224), size=wx.Size(240, 16), style=0)

        self.textCtrl1 = wx.TextCtrl(id=wxID_WXFRAME1TEXTCTRL1,
              name='textCtrl1', parent=self, pos=wx.Point(8, 244),
              size=wx.Size(264, 22), style=0, value='')
        self.textCtrl1.SetToolTipString('Initial conditions: values separated by spaces.')

        self.staticText3 = wx.StaticText(id=wxID_WXFRAME1STATICTEXT3,
              label='Start time:', name='staticText3', parent=self,
              pos=wx.Point(8, 274), size=wx.Size(72, 16), style=0)

        self.textCtrl2 = wx.TextCtrl(id=wxID_WXFRAME1TEXTCTRL2,
              name='textCtrl2', parent=self, pos=wx.Point(8, 289),
              size=wx.Size(80, 22), style=0, value='0')
        self.textCtrl2.SetToolTipString('Time value at the start of simulation')

        self.staticText4 = wx.StaticText(id=wxID_WXFRAME1STATICTEXT4,
              label='End Time:', name='staticText4', parent=self,
              pos=wx.Point(100, 274), size=wx.Size(76, 16), style=0)
        self.staticText4.SetToolTipString('Time value to end simulation')

        self.textCtrl3 = wx.TextCtrl(id=wxID_WXFRAME1TEXTCTRL3,
              name='textCtrl3', parent=self, pos=wx.Point(100, 289),
              size=wx.Size(80, 22), style=0, value='10')
        self.textCtrl3.SetToolTipString('Time value to end simulation')

        self.staticText5 = wx.StaticText(id=wxID_WXFRAME1STATICTEXT5,
              label='Time Step:', name='staticText5', parent=self,
              pos=wx.Point(190, 274), size=wx.Size(82, 16), style=0)

        self.textCtrl4 = wx.TextCtrl(id=wxID_WXFRAME1TEXTCTRL4,
              name='textCtrl4', parent=self, pos=wx.Point(190, 289),
              size=wx.Size(80, 22), style=0, value='0.1')
        self.textCtrl4.SetToolTipString('Time step for the output')

        self.staticText6 = wx.StaticText(id=wxID_WXFRAME1STATICTEXT6,
              label='Critical Time Steps:', name='staticText6', parent=self,
              pos=wx.Point(8, 316), size=wx.Size(144, 16), style=0)

        self.textCtrl5 = wx.TextCtrl(id=wxID_WXFRAME1TEXTCTRL5,
              name='textCtrl5', parent=self, pos=wx.Point(8, 332),
              size=wx.Size(168, 22), style=0, value='')
        self.textCtrl5.SetToolTipString('Time points where integration care should be taken.')

        self.staticText7 = wx.StaticText(id=wxID_WXFRAME1STATICTEXT7,
              label='First Step:', name='staticText7', parent=self,
              pos=wx.Point(190, 316), size=wx.Size(82, 16), style=0)

        self.textCtrl6 = wx.TextCtrl(id=wxID_WXFRAME1TEXTCTRL6,
              name='textCtrl6', parent=self, pos=wx.Point(190, 332),
              size=wx.Size(80, 22), style=0, value='0')
        self.textCtrl6.SetToolTipString('Size of the first step (0=auto)')

        self.staticText8 = wx.StaticText(id=wxID_WXFRAME1STATICTEXT8,
              label='Min. Step Size:', name='staticText8', parent=self,
              pos=wx.Point(8, 356), size=wx.Size(84, 16), style=0)

        self.textCtrl7 = wx.TextCtrl(id=wxID_WXFRAME1TEXTCTRL7,
              name='textCtrl7', parent=self, pos=wx.Point(8, 372),
              size=wx.Size(80, 22), style=0, value='0')
        self.textCtrl7.SetToolTipString('Minimum absolute step size allowed (0=auto).')

        self.staticText9 = wx.StaticText(id=wxID_WXFRAME1STATICTEXT9,
              label='Max Step Size:', name='staticText9', parent=self,
              pos=wx.Point(100, 356), size=wx.Size(84, 16), style=0)

        self.textCtrl8 = wx.TextCtrl(id=wxID_WXFRAME1TEXTCTRL8,
              name='textCtrl8', parent=self, pos=wx.Point(100, 372),
              size=wx.Size(80, 22), style=0, value='0')
        self.textCtrl8.SetToolTipString('Maximum absolute step size allowed (0=auto)')

        self.staticLine1 = wx.StaticLine(id=wxID_WXFRAME1STATICLINE1,
              name='staticLine1', parent=self, pos=wx.Point(305, 16),
              size=wx.Size(300, 4), style=wx.LI_VERTICAL| 1)
        self.staticLine1.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.staticLine1.SetToolTipString('')

        self.checkBox1 = wx.CheckBox(id=wxID_WXFRAME1CHECKBOX1,
              label='Full Output', name='checkBox1', parent=self,
              pos=wx.Point(344, 16), size=wx.Size(128, 24), style=0)
        self.checkBox1.SetValue(True)
        self.checkBox1.SetToolTipString('Check if you want the full output.')

        self.checkBox2 = wx.CheckBox(id=wxID_WXFRAME1CHECKBOX2,
              label='Show Convergence Message', name='checkBox2', parent=self,
              pos=wx.Point(344, 34), size=wx.Size(208, 24), style=0)
        self.checkBox2.SetValue(False)
        self.checkBox2.SetToolTipString('Check if you want the convergence message to be displayed.')
        self.checkBox2.Enable(True)
        self.checkBox2.SetThemeEnabled(True)

        self.staticText10 = wx.StaticText(id=wxID_WXFRAME1STATICTEXT10,
              label='Parameters:', name='staticText10', parent=self,
              pos=wx.Point(344, 60), size=wx.Size(88, 16), style=0)

        self.parEdit = wx.TextCtrl(id=wxID_WXFRAME1PAREDIT, name='parEdit',
              parent=self, pos=wx.Point(344, 75), size=wx.Size(192, 149),
              style=wx.HSCROLL | wx.TE_PROCESS_TAB | wx.VSCROLL | wx.TE_MULTILINE,
              value='')
        self.parEdit.SetToolTipString('Enter parameter values or expressions, one per line. Parameter should be refered to as p[0], p[1],... in the DEs.')
        self.parEdit.SetHelpText('Each line corresponds to one Parameter (p[0], p[1], ...)')

        self.gauge1 = wx.Gauge(id=wxID_WXFRAME1GAUGE1, name='gauge1',
              parent=self, pos=wx.Point(192, 372), range=100, size=wx.Size(80,
              20), style=wx.GA_HORIZONTAL, validator=wx.DefaultValidator)
        self.gauge1.SetLabel('Percent Done')
        self.gauge1.SetValue(0)
        self.gauge1.SetToolTipString('Percent Done')
        self.gauge1.SetHelpText('Show the percentage of the simulation done.')
        self.gauge1.SetShadowWidth(10)
        self.gauge1.SetBezelFace(1)

        self.staticText11 = wx.StaticText(id=wxID_WXFRAME1STATICTEXT11,
              label='Progress:', name='staticText11', parent=self,
              pos=wx.Point(192, 356), size=wx.Size(72, 16), style=0)

        self.eqnEdit = wx.TextCtrl(id=wxID_WXFRAME1EQNEDIT, name='eqnEdit',
              parent=self, pos=wx.Point(8, 64), size=wx.Size(264, 158),
              style=wx.HSCROLL | wx.TE_PROCESS_TAB | wx.TE_MULTILINE, value='')
        self.eqnEdit.SetToolTipString('ODE box. Enter one equation per line. Right hand side only.')

        self._init_coll_toolBar1_Tools(self.toolBar1)

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.FileName = None
        self.ModLoaded = None #no model has been loaded
        self.Neq = None
        self.modict = {'name':None, 'type':'ODE'}
        self.modbuilt = 0 #model has never been built
        self.modRan = 0 #model has never been ran
        self.plot = 0 #no plot has ever been generated
        self.gauge1.SetRange(100)
        self.uncertainty = 0 # uncertainty analysis is off

    def OnMenu1items0Menu(self, event):
        os.chdir(os.getcwd())
        dlg = wx.FileDialog(self, "Choose a file", ".", "", "*.ode", wx.OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                f = open(filename)
                self.modict = pickle.load(f)
                self.eqnEdit.SetValue(self.modict['equations'])
                self.textCtrl2.SetValue(str(self.modict['start']))
                self.textCtrl3.SetValue(str(self.modict['end']))
                self.textCtrl4.SetValue(str(self.modict['step']))
                self.textCtrl1.SetValue(str(self.modict['init']))
                self.parEdit.SetValue(self.modict['parameters'])
                self.FileName = filename
                self.SetTitle('Model Builder - '+filename)
                self.gauge1.SetValue(0)
                f.close()
                self.ModLoaded = 1
        finally:
            dlg.Destroy()



    def OnMenu1items1Menu(self, event):
        if self.FileName == None:
            return self.OnMenu1items2Menu(event)
        else:
            filename = self.FileName
            f = open(filename,'w')
            self.BuildModel(r=0) # call BuildModel without running the model
            pickle.dump(self.modict, f)
            f.close()


    def OnMenu1items2Menu(self, event):
        
        dlg = wx.FileDialog(self, "Save File As", ".", "", "*.ode", wx.SAVE)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                f=open(filename, 'w')
                if self.modbuilt: #check to see if model's dictionary has been built
                    pickle.dump(self.modict, f)
                else: #if not, build and then save
                    self.BuildModel(r=0) # call BuildModel without running the model
                    pickle.dump(self.modict, f)
                f.close()
                self.FileName = filename
                self.SetTitle('Model Builder - '+filename)

        finally:
            dlg.Destroy()


    def OnMenu1items3Menu(self, event):
        self.FileName = None
        self.ModLoaded = None
        self.eqnEdit.SetValue('')
        self.textCtrl2.SetValue('')
        self.textCtrl3.SetValue('')
        self.textCtrl4.SetValue('')
        self.textCtrl1.SetValue('')
        self.parEdit.SetValue('')
        self.SetTitle('Model Builder - ODE')


    def OnMenu1items4Menu(self, event):
        """
        Exit the program
        """

        self.Close()
        self.Destroy()


    def OnMenu2items0Menu(self, event):
        """
        If Uncertainty Analysis has been selected, it will Open the uncertainty panel to set
        the parameters for the analysis.
        """
        if not self.ModLoaded:
            self.OnMenu1items0Menu(event)
            return
        #--Checks if the Uncertainty item in the analysis menu (2) has been checked------

        if self.menu2.IsChecked(wx.ID_WXFRAME1MENU2ITEMS0):
            self.uncertaintyPanel=uncertaintyMiniFrame.create(None)
            self.uncertaintyPanel.Show()
            self.initUncertainty()
            self.uncertainty = 1 #raises uncertainty flag
        else:
            self.uncertainty = 0 #Uncertainty mode off
            try:
                self.uncertaintyPanel.Close()
            except:
                pass


    def checkErrors(self):
        """
        Check for normal editing errors in model definition
        """
        while not self.eqnEdit.GetValue()=='':
            val = strip(self.eqnEdit.GetValue()).split('\n')
            Neq = len(val)
            break
##~         Neq = int(self.eqnEdit.GetNumberOfLines()) #get number of ODEs
##~         while strip(self.eqnEdit.GetLineText(Neq-1)) == '': # avoid getting empty lines at the end of the eq. box
##~             Neq = Neq-1
##~             if Neq == 1:
##~                 break

        if not self.parEdit.GetValue() == '':
            valp = strip(self.parEdit.GetValue()).split('\n')
            Npar = len(valp)
        else:
            Npar = 0

##~         Npar = int(self.parEdit.GetNumberOfLines()) #get Number of  Parameters
##~         while strip(self.parEdit.GetLineText(Npar-1)) == '':# avoid getting empty lines at the end of the eq. box
##~             Npar=Npar-1
##~             if Npar == 1:
##~                 break
##~             if Npar == 0:
##~                 Npar = 1
##~                 break

#---Check number of initial conditions----------------------------------------------------------------------------
        if strip(self.textCtrl1.GetValue()) == '':
            ni = 0
        else:
            ni = len(strip(self.textCtrl1.GetValue()).split(' '))
        if not ni == Neq:
            return 1

#---Check that all initial conditions are numbers----------------------------------------------------------------------------
        for i in range(ni):
            try:
                float(strip(self.textCtrl1.GetValue()).split(' ')[i])
            except ValueError:
                e = 2
                return 2
#---Check syntax of equations----------------------------------------------------------------------------
        y=zeros(Neq)#fake equation array
        p=zeros(Npar)#fake parameter array
        t=0
        eqs = strip(self.eqnEdit.GetValue()).split('\n')
        for k in eqs:
            try:
                eval(k) #dy(k)/dt
            except (SyntaxError, NameError), details:
                print details
                return 3

        return 0


    def OnToolbar1tools0Tool(self, event):
        """
        Run button event.
        Call BuildModel with r=1, and times how long the model takes to run.
        The time elapsed is shown in a message dialog.
        """
        if not self.ModLoaded:
            if strip(self.eqnEdit.GetValue()) == '':
                return self.OnMenu1items0Menu(event)

#---checking for errors----------------------------------------------------------------------------
        e = self.checkErrors()
        if e == 1:
            dlg = wx.MessageDialog(self, 'Wrong number of initial condition values.',
              'Initial Condition Error', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
            return
        elif e == 2:
            dlg = wx.MessageDialog(self, 'There is a syntax error on the initial conditions box.',
              'Syntax Error', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
            return
        elif e==3:
            dlg = wx.MessageDialog(self, 'There is a syntax error in the Equation Box.\nPlease fix it and try again.',
              'Syntax Error', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
        else:
            pass




        self.modbuilt = 0
        self.sw = wx.StopWatch()
        self.gauge1.SetValue(0)
        self.sw.Start()
        if self.uncertainty == 0:
            self.BuildModel(r=1) #regular run
            self.modRan = 1 #set the flag indicating model has been run
        else:
            if not self.uncertaintyPanel.Donebutton.IsEnabled():
                self.uncertaintyPanel.statusPanel.AppendText('Simulation Started!\n')
                self.BuildModel(r=1) # Melding setup
                self.modRan = 1 #set the flag indicating model has been run
            else:
                dlg = wx.MessageDialog(self, 'Set the parameters for the Uncertainty Analysis\nin its panel and press the "Done" button',
                  'Uncertain Parameters', wx.OK | wx.ICON_INFORMATION)
                try:
                    dlg.ShowModal()
                finally:
                    dlg.Destroy()

        if self.modRan:
            t = gmtime(self.sw.Time()/1000)

            dlg = wx.MessageDialog(self, 'The simulation was completed in '+str(t[3])+' hours, '+str(t[4])+' minutes and '+str(t[5])+' seconds.',
          'Time Elapsed', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
            if self.uncertainty == 1:
                self.uncertaintyPanel.statusPanel.AppendText('The simulation was completed in:\n '+str(t[3])+' hours, '+str(t[4])+' minutes and '+str(t[5])+' seconds.')



    def OnToolbar1tools0ToolRclicked(self, event):
        event.Skip()

    def Equations(self, y, t):
        """
        This function defines the system of differential equations, evaluating
        each line of the equation text box as ydot[i]

        returns ydot
        """
##        pd = (100*t)/(float(strip(str(self.textCtrl3.GetValue())))-float(strip(str(self.textCtrl2.GetValue())))) #calcutates percentage done
##        self.gauge1.SetValue(int(pd))
##        self.gauge1.SetToolTipString(str(pd)+'%')
##        self.gauge1.Refresh() #update the gauge

        Neq=self.Neq
        Npar = self.Npar
        par = self.par


        ydot = zeros((Neq),'d') #initialize ydot
        p = zeros((Npar),'d') #initialize p
    #---Create Parameter Array----------------------------------------------------------------------------
        if self.uncertainty == 0:
            pars = strip(par.GetValue()).split('\n')
            if len(pars) != 0:
                for j in xrange(len(pars)):
                    try:
                        p[j] = eval(pars[j]) #initialize parameter values
                    except SyntaxError:
                        dlg = wx.MessageDialog(self, 'There is a syntax error in the parameter Box.\nPlease fix it and try again.',
                          'Syntax Error', wx.OK | wx.ICON_INFORMATION)
                        try:
                            dlg.ShowModal()
                        finally:
                            dlg.Destroy()
                        
        else:
            for i in range(Npar):
                p[i] = par[i][self.run] # Get a new set of parameters for each repeated run
    #---Create equation array----------------------------------------------------------------------------
        eqs = strip(self.eqnEdit.GetValue()).split('\n')
        for k in range(Neq):
            ydot[k] = eval(eqs[k]) #dy(k)/dt

        return ydot

    def OnToolbar1tools1Tool(self, event):
        """
        Show a figure with the equations typeset
        """
#---translate equations to pseudo-TeX notation----------------------------------------------------------------------------
        texdict = {
        '**':r'^','sqrt':r'\sqrt','[':r'_{',']':r'}',
        'sin':r'\rm{sin}','cos':r'\rm{cos}',
        'alpha':r'\alpha ','beta ':r'\beta ','gamma':r'\gamma '
        } #Can be extended to acomodate new strings
        texdict2 = {'*':r'\times '}# to take care of the multiplication sign *
        xlat = Xlator(texdict)
        xlat2 = Xlator(texdict2)
        if not self.modbuilt:
            self.BuildModel(r=0)
        eq = range(self.Neq) #initialize
        eqs = strip(self.eqnEdit.GetValue()).split('\n')
        for i in xrange(self.Neq):
            eq[i] = xlat2.xlat(xlat.xlat(eqs[i]))
#-------------------------------------------------------------------------------

        eqlist=[]
        for i in range(self.Neq):
            eq[i] = r'$dY_%s/dt = '%i + eq[i] +r'$'
            eqlist.append(eq[i])
#---plot equations----------------------------------------------------------------------------
        DP = PF.create(None)
        DP.SetTitle('Model '+str(self.FileName)[:-4]+': Equations')
        DP.plotEquation(eqlist)
        DP.Show()


    def plotOutput(self, x, y):
        """
        Plots the results of a single run.
        Raises the flag that the plot has been created
        """
        self.PF = PF.create(None)
        self.PF.plot_data(x,y)
        self.PF.Show()


        self.plot = 1

    def plotMelding(self,x,y,tit='Results'):
        """
        This function preprocesses the output of the repeated Runs, calls Bayesian Melding run and sends the data to
        PlotFigure.plotStats to be plotted.
        x contains the time values and y is a list of outputs from odeint, one from each run.
        """
        self.uncertaintyPanel.statusPanel.AppendText('Preparing data for plotting...\n')
        yt = [] # initializes list of transposed runs
        nvar = min(y[0].shape) # Number of Variables
        runlen = max(y[0].shape) #Lenght of runs

        nruns = len(y) # Number of runs

##        SPF = PF.create(None)
##        SPF.plot_data(x,y)
##        SPF.Show()

        self.nruns = nruns
        runs_byvar = [] #List of arrays that will contain all runs for each given variable

        for i in y:
            yt.append(transpose(i)) #Extracts the time series arrays and transpose them (the median function needs to have the series in rows, not in columns).

        for v in range(nvar):
            runs_byvar.append(array([yt[i][v] for i in range(nruns)]))



        # TODO: Turn medianruns into a function
        medianRuns = [median(i) for i in runs_byvar]
        self.uncertaintyPanel.statusPanel.AppendText('Done!\n\n')



        #---95% Limits----------------------------------------------------------
        # TODO: Turn calculation of limits into a function
        self.uncertaintyPanel.statusPanel.AppendText('Calculating credibility intervals...\n')
        sorted=[]
        ll = []
        ul = []
        lc = int(runs_byvar[0].shape[0]*0.025) #column containing the lower boundary for the 95% interval
        hc = int(runs_byvar[0].shape[0]*0.975) #column containing the upper boundary for the 95% interval
        for l in range(nvar):
            sorted.append(msort(runs_byvar[l]))
            ll.append(sorted[l][lc])
            ul.append(sorted[l][hc])

        ts = (medianRuns,ll,ul)
        self.uncertaintyPanel.statusPanel.AppendText('Done!\n\n')

#---testing---------------------------------------------------------------------
##        med = medianRuns[0]-medianRuns[1]
##        SPF = PF.create(None)
##        SPF.plot(x,med)
##        SPF.Show()
#-------------------------------------------------------------------------------


        TP = PF.create(None)
        TP.SetTitle(tit)
        TP.plotStats(x,ts)
        TP.Show()


        self.plot = 1
        return (x,runs_byvar)


    def OnToolbar1tools2Tool(self, event):
        """
        Show Output Table
        """
        if self.modRan:
            self.TableOut = wxFrame2.create(None)
            output = self.modict['results'] # get output from model's dictionary
            x = self.modict['trange']
            y = output[0]
            info = output[1]
            [r,c] = y.shape # get size of t_course array
            self.TableOut.grid1.CreateGrid(r+1,c+6)
            self.TableOut.Show()
            for i in range(r):
                self.TableOut.grid1.SetCellValue(i,0,str(x.flat[i]))
                self.TableOut.grid1.SetColLabelValue(0,'Time')
                for j in range(1,c+1): #fill grid with time series
                    self.TableOut.grid1.SetCellValue(i,j,str(y[i,j-1]))
                    self.TableOut.grid1.SetColLabelValue(j,'y['+str(j)+']')

                if i < r-1: #fill the grid with info series from info
                    self.TableOut.grid1.SetCellValue(i+1,c+1,str(info['hu'][i]))
                    self.TableOut.grid1.SetColLabelValue(c+1,'Step sizes')
                    self.TableOut.grid1.SetCellValue(i+1,c+2,str(info['tcur'][i]))
                    self.TableOut.grid1.SetColLabelValue(c+2,'Time reached')
                    self.TableOut.grid1.SetCellValue(i+1,c+3,str(info['tsw'][i]))
                    self.TableOut.grid1.SetColLabelValue(c+3,'Last method switch')
                    self.TableOut.grid1.SetCellValue(i+1,c+4,str(info['nqu'][i]))
                    self.TableOut.grid1.SetColLabelValue(c+4,'Method order')
                    self.TableOut.grid1.SetCellValue(i+1,c+5,str(int(info['mused'][i])))
                    self.TableOut.grid1.SetColLabelValue(c+5,'Method nused')

            self.TableOut.grid1.AutoSizeColumns()


    def BuildModel(self, r=0):
        """
        Constructs the model from the input fields and runs it if r==1
        """
        self.modict['equations'] = self.eqnEdit.GetValue() #put equations into model's dictionary
        self.modict['parameters'] = self.parEdit.GetValue() # put parameters into model's dictionary
        t_start = float(strip(str(self.textCtrl2.GetValue())))
        self.modict['start'] = strip(str(self.textCtrl2.GetValue())) #store start time
        t_end = float(strip(str(self.textCtrl3.GetValue())))
        self.modict['end'] = strip(str(self.textCtrl3.GetValue())) #store end time
        t_step = float(strip(str(self.textCtrl4.GetValue())))
        self.modict['step'] = strip(str(self.textCtrl4.GetValue())) # Store step size
        init_conds = array([float(i) for i in strip(self.textCtrl1.GetValue()).split(' ') if i != ''])
        self.modict['init'] = strip(self.textCtrl1.GetValue()) # Store initial conditions
        t_range = arange(t_start, t_end+t_step, t_step)
        self.modict['trange'] = t_range
        if self.checkBox1.GetValue():
            fo = 1
        else:
            fo = 0
        if self.checkBox2.GetValue():
            cm = 1
        else:
            cm = 0


        while not self.eqnEdit.GetValue()=='':#get number of ODEs
            val = strip(self.eqnEdit.GetValue()).split('\n')
            Neq = len(val)
            break


        self.Neq = Neq#to be used by Equations
        if r==1:
            #-----------------------------------------------------
            if self.uncertainty == 0:#regular (single) run
                if not self.parEdit.GetValue() == '':#get Number of  Parameters
                    valp = strip(self.parEdit.GetValue()).split('\n')
                    Npar = len(valp)
                else:
                    Npar = 0

                self.Npar = Npar#to be used by Equations
                self.par = self.parEdit #to be used by Equations
                t_course = integrate.odeint(self.Equations,init_conds,t_range, full_output=fo, printmessg=cm)
                self.plotOutput(t_range,t_course)
                self.modict['results'] = t_course
                self.modRan = 1
            else:
#-------------Multiple runs (uncertainty analysis)------------------------------------

                nr= self.uncertaintyPanel.spinCtrl1.GetValue() # Get K from uncertaity panel
                t_courseList = []


                self.parMeld = self.uncertaintyPanel.uncertainPars[1][Neq:] # List of parameter priors. Excluding state variables]
                self.par = self.parMeld #to be used by Equations
                self.Npar = len(self.par)
                for i in range(nr):
                    self.run = i
#---tcourselist for multiple runs does not contain the full output of odeint, just the time series--------------
                    t_courseList.append(integrate.odeint(self.Equations,init_conds,t_range, full_output=0, printmessg=cm))
                    #if self.run%20 == 0:
                     #   self.uncertaintyPanel.statusPanel.AppendText(str(self.run)+'\n')
                    init_conds = array([float(i) for i in strip(self.textCtrl1.GetValue()).split(' ') if i != '']) #reset initial conditions between runs

                self.modRan = 1
                te = gmtime(self.sw.Time()/1000)#time elapses so far (first stage of melding)
                self.uncertaintyPanel.statusPanel.AppendText('First stage of simulation completed in:'+str(te[3])+' hours, '+str(te[4])+' minutes and '+str(te[5])+' seconds.'+'\n')
                (x,runs_byvar) = self.plotMelding(t_range,t_courseList,tit='Median Runs and 95% intervals')
                self.Bmeld(x,runs_byvar) # Perform the rest of the melding calculations
                self.modict['meldruns'] = t_courseList
#-------------------------------------------------------------------------------

        self.modbuilt = 1

    def Bmeld(self,t,ModOut):
        """
        Performs the Melding.
        t is an array of time values.
        Modout is a list of n arrays of time courses where n is the number of variables.
        """
        nvar = len(ModOut)
        dlg = wx.TextEntryDialog(self, 'for which time do you want to run the Melding', 'Choose Time', str(t[-1]))
        try:
            if dlg.ShowModal() == wx.ID_OK:
                answer = dlg.GetValue()
                if answer == '':
                    time = t[-1]
                else:
                    time  = eval(answer)
        finally:
            dlg.Destroy()


        Phis = [ModOut[i][:,int(time)] for i in range(nvar)] # list with all the specified values for each variable
        q2phis = self.uncertaintyPanel.uncertainPars[1][:nvar] # priors (pre-model) for the phis
        q1thetas = tuple(self.uncertaintyPanel.uncertainPars[1][nvar:]) # priors for the thetas (parameters)
        plimits = self.uncertaintyPanel.uncertainPars[0][1][:nvar] #limits of the prior distributions of the phis
        ptype = self.uncertaintyPanel.uncertainPars[0][0][:nvar] #types of the prior distributions
        lik = self.uncertaintyPanel.uncertainPars[3]
        L = int(self.nruns*0.1)
#---Run SIR----------------------------------------------------------------------------
#---meldout=(w, post_theta, qtilphi, q1est)----------------------------------------------------------------------------
        meldout = meld.SIR(0.5,q2phis,plimits,ptype, q1thetas,Phis,L,lik) # output of meld.SIR: (w,qtiltheta,qtilphi,q1est)
#---If SIR fails, don't proceed----------------------------------------------------------------------------
        if meldout == None:
            return


#---Calculate posterior of phis-----------------------------------------------------
        (x,post_phi) = self.postPHI(meldout, L)
#---Plotting results---------------------------------------------------------------------------
        nplots = len(self.uncertaintyPanel.uncertainPars[1])
        allpriors = self.uncertaintyPanel.uncertainPars[1]
        nvp = len(allpriors) # Get number of variable + parameters in the model)
        nlik = len (lik) # Get number of likelihood functions
        vname = ['prior of v[%s]' % i for i in range(nvp)]

        DP = PF.create(None)
        DP.SetTitle('Prior distributions for the parameters')
        DP.plotDist(allpriors,vname)
        DP.Show()

#---Plot posteriors of theta----------------------------------------------------------------------------
        MP = PF.create(None)
        MP.SetTitle('Theta posteriors')
        MP.plotMeldout(meldout)
        MP.Show()
#---Plot posteriors of phi----------------------------------------------------------------------------
# TODO: extract the values of post_phi at time time for each variable to plot.
        self.plotMelding(x,post_phi,tit='Series After Melding Calibration')
        yt = []
        runs_byvar = []
        for i in post_phi:
            yt.append(transpose(i)) #Extracts the time series arrays and transpose them (the median function needs to have the series in rows, not in columns).

        for v in range(nvar):
            runs_byvar.append(array([yt[i][v] for i in range(L)]))
        data = [runs_byvar[i][:,-1] for i in range(nvar)]
        vname2 = ['v[%s]' % i for i in range(nvar)]
        MP = PF.create(None)
        MP.SetTitle('Phi posteriors at time t='+str(time))
        MP.plotDist(data,vname2)
        MP.Show()

    def postPHI(self,meldout,L):
        """
        this function takes the output of the SIR algorithm and calculates the posterior
        distributions of the Phis from the posteriors of the thetas.
        """
        self.post_theta = meldout[1]
        init_conds = array([float(i) for i in strip(self.textCtrl1.GetValue()).split(' ') if i != ''])
        t_start = float(self.modict['start'])
        t_end = float(self.modict['end'])
        t_step = float(self.modict['step'])
        t_range = arange(t_start, t_end+t_step, t_step)
        t_courseList = []
        for i in range(L):
            self.run = i
            t_courseList.append(integrate.odeint(self.Equations2,init_conds,t_range, full_output=0, printmessg=0))
            #self.uncertaintyPanel.statusPanel.AppendText(str(self.run)+'\n')
            init_conds = array([float(i) for i in strip(self.textCtrl1.GetValue()).split(' ') if i != '']) #reset initial conditions between runs

        return (t_range,t_courseList)
    def Equations2(self,y,t):
        """
        Variation of the Equations function to calculate the posterior of phi
        """
        Neq = self.Neq
        pars = self.post_theta
        Npar = len(pars) #get number of parameters

        ydot = zeros((Neq),'d') #initialize ydot
        p = zeros((Npar),'d') #initialize p
    #---Create Parameter Array----------------------------------------------------------------------------
        for i in range(Npar):
            p[i] = pars[i][self.run] # Get a new set of parameters for each repeated run
    #---Create equation array----------------------------------------------------------------------------
        eqs = strip(self.eqnEdit.GetValue()).split('\n')
        for k in xrange(Neq):
            try:
                ydot[k] = eval(eqs[k]) #dy(k)/dt
            except SyntaxError:
                dlg = wx.MessageDialog(self, 'There is a syntax error in the Equation Box.\nPlease fix it and try again.',
                  'Syntax Error', wx.OK | wx.ICON_INFORMATION)
                try:
                    dlg.ShowModal()
                finally:
                    dlg.Destroy()


        return ydot





    def OnMenu3items0Menu(self, event):
        """
        Opens the about window
        """
        dlg = about.wxDialog1(self)
        try:
            dlg.ShowModal()
        finally:
            dlg.Destroy()

    def initUncertainty(self):
        """
        Initializes the values on the uncertainty Analysis Panel based on
        model specification
        """

        while not self.eqnEdit.GetValue()=='':#get number of ODEs
            val = strip(self.eqnEdit.GetValue()).split('\n')
            Neq = len(val)
            break

        if not self.parEdit.GetValue() == '':#get number of parameters
            valp = strip(self.parEdit.GetValue()).split('\n')
            Npar = len(valp)
        else:
            Npar = 0

        items = ["Y[%s]" % str(i) for i in range(Neq)]

        if Npar > 0:
            items += ['P[%s]' % str(i) for i in range(Npar)]

        self.uncertaintyPanel.createVarList(items) # re-create varList on uncertaintyMiniFrame
        self.uncertaintyPanel.fileName = self.FileName #create local variable on Uncertainty panel with filename
        fname = os.path.split(self.FileName)[1]
        fname = fname[:-4]+'_unc.spec'
        if fname in os.listdir('.'):
            self.uncertaintyPanel.loadSpecs(fname)

    def OnWxFrame1Close(self, event):
        """
        Things to do before Exiting.
        """
        # Tries to close other windows if they exist
        try:
            DP.Close()
        except (NameError, AttributeError):
            pass
        try:
            self.PF.Close()
        except (NameError, AttributeError):
            pass
        try:
            MP.Close()
        except (NameError, AttributeError):
            pass
        try:
            self.TableOut.Close()
        except (AttributeError, NameError):
            pass
        try:
            self.uncertaintyPanel.Close()
        except (AttributeError, NameError):
            pass
