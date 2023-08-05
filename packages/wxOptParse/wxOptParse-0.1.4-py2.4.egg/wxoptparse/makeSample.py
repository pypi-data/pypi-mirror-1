#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

from subprocess import Popen, PIPE
import re

class MakeSample:
    def __init__(self):
        self.params = []
    
    def getHelpText(self, strCommand):
        self.strCommand = strCommand
        output = Popen([strCommand, "--help"], stdout=PIPE).communicate()[0]
        return output


    def doMatches(self, line):
        re_four  = re.compile(r"\s+\-(.),\s+\-\-([^ ]+),\s+\-\-([^ ]+)\s+(.*)")
        re_three = re.compile(r"\s+\-(.),\s+\-\-([^ ]+)\s+(.*)")
        re_two   = re.compile(r"\s+\-\-([^ ]+)\s+(.*)")
        
        match = re_four.match(line)
        if match:
            self.params.append({
                'short' : match.group(1), 
                'long'  : [match.group(2), match.group(3)], 
                'desc'  : match.group(4)})
            return
            
        match = re_three.match(line)
        if match:
            short = match.group(1)
            if short == 'h' and match.group(2) == 'help':
                return
            
            if short == 'h':
                # Kill off the -h option
                self.params.append({
                    'long'  : [match.group(2),], 
                    'desc'  : match.group(3)})
            else:
                self.params.append({
                    'short' : short, 
                    'long'  : [match.group(2),], 
                    'desc'  : match.group(3)})
            return
            
        match = re_two.match(line)
        if match:
            if match.group(1) == 'help':
                return
            
            self.params.append({
                'long' : [match.group(1),], 
                'desc' : match.group(2)})
                    
            return
        
        if len(self.params) > 0:
            self.params[-1]['desc'] += " " + line.strip()

    def parseText(self, helpText):
        for line in helpText.split("\n"):
            line = line.rstrip()
            self.doMatches(line)
        
    def makeCode(self):
        re_metavar = re.compile("(.+)=(.+)")
        lines = []
        lines.append("#! /usr/bin/env python")
        lines.append("# -*- coding: iso-8859-1 -*-")
        lines.append("")
        lines.append("import optparse, sys, subprocess")
        lines.append("")
        lines.append("parser = optparse.OptionParser()")
        for param in self.params:
            paramList = []
            strVarName = ''
            if 'short' in param:
                paramList.append("'-%s'" % (param['short']))
                strVarName = param['short']
                
            if 'long' in param:
                strLongs = param['long']
                strVarName = strLongs[0]
                strMetavar = None
                for strLong in strLongs:
                    match = re_metavar.match(strLong)
                    if match:
                        paramList.append("'--%s'" % (match.group(1)))
                        strVarName = match.group(1)
                        strMetavar = match.group(2)
                        paramList.append("metavar='%s'" % (strMetavar))
                    else:
                        paramList.append("'--%s'" % (strLong))
                    
            if len(strVarName) > 0:
                strVarName = makeNiceVarName(strVarName)
                paramList.append("dest='%s'" % (strVarName))
            
            if not strMetavar:
                paramList.append('action="store_true"')
            
            if 'desc' in param:
                paramList.append("\n     help='%s'" % (param['desc'].replace("'", "\\'")))
            
            lines.append("parser.add_option(%s)" % (", ".join(paramList), ))
            
        lines.append("(options, args) = parser.parse_args()")
        lines.append("sys.argv[0] = '%s'" % (self.strCommand))
        #lines.append("print sys.argv")
        lines.append("try:")
        lines.append('    retcode = subprocess.call("%s" % (" ".join(sys.argv)), shell=True)')
        lines.append("    if retcode < 0:")
        lines.append('        print >>sys.stderr, "Child was terminated by signal", -retcode')
        lines.append("    else:")
        lines.append('        print >>sys.stderr, "Child returned", retcode')
        lines.append("except OSError, e:")
        lines.append('    print >>sys.stderr, "Execution failed:", e')
        
        return lines
        
    def createCode(self, strCommand):
        helpText = self.getHelpText(strCommand)
        self.parseText(helpText)
        lines = self.makeCode()
        print "\n".join(lines)
    
def makeNiceVarName(strVarName):
    strVarName = re.sub('^--', '', strVarName)
    strVarName = re.sub('^-', '', strVarName)
    strVarName = re.sub('-', '_', strVarName)
    return strVarName
    
if __name__ == "__main__":
    ms = MakeSample()
    strProg = "wget"
    strProg = "grep"
    #strProg = "find"
    strProg = "tar"
    ms.createCode(strProg)