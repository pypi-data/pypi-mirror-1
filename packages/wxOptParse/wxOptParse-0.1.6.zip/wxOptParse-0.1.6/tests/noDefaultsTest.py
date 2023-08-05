import optparse

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-f", "--file", action="store", type="string", dest="filename",
        help="Filename")
    parser.add_option("-p", "--path", action="store", type="string", dest="path", 
        help="Path")
    
    parser.add_option("-2", "--noHelp", action="store", type="string", dest="filename2")
    
    parser.add_option("-n", "--count", action="store", type="int", dest="number", 
        help="Count")
    parser.add_option("-m", "--float", action="store", type="float", dest="float",
        help="Float")
    parser.add_option("-b", "--bool", action="store_true", dest="bBool", 
        help="None by default")
    parser.add_option("", "--nbool", action="store_true", dest="bBool2", 
        help="None by default")
    #~ parser.add_option("-q", "--quiet",
                  #~ action="store_const", const=0, dest="verbose", help="Quiet")
    #~ parser.add_option("-v", "--verbose",
                      #~ action="store_const", const=1, dest="verbose", help="Verbose")
    #~ parser.add_option("--noisy",
                      #~ action="store_const", const=2, dest="verbose", help="Very verbose")

    parser.add_option("--choice", type="choice", dest="choice", choices=('One', "Two", "Three"), 
        help="One of ...")
    
    if '_wxOptParseCallback' in globals():
        parser._wxOptParseCallback = _wxOptParseCallback
    
    (options, args) = parser.parse_args()
    
