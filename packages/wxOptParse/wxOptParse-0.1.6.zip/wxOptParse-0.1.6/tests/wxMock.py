from types import ModuleType
from mock import Mock

class Dummy(ModuleType):
  def __getattr__(self,name):
      if name.startswith('__'):
          raise AttributeError, name
      if name.endswith('VERSION') or name.startswith('VERSION'):
          import wx.__version__
          return getattr(sys.modules['wx.__version__'],name)
      return lambda *__args,**__kw: None

  def _wxPySetDictionary(self,d):
      d['Platform'] = '__WXMSW__'
      d['PlatformInfo'] = ['__WXMSW__']
      d['__wxPyPtrTypeMap'] = {}

_core_ = Dummy("dummy")
_core_.cvar = Dummy("dummy")
_gdi_ = Dummy("dummy")
_gdi_.cvar = Dummy("dummy")
_windows_ = Dummy("dummy")
_windows_.cvar = Dummy("dummy")
_controls_ = Dummy("dummy")
_controls_.cvar = Dummy("dummy")

import sys
sys.modules['wx._core_'] = _core_
sys.modules['wx._gdi_'] = _gdi_
sys.modules['wx._windows_'] = _windows_
sys.modules['wx._controls_'] = _controls_
sys.modules['wx._misc_'] = _controls_
sys.modules['wx._html'] = _controls_
sys.modules['wx._grid'] = _controls_

PlatformInfo=[]
import wx
import wx.html
import wx.grid
import wx.lib.intctrl

def makeAssociation(strClass, strModule = 'wx'):
    if 'wxMock' in sys.modules:
        setattr(sys.modules[strModule], strClass, getattr(sys.modules['wxMock'], 'My' + strClass))
    else:
        setattr(sys.modules[strModule], strClass, getattr(sys.modules['__main__'], 'My' + strClass))

class wxMock(Mock):
    def __init__(self, *args, **kwargs):
        Mock.__init__(self)

#################################################
class MyFrame(wxMock):
    pass
makeAssociation('Frame')

class MyIcon(wxMock):
    pass
makeAssociation('Icon')

class MyMenuBar(wxMock):
    pass
makeAssociation('MenuBar')

class MyMenu(wxMock):
    pass
makeAssociation('Menu')

class MyAcceleratorTable(wxMock):
    pass
makeAssociation('AcceleratorTable')

class MyStaticText(wxMock):
    def __init__(self, *args, **kwargs):
        self.value = ''
        Mock.__init__(self)
    def SetValue(self, value):
        self.value = value
    def GetValue(self):
        return self.value
makeAssociation('StaticText')

class MyCheckBox(wxMock):
    def __init__(self, *args, **kwargs):
        self.value = None
        Mock.__init__(self)
    def SetValue(self, value):
        self.value = value
    def GetValue(self):
        return self.value
    def IsChecked(self):
        if self.value == 'True':
            return True
        elif self.value == 'False':
            return False
            
        return self.value

makeAssociation('CheckBox')

class MyComboBox(wxMock):
    def __init__(self, *args, **kwargs):
        self.value = None
        Mock.__init__(self)
    def SetValue(self, value):
        self.value = value
    def GetValue(self):
        return self.value
makeAssociation('ComboBox')

class MyTextCtrl(Mock):
    def __init__(self, *args, **kwargs):
        self.value = None
        Mock.__init__(self)
    def SetValue(self, str):
        self.value = str
    def GetValue(self):
        return self.value
        
makeAssociation('TextCtrl')
    
class MyNotebook(wxMock):
    pass
makeAssociation('Notebook')

class MyBoxSizer(wxMock):
    pass
makeAssociation('BoxSizer')

class MyRadioButton(wxMock):
    pass
makeAssociation('RadioButton')

class MyPanel(wxMock):
    pass
makeAssociation('Panel')

class MyButton(wxMock):
    pass
makeAssociation('Button')

class MyHtmlEasyPrinting(wxMock):
    pass
makeAssociation('HtmlEasyPrinting', 'wx.html')
    
class MyHtmlWindow(wxMock):
    pass
makeAssociation('HtmlWindow', 'wx.html')

class MyScrolledWindow(wxMock):
    def GetSize(self):
        return (10,10)

makeAssociation('ScrolledWindow')

class MyPySimpleApp(wxMock):
    pass
makeAssociation('PySimpleApp', 'wx')

class MyFont(wxMock):
    pass
makeAssociation('Font')

class MyGrid(Mock):
    def __init__(self, *args, **kwargs):
        self.data = [[]]
        self.nCols = 0
        self.nCurRow = 0
        Mock.__init__(self)
        
    def CreateGrid(self, numRows, numCols):
        self.data = []
        self.nCols = numCols
        for nRow in range(numRows):
            self.AppendRows(1)
        
    def SetCellValue(self, row, col, s):
        self.data[row][col] = s
        
    def GetNumberRows(self):
        return len(self.data)

    def DeleteRows(self, pos = 0, numRows = 1, updateLabels = True):
        print "Todo"
        
    def AppendRows(self, numRows = 1, updateLabels = True):
        for nRow in range(numRows):
            self.data.append([ [] for nCol in range(self.nCols)])
        
        return True
        
    def GetGridCursorRow(self):
        return self.nCurRow
        
    def MoveCursorDown(self, expandSelection):
        self.nCurRow += 1
        if self.nCurRow >= self.GetNumberRows():
            self.nCurRow -= 1

makeAssociation('Grid', 'wx.grid')

class MyIntCtrl(wxMock):
    def __init__(self, *args, **kwargs):
        self.value = None
        Mock.__init__(self)
    def SetValue(self, value):
        self.value = value
    def GetValue(self):
        return self.value
makeAssociation('IntCtrl', 'wx.lib.intctrl')

wx.WXK_NUMPAD0 = 326
wx.WXK_NUMPAD9 = 335
wx.BOTTOM = 1
wx.LEFT = 1
wx.RIGHT = 1
wx.TOP = 1
wx.ALIGN_BOTTOM = 1
wx.CB_READONLY=1
wx.CB_DROPDOWN=1
wx.SWISS=1
wx.NORMAL=1
wx.EXPAND=1
wx.ALL=1
