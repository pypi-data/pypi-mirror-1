#Boa:Dialog:wxDialog1

import wx
import wx.html
import webbrowser

def create(parent):
    return wxDialog1(parent)

[wxID_WXDIALOG1, wxID_WXDIALOG1CLOSE, wxID_WXDIALOG1HTMLWINDOW1, 
 wxID_WXDIALOG1TUTORIAL, 
] = [wx.NewId() for _init_ctrls in range(4)]

class wxDialog1(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_WXDIALOG1, name='', parent=prnt,
              pos=wx.Point(554, 80), size=wx.Size(357, 508),
              style=wx.DEFAULT_DIALOG_STYLE, title='About')
        self.SetClientSize(wx.Size(357, 508))

        self.htmlWindow1 = wx.html.HtmlWindow(id=wxID_WXDIALOG1HTMLWINDOW1,
              name='htmlWindow1', parent=self, pos=wx.Point(8, 8),
              size=wx.Size(344, 464),
              style=wx.html.HW_SCROLLBAR_AUTO | wx.html.HW_DEFAULT_STYLE)
        self.htmlWindow1.SetThemeEnabled(True)
        self.htmlWindow1.SetToolTipString('About ModelBuilder')
        self.htmlWindow1.SetBackgroundColour(wx.Colour(255, 0, 0))

        self.close = wx.Button(id=wxID_WXDIALOG1CLOSE, label='Close',
              name='close', parent=self, pos=wx.Point(272, 482),
              size=wx.Size(80, 22), style=0)
        self.close.Bind(wx.EVT_BUTTON, self.OnCloseButton,
              id=wxID_WXDIALOG1CLOSE)

        self.tutorial = wx.Button(id=wxID_WXDIALOG1TUTORIAL, label='Tutorial',
              name='tutorial', parent=self, pos=wx.Point(8, 480),
              size=wx.Size(80, 22), style=0)
        self.tutorial.Bind(wx.EVT_BUTTON, self.OnTutorialButton,
              id=wxID_WXDIALOG1TUTORIAL)

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.htmlWindow1.LoadPage('ModelBuilder_About.html')

    def OnCloseButton(self, event):
        self.Close()

    def OnTutorialButton(self, event):
        webbrowser.open_new('http://www.procc.fiocruz.br/~cursos/course/view.php?id=6')
