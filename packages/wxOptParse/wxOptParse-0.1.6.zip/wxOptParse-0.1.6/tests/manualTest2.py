import optparse


class MyClass:
    def __init__(self, strMessage):
        self.strMess = strMessage
    
    def printMess(self):
        print self.strMess

def parseParams():
    global MyClass
    parser = optparse.OptionParser(usage="usage: %prog [options] filename")
    parser.add_option("-m", "--mess", action="store", type="string", dest="strMess", default="Bob", 
        help="Enter a message")
    parser.add_option("-s", "--show", action="store_true", dest="bShow")
    
    (options, args) = parser.parse_args()
    
    mc = MyClass(options.strMess)
    if options.bShow:
        mc.printMess()

if __name__ == "__main__":
    mc = MyClass("Before")
    mc.printMess()    
    parseParams()
