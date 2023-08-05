#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

import optparse
from optparse import OptionParser
from elementtree import ElementTree
import wxversion
wxversion.select("2.5.3")

import wx, wx.lib.intctrl
import textwrap
import os,sys,re

class SecondWindow(wx.Frame):
    """ Not used at the moment.
    The idea is to have a graphical window where the output is send """
    
    def __init__(self):
        self.orig = sys.stdout
        title = "wxOptParser"
        wx.Frame.__init__(self, 
            None, 
            wx.ID_ANY, 
            title, 
            size = (900,600),
            style = wx.DEFAULT_FRAME_STYLE)
        self.panel = wx.Panel(self, -1)
        
        aVBox = wx.BoxSizer(wx.VERTICAL)
        aVBox.Add(wx.StaticText(self.panel, -1, "Output:"), 0, flag=wx.LEFT | wx.TOP, border = 5)
        self.ctrlTextOutput = wx.TextCtrl(self.panel, -1, '', size=(600, 50))
        aVBox.Add(self.ctrlTextOutput, 0, flag=wx.ALL, border = 5)
        self.panel.SetSizer(aVBox)
        self.panel.Fit()
        self.Fit()
        
    def write(self, info):
        self.orig.write(info)
        
        
class wxOptParser(optparse.OptionParser):
    def _retAppFrame(self, args=None, values=None):
        """ This is required for testing """
        
        rargs = self._get_args(args)
        if values is None:
            values = self.get_default_values()

        self.rargs = rargs
        self.largs = largs = []
        self.values = values

        try:
            stop = self._process_args(largs, rargs, values)
        except (BadOptionError, OptionValueError), err:
            self.error(err.msg)

        args = largs + rargs
        (self.options, self.args) = self.check_values(values, args)

        app = wx.PySimpleApp()
        frame = MainWindow(self, self.option_list)
        app.MainLoop()
        
        return app, frame
        
    def parse_args(self, args=None, values=None):
        app, frame = self._retAppFrame(args, values)
        if hasattr(self, '_wxOptParseCallback'):
            # This gives you a chance to change/test some stuff when the dialog is up
            self._wxOptParseCallback(self, app, frame)
        
        return (self.options, self.args)
        

class MainWindow(wx.Frame):
    """ We simply derive a new class of Frame. """
    
    def __init__(self, parent, options):
        self.et = None
        self.parent = parent # wxOptParser
        self.progname = sys.argv[0]
        self.bPipe = True
        
        self.options = options
        self.ctrlOptions = []
        id = -1
        
        title = "wxOptParser"
        
        wx.Frame.__init__(self, 
            None,
            wx.ID_ANY,
            title,
            size = (900,600),
            style = wx.DEFAULT_FRAME_STYLE)
            
        #~ self.panel = wx.Panel(self, -1)
        self.panel = wx.ScrolledWindow(self, -1, (0, 0))
        
        self.loadSavedInfo()

        aVBox = wx.BoxSizer(wx.VERTICAL)
        
        text = wx.StaticText(self.panel, -1, self.progname, style = wx.ALIGN_CENTRE)
        font = wx.Font(18, family = wx.SWISS, style = wx.NORMAL, weight = wx.NORMAL)
        text.SetFont(font)
        text.SetSize(text.GetBestSize())
        aVBox.Add(text, flag=wx.ALL, border = 5)

        for myOption in IterOptions(self):
            strHelp = myOption.getHelp()
                
            if myOption.toSkip():
                pass # skip these
            elif myOption.isChoice():
                choices = [''] + list(myOption.getChoices())
                cbox = wx.ComboBox(self.panel, -1, choices = choices, style = wx.CB_READONLY | wx.CB_DROPDOWN)
                self._addCtrl(aVBox, cbox, myOption, wx.EVT_COMBOBOX, self.OnComboChanged, strHelp)
            elif myOption.isBoolean():
                listHelp = textwrap.wrap(strHelp)
                checkb = wx.CheckBox(self.panel, -1, listHelp[0], size=(600, 20))
                self._addCtrl(aVBox, checkb, myOption, wx.EVT_CHECKBOX, self.OnCheckClicked)
                if len(listHelp) > 1:
                    aVBox.Add(wx.StaticText(self.panel, -1, '\n'.join(listHelp[1:])), flag = wx.LEFT, border = 20)
            elif myOption.getType() == 'int':
                min = wx.lib.intctrl.IntCtrl(self.panel, size=( 50, -1 ) )
                min.SetNoneAllowed(True)
                min.SetValue(None)
                self._addCtrl(aVBox, min, myOption, wx.lib.intctrl.EVT_INT, self.OnIntChanged, strHelp)
            elif myOption.getType() == 'float':
                textctrl = wx.TextCtrl(self.panel, -1, size=(50, -1))
                self._addCtrl(aVBox, textctrl, myOption, wx.EVT_TEXT, self.OnTextChange, strHelp)
            elif self._guessFile(myOption):
                self._addFileBox(aVBox, myOption)
            elif self._guessPath(myOption):
                self._addPathBox(aVBox, myOption)
            else:
                textctrl = wx.TextCtrl(self.panel, -1, size=(-1, -1))
                self._addCtrl(aVBox, textctrl, myOption, wx.EVT_TEXT, self.OnTextChange, strHelp)

        self.ctrlArgs = wx.TextCtrl(self.panel, -1, '', size=(-1,-1))
        aVBox.Add(wx.StaticText(self.panel, -1, "Additional arguments:"), 0, flag=wx.LEFT | wx.TOP, border = 5)
        aVBox.Add(self.ctrlArgs, 0, flag=wx.ALL | wx.EXPAND, border = 5)
        self.ctrlArgs.Bind(wx.EVT_TEXT, self.OnTextChange)
        
        self.ctrlParams = wx.TextCtrl(self.panel, -1, '', size=(-1,-1))
        aVBox.Add(wx.StaticText(self.panel, -1, "Params:"), 0, flag=wx.LEFT | wx.TOP, border = 5)
        aVBox.Add(self.ctrlParams, 0, flag=wx.ALL | wx.EXPAND, border = 5)
        
        self.ctrlGo = wx.Button(self.panel, -1, "Go")
        aVBox.Add(self.ctrlGo, flag = wx.ALL, border = 5)
        self.ctrlGo.Bind(wx.EVT_BUTTON, self.OnGo)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.buildParams()

        self.panel.SetSizer(aVBox)
        self.panel.Fit()
        
        w, h = self.panel.GetSize()
        maxW = wx.SystemSettings_GetMetric(wx.SYS_SCREEN_X)
        maxH = wx.SystemSettings_GetMetric(wx.SYS_SCREEN_Y)
        self.panel.SetScrollbars(20, 20, w/20, h/20)
        if w <= maxW and h <= maxH:
            self.Fit()        
        self.Show(True)

    def _guessFile(self, option):
        strSearch = option.getHelp()
        if not strSearch:
            return False
        return 'file' in strSearch.lower()
    
    def _guessPath(self, option):
        strSearch = option.getHelp()
        if not strSearch:
            return False
        return 'path' in strSearch.lower() or 'folder' in strSearch.lower()
    
    def _addFileBox(self, aVBox, option):
        ahBox = wx.BoxSizer(wx.HORIZONTAL)
        avBox = wx.BoxSizer(wx.VERTICAL)
        
        textctrl = wx.TextCtrl(self.panel, -1, size=(-1, -1))
        self._addCtrl(avBox, textctrl, option, wx.EVT_TEXT, self.OnTextChange, option.getHelp())
        
        ahBox.Add(avBox)
        button = wx.Button(self.panel, -1, '...', size=(30, -1))
        ahBox.Add(button, 0, flag = wx.BOTTOM | wx.ALIGN_BOTTOM, border = 4)
        button.Bind(wx.EVT_BUTTON, self.OnClickFile)
        
        aVBox.Add(ahBox, 0, flag = wx.LEFT | wx.TOP, border = 0)

    def _addPathBox(self, aVBox, option):
        ahBox = wx.BoxSizer(wx.HORIZONTAL)
        avBox = wx.BoxSizer(wx.VERTICAL)
        
        textctrl = wx.TextCtrl(self.panel, -1, size=(-1, -1))
        self._addCtrl(avBox, textctrl, option, wx.EVT_TEXT, self.OnTextChange, option.getHelp())
        
        ahBox.Add(avBox)
        button = wx.Button(self.panel, -1, '...', size=(30, -1))
        ahBox.Add(button, 0, flag = wx.BOTTOM | wx.ALIGN_BOTTOM, border = 4)
        button.Bind(wx.EVT_BUTTON, self.OnClickFolder)
        
        aVBox.Add(ahBox, 0, flag = wx.LEFT | wx.TOP, border = 0)
        
    def _addCtrl(self, aVBox, ctrl, option, eventId, function, text = None):
        if text:
            aVBox.Add(wx.StaticText(self.panel, -1, textwrap.fill(text), size=(600, -1)), 0, flag=wx.LEFT | wx.TOP, border = 5)
        
        strDefault = option.getDefault()
            
        if strDefault != None:
            if isinstance(ctrl, wx.lib.intctrl.IntCtrl):
                try:
                    ctrl.SetValue(int(strDefault))
                except:
                    ctrl.SetValue(None)
            elif isinstance(ctrl, wx.CheckBox):
                if strDefault == 'True':
                    strDefault = True
                elif strDefault == 'False':
                    strDefault = False
                else:
                    strDefault = None
                if strDefault == None:
                    ctrl.SetValue(False)
                elif option.getAction() == 'store_false':
                    ctrl.SetValue(not strDefault)
                else:
                    ctrl.SetValue(strDefault)
            elif option.isChoice():
                if str(strDefault) in option.getChoices():
                    ctrl.SetValue(str(strDefault))
            else:
                ctrl.SetValue(str(strDefault))
        
        aVBox.Add(ctrl, 0, flag = wx.EXPAND | wx.ALL, border = 5)
        self.ctrlOptions.append((ctrl, option.option))
        ctrl.Bind(eventId, function)

    def OnGo(self, evnt):
        self.params =  self._buildParams()
        values = self.parent.get_default_values()
        self.saveInfo()

        self.parent.rargs = self.params[:]
        self.parent.largs = largs = []
        self.parent.values = values

        try:
            stop = self.parent._process_args(largs, self.parent.rargs, values)
        except (optparse.BadOptionError, optparse.OptionValueError), err:
            print err

        args = largs + self.parent.rargs
        (self.parent.options, self.parent.args) = self.parent.check_values(values, args)

        #print "Args:", self.params
        self.Destroy()
        
    def OnTextChange(self, event):
        self.buildParams()

    def OnClickFile(self, event):
        ctrl = event.GetEventObject()
        dlg = wx.FileDialog(
            self, message="Choose a file", defaultDir=os.getcwd(), 
            defaultFile="", wildcard='*.*', style=wx.OPEN | wx.CHANGE_DIR
            )

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
    
            ctrl = self.prevTextCtrl(event)
            ctrl.SetValue(' '.join(paths))

        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()

    def OnClickFolder(self, event):
        dlg = wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)

        # If the user selects OK, then we process the dialog's data.
        # This is done by getting the path data from the dialog - BEFORE
        # we destroy it. 
        if dlg.ShowModal() == wx.ID_OK:
            ctrl = self.prevTextCtrl(event)
            ctrl.SetValue(dlg.GetPath())
            
        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()

    def prevTextCtrl(self, event):
        ctrl = event.GetEventObject()
        ctrlParent = ctrl.GetParent()
        windows = ctrlParent.GetChildren()
        ctrlPrev = windows[0]
        for win in windows:
            if win == ctrl:
                break
            if isinstance(win, wx.TextCtrl):
                winPrev = win
        return winPrev
        
    def OnCheckClicked(self, event):
        self.buildParams()

    def OnComboChanged(self, event):
        self.buildParams()
        
    def OnIntChanged(self, event):
        self.buildParams()
        
    def buildParams(self):
        strTextList = self._buildParams(useQuotes = True)
        self.ctrlParams.SetValue(' '.join(strTextList))

    def _buildParams(self, useQuotes = False):
        strTextList = []
        for myOption in IterOptions(self):
            
            strValue = myOption.getValue()
            if strValue == 'None':
                strValue = ''
                
            if myOption.isChoice():
                if strValue != None and len(strValue) > 0:
                    strTextList.append(myOption.getOptString())
                    if useQuotes and ' ' in strValue:
                        strValue = '"%s"' % (strValue)
                    
                    strTextList.append(strValue)
            elif myOption.isBoolean():
                if myOption.getBooleanStringValue() == "True":
                    strTextList.append(myOption.getOptString()) # FIX to check, why opt_string()?
            else:
                if myOption.getType() == 'int':
                    strValue = str(strValue)
                elif myOption.getType() == 'float':
                    try:
                        strValue = str(float(strValue))
                    except ValueError:
                        strValue = ''
                    
                if len(strValue) > 0:
                    strTextList.append(myOption.getOptString())
                    if useQuotes and ' ' in strValue:
                        strValue = '"%s"' % (strValue)
                    
                    strTextList.append(strValue)
    
        if self.ctrlArgs.GetValue() != None:
            strTextList += self.ctrlArgs.GetValue().split(' ')
        
        return strTextList

    def loadSavedInfo(self):
        strFilename = self.getXmlFilename()
        if strFilename == None:
            return
        
        if not os.path.isfile(strFilename):
            return 
        
        # Unfortunately we need to assume the file has the real information
        # and that the 
        self.et = ElementTree.parse(strFilename)
        
    def saveInfo(self):
        strFilename = self.getXmlFilename()
        if strFilename == None:
            return
            
        if self.et:
            self.updateElementTree()
            self.et.write(strFilename, encoding="iso-8859-1")
            return
        
        of = file(strFilename, "w")
        of.write('<wxOptParse app="%s">\n' % (self.progname))
        for myOption in IterOptions(self):
            of.write('  <option name="%s"' % (myOption.getName()))
            strValue = myOption.getValue()
            
            if myOption.isChoice() or myOption.isNumber():
                of.write(' lastval="%s">\n' % (strValue,))
            elif myOption.isBoolean():
                of.write(' lastval="%s">\n' % (myOption.getBooleanStringValue(),))
            else:
                of.write(' lastval="%s">\n' % (strValue,))
            
            of.write('  </option>\n')

        of.write('</wxOptParse>\n')
        
        of.close()

    def updateElementTree(self):
        for ctrl, option in self.ctrlOptions:
            strName = option.dest
            if option.action == 'store_true' or option.action == 'store_false':
                if (option.action == 'store_true' and ctrl.IsChecked() == True) or (option.action == 'store_false' and ctrl.IsChecked() == False):
                    strLastVal = 'True'
                elif ctrl.GetValue() != None:
                    strLastVal = 'False'
                else:
                    strLastVal = 'None'
            else:
                strLastVal = str(ctrl.GetValue())
            
            self.updateElement(strName, strLastVal)
    
    def updateElement(self, strName, strLastVal):
        for item in self.et.findall('//option'):
            if item.attrib['name'] == strName:
                #print "%s = '%s'" % (strName, strLastVal)
                if strLastVal == optparse.NO_DEFAULT:
                    strLastVal = None
                previous = item.attrib['lastval'][:]
                item.attrib['lastval'] = str(strLastVal)
                self.AppendRecent(item, strLastVal, previous)
                break

    def AppendRecent(self, node, curVal, lastVal):
        if str(curVal) == str(lastVal):
            return
        
        node.text = '\n    '
        
        for event in node.findall('recent'):
            if event.attrib['value'] == curVal:
                node.remove(event)
                break
        
        newNode = ElementTree.Element('recent')
        newNode.attrib['value'] = lastVal
        newNode.tail = '\n    '
        node.insert(0, newNode)

    def getXmlFilename(self):
        strFilename = self.progname
        strFilename = re.sub(r'\..{1,4}$', '.args', strFilename)
        if strFilename == self.progname:
            # Don't overwrite the program
            return None
        return strFilename

    def OnClose(self, event):
        self.Destroy()
        sys.exit(-1)


class IterOptions:
    def __init__(self, parent):
        self.parent = parent
        
        if len(self.parent.ctrlOptions) > 0:
            self.list = self.parent.ctrlOptions
        else:
            self.list = self.parent.options
        
        self.nIndex = 0
        
    def __iter__(self):
        return self
        
    def next(self):
        if len(self.list) > self.nIndex:
            self.nIndex += 1
            return MyOption(self.list[self.nIndex - 1], self.parent.et)
        raise StopIteration

class MyOption:
    """ Create a class so that all the times we have to iterate over the options we have a 
    consistent set of rules about what type of object we are looking at, for example """
    
    def __init__(self, listItem, et):
        self.et = et
        if isinstance(listItem, tuple):
            self.ctrl, self.option = listItem
        else:
            self.ctrl = None
            self.option = listItem
        
    def getCtrl(self):
        return self.ctrl
    
    def getType(self):
        return self.option.type
    
    def getValue(self):
        strValue = self.ctrl.GetValue()
        if strValue == None  or str(strValue) == str(optparse.NO_DEFAULT):
            strValue = 'None'
            
        return strValue
        
    def getName(self):
        return self.option.dest
        
    def isChoice(self):
        return self.option.choices != None

    def getChoices(self):
        return self.option.choices
        
    def isNumber(self):
        return self.option.type == 'int' or self.option.type == 'float'
    
    def isBoolean(self):
        return self.option.action == 'store_true' or self.option.action == 'store_false'

    def getBooleanStringValue(self):
        if (self.option.action == "store_true" and self.getValue() == True) or (self.option.action == "store_false" and self.getValue() == False):
            return "True"
        elif self.getValue() != 'None':
            return "False"
        return "None"

    def getOptString(self):
        return self.option.get_opt_string()

    def getAction(self):
        return self.option.action
        
    def getHelp(self):
        strHelp = self.option.help
        
        if not strHelp and self.option._long_opts:
            strHelp = self.option._long_opts[0]
        if not strHelp and self.option._short_opts:
            strHelp = self.option._short_opts[0]

        return strHelp
        
    def toSkip(self):
        return self.option.action == 'help' or self.option.action == 'version'

    def getDefault(self):
        strDefault = self.option.default
        
        if self.findLastVal(self.option.dest) != None:
            strDefault = self.findLastVal(self.option.dest)
        
        if str(strDefault) == str(optparse.NO_DEFAULT):
            strDefault = None
            
        return strDefault

    def findLastVal(self, strName):
        return self.findItemAttrib(strName, 'lastval')
        
    def findItemAttrib(self, strName, strAttrib):
        item = self.findItem(strName)
        if item and strAttrib in item.attrib:
            return item.attrib[strAttrib]
        
        return None

    def findItem(self, strName):
        if self.et == None:
            return None
            
        for item in self.et.findall('//option'):
            if item.attrib['name'] == strName:
                return item

        return None

    def __str__(self):
        return "%s:%s" % (self.getName(), self.getDefault())

optparse.OptionParser = wxOptParser
OptionParser = wxOptParser

def handleCommandLine():
    import sys
    
    if len(sys.argv) > 1 and len(sys.argv[1]) > 0:
        strFilename = sys.argv[1]
    else:
        print "usage: wxoptparse.py <programtorun>"
        #~ strFilename = "tests/mytest.py"
        #~ strFilename = "tests/noDefaultsTest.py"
        #strFilename = "tests/grepTest.py"
        sys.exit(-1)
        
    strDir = os.path.dirname(strFilename)
    if len(strDir) > 0:
        try:
            os.chdir(strDir)
        except Exception, e:
            print "Unable to change to folder '%s'" % (strDir)
    
    globals()['__name__'] = '__main__'
    
    sys.argv[0] = os.path.basename(strFilename) # Let's cheat
    if sys.argv[0] == strFilename and len(strDir) > 0:
        sys.argv[0] = sys.argv[0][len(strDir):]

    strModuleName = sys.argv[0][:-3]
    __import__(strModuleName)
    execfile(sys.argv[0])

if __name__ == "__main__":
    handleCommandLine()