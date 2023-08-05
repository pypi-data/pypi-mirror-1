# -*- coding:iso8859-1 -*-
#-----------------------------------------------------------------------------
# Name:        PlotFigure.py
# Purpose:     Plotting frame that contains the plots generated by Model Buider
#
# Author:      Flavio C. Coelho
#
# Created:     2004/09/01
# RCS-ID:      $Id: PlotFigure.py,v 1.1 2004/01/13 10:51:43 fccoelho Exp $
# Copyright:   (c) 2003
# Licence:     GPL
# Obs:   This code was based on Jeremy Donoghue's embedding_in_wx.py included with
#       matplotlib.
#-----------------------------------------------------------------------------
#Boa:Frame:PlotFigure

import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wx import NavigationToolbar2Wx, FigureManager
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas


from matplotlib.figure import Figure
from matplotlib.axes import Subplot
import matplotlib.numerix as numpy
#from RandomArray import *
#from numpy.random.old import *
from numpy.random import *


import wx

def create(parent):
    return PlotFigure(parent)

[wxID_PLOTFIGURE] = [wx.NewId() for _init_ctrls in range(1)]

class PlotFigure(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_PLOTFIGURE, name='Output', parent=prnt,
              pos=wx.Point(311, 209), size=wx.Size(1280, 893),
              style=wx.DEFAULT_FRAME_STYLE, title='Results')
        self.SetClientSize(wx.Size(1280, 893))

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.fig = Figure((10,8), 75)
        self.canvas = FigureCanvas(self,-1, self.fig)
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()



                # On Windows, default frame size behaviour is incorrect
        # you don't need this under Linux
        tw, th = self.toolbar.GetSizeTuple()
        fw, fh = self.canvas.GetSizeTuple()
        self.toolbar.SetSize(wx.Size(fw, th))



        # Create a figure manager to manage things
        self.figmgr = FigureManager(self.canvas, 1, self)



        # Now put all into a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
                # This way of adding to sizer prevents resizing
        #sizer.Add(self.fig, 0, wxLEFT|wxTOP)



                # This way of adding to sizer allows resizing
        sizer.Add(self.canvas, 1, wx.LEFT|wx.TOP|wx.GROW)



                # Best to allow the toolbar to resize!
        sizer.Add(self.toolbar, 0, wx.GROW)
        self.SetSizer(sizer)
        self.Fit()


    def plot(self,x,y,leg=[]):
        """
        This function will plot one or more lines.
        y is a list of sequances or a single vector.
        x is a vector.
        """
        # Use this line if using a toolbar
        a = self.fig.add_subplot(111)



        # Or this one if there is no toolbar
        #a = Subplot(self.fig, 111)
        if str(type(y)) == "<type 'list'>":
            nlin = len(y)

            for i in range(nlin):
                a.plot (x,y[i])
        else:
            a.plot(x,y)


        a.set_xlabel('Time', fontsize=9)

#---generating tuple of legends-------------------------------------------------
        if str(type(y)) == "<type 'list'>":
            if leg ==[]:
                b = range(nlin)
                leg = tuple(['$y_{'+str(i)+'}$' for i in b])
        else:
            pass
#-------------------------------------------------------------------------------
        a.legend(leg)

        self.toolbar.update()

    def vectorField(self,x,y,u,v,c=0.2,xlabel='',ylabel='',trajectory=[]):
        """
        Plot a vector field for State space visualizations
        """
        # Use this line if using a toolbar
        a = self.fig.add_subplot(111)
        # Or this one if there is no toolbar
        #a = Subplot(self.fig, 111)
        a.quiver2(x,y,u,v,c)
        a.set_xlabel(xlabel)
        a.set_ylabel(ylabel)
        a.set_title('State Space Diagram')
        if trajectory:
            a.plot(trajectory[0],trajectory[1],'r-')
    
    def plot_data(self, x,y):
        """
        This function will plot the time series as output by odeint.
        """
        # Use this line if using a toolbar
        a = self.fig.add_subplot(111)



        # Or this one if there is no toolbar
        #a = Subplot(self.fig, 111)

        nvar = min(y[0].shape)

        for i in range(nvar):
            a.plot (x,y[0][:,i])




        a.set_xlabel('Time', fontsize=9)
        a.set_ylabel('$Y_{i}$', fontsize=9)
        a.set_title('Time series')
#---generating tuple of legends-------------------------------------------------
        b = range(nvar)
        leg = tuple(['$y_{'+str(i)+'}$' for i in b])
#-------------------------------------------------------------------------------
        a.legend(leg)

        self.toolbar.update()


    def plotStats(self,x, ts):
        """
        This function will plot multiple time series
        ts is a list of lists: [list of median time-series, list of lower credible intervals, list of upper credible intervals]
        """
        # Use this line if using a toolbar
        #a = self.figmgr.add_subplot(111)
        # Or this one if there is no toolbar
        #a = Subplot(self.fig, 111)
        nvar = len(ts[0])
        print len(x), len(ts[0])
        c=['r','g','b','c','m','y','k']
        for i in range(nvar):
            a = self.fig.add_subplot(nvar*100+10+i+1)
            a.plot(x,ts[0][i], '%s-o'%c[i%len(c)],x,ts[1][i],'%s-.'%c[i%len(c)], x,ts[2][i],'%s-.'%c[i%len(c)])
            a.set_xlabel('Time', fontsize=9)
            a.set_ylabel('$y_{'+str(i)+'}$', fontsize=9)
            a.legend(('median'))

#---generating tuple of legends-------------------------------------------------
        b = range(nvar)
        leg = tuple(['$y_{'+str(i)+'}$' for i in b])
#-------------------------------------------------------------------------------


        self.toolbar.update()


    def plotDist(self,data,vname):
        """
        Plots histograms of each line of 'data'
        the name of the variables are the elements of the list 'vname'
        """
        nvar = len(data)
        for i in range(nvar):
            # Use this line if using a toolbar
            a = self.figmgr.add_subplot(nvar*100+10+i+1)
            nb, bins, patches = a.hist(data[i],bins=50, normed=1)
            a.set_ylabel(vname[i], fontsize=9)



        self.toolbar.update()



    def plotMeldout(self,meldout):
        """
        Plots histograms of the posterior distributions of the model components
        meldOut is the output of the Melding.SIR function: (w,qtiltheta,qtilphi,q1est)
        """
        nvar = len(meldout[1])
        data = meldout[1]
        for i in range(nvar):
            # Use this line if using a toolbar
            a = self.figmgr.add_subplot(nvar*100+10+i+1)

            # Or this one if there is no toolbar
            #a = Subplot(self.fig, 111)

            nb, bins, patches = a.hist(data[i],bins=50, normed=1)
            a.set_title('Posterior Distribution of '+'$p_{%s}$'%i, fontsize=9)

        self.toolbar.update()

    def plotEquation(self, eqlist):
        """
        Plot list of equations typeset with mathtext on an equation box
        """

        a = self.fig.add_subplot(111)

        a.plot([0,10],'w.')
        a.set_xlim((0,10))
        a.set_ylim((0,10))

        a.set_title('Model Equations')
        a.set_xticklabels([])
        a.set_yticklabels([])
        a.set_xticks([])
        a.set_yticks([])

        for i in range(len(eqlist)):
            print eqlist[i]
            a.text(1,9-i,eqlist[i], fontsize=15)


        self.toolbar.update()

    def GetToolBar(self):
        # You will need to override GetToolBar if you are using an
        # unmanaged toolbar in your frame
        return self.toolbar

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = create(None)
    x = normal(0,1,50)
    y = normal(0,1,(50,5))
    frame.plot_data(x,[y])
    frame.Show()
    app.MainLoop()
