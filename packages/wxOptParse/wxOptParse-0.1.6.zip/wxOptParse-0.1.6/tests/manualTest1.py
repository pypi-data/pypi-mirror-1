#~ import optparse

class MyClass:
    def __init__(self, strMessage):
        self.strMess = strMessage
    
    def printMess(self):
        print self.strMess
        
if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-m", "--mess", action="store", type="string", dest="strMess", default="Bob", 
        help="Enter a message")
    parser.add_option("-s", "--show", action="store_true", dest="bShow")
    
    (options, args) = parser.parse_args()
    
    mc = MyClass(options.strMess)
    if options.bShow:
        mc.printMess()
