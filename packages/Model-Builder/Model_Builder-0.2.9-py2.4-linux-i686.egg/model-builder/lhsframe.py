#Boa:Frame:LHS

import wx

def create(parent):
    return LHS(parent)

[wxID_LHS] = [wx.NewId() for _init_ctrls in range(1)]

class LHS(wx.Frame):
    def _init_sizers(self):
        # generated method, don't edit
        self.boxSizer1 = wx.BoxSizer(orient=wx.VERTICAL)

        self.flexGridSizer1 = wx.FlexGridSizer(cols=3, hgap=1, rows=2, vgap=1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_LHS, name='LHS', parent=prnt,
              pos=wx.Point(518, 331), size=wx.Size(849, 561),
              style=wx.DEFAULT_FRAME_STYLE,
              title='Sensitivity and Uncertainty Analysis')
        self.SetClientSize(wx.Size(849, 561))

        self._init_sizers()

    def __init__(self, parent):
        self._init_ctrls(parent)
