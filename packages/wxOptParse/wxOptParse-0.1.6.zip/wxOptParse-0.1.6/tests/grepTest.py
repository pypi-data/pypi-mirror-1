import optparse

"""
grep, egrep, fgrep - print lines matching a pattern
"""
if __name__ == "__main__":
    parser = optparse.OptionParser(add_help_option=False)

    parser.add_option('-A', '--after-context', metavar='NUM', dest="nAfterContext", 
        type="int", 
        help="""Print NUM  lines  of  trailing  context  after  matching  lines. Places  a  line  containing  --  between  contiguous  groups  of matches.""")

    parser.add_option('-a', '--text', dest="bText", action="store_true",
        help="""Process a binary file as if it were text; this is equivalent  to the --binary-files=text option.""")

    parser.add_option('-B', '--before-context', metavar='NUM', dest="nBeforeContext",
        type="int",
        help="""Print  NUM  lines  of  leading  context  before  matching lines. Places  a  line  containing  --  between  contiguous  groups  of matches.""")

    parser.add_option('-C', '--context', metavar="NUM",
        help="""Print  NUM lines of output context.  Places a line containing -- between contiguous groups of matches.""")

    parser.add_option('-b', '--byte-offset',
        help="""Print the byte offset within the input file before each line of output.""")

    parser.add_option('', '--binary-files', metavar='TYPE', dest="strBinaryFiles",
        help=' '.join(["If the first few bytes of a file indicate that the file contains binary data, assume that the file is of type TYPE.",
            "By  default, TYPE is binary, and grep normally outputs either a one-line message saying that a binary file matches, or no message",
            "if  there is  no  match.   If  TYPE  is without-match, grep assumes that a binary file does not match; this is equivalent to the -I option.",
            "If  TYPE  is  text,  grep  processes a binary file as if it were text; this is  equivalent  to  the  -a  option.",
            "Warning:  grep --binary-files=text  might output binary garbage, which can have nasty side effects if the output is ",
            "a terminal and if the terminal driver interprets some of it as commands.",]))

    parser.add_option('--colour', '--color', type="choice", metavar="WHEN", choices=('never', 'always', 'auto'), default='auto',
        help="""Surround  the matching string with the marker find in GREP_COLOR environment variable. WHEN may be 'never', 'always', or 'auto'""")

    parser.add_option('-c', '--count', dest="bCount", action="store_true",
        help="""Suppress normal output; instead print a count of matching  lines for  each  input  file.  With the -v, --invert-match option (see below), count non-matching lines.""")

    parser.add_option('-D', '--devices', metavar='ACTION', dest='strDevices', choices=('read', 'skip'),
        help="""If an input file is a device, FIFO or socket, use ACTION to process  it.   By default, ACTION is read, which means that devices are read just as if they were  ordinary  files.   If  ACTION  is skip, devices are silently skipped.""")

    parser.add_option('-d', '--directories', type="choice", metavar='ACTION', dest='strDirectories', choices=('read', 'skip', 'recurse'),
        help=' '.join([
            "If an  input file is a directory, use ACTION to process it.",
            "By default, ACTION is read, which means that directories are read just  as if they were ordinary files.",
            "If ACTION is skip, directories are silently skipped.",
            "If ACTION is recurse,  grep  reads all  files under each directory, recursively; this is equivalent to the -r option."]))

    parser.add_option('-E', '--extended-regexp', dest="bExtendedRegexp", action="store_true",
        help="""Interpret PATTERN as an extended regular expression (see below).""")

    parser.add_option('-e', '--regexp', metavar='PATTERN', dest='strRegexp', 
        help="""Use PATTERN as the pattern; useful to protect patterns beginning with -.""")

    parser.add_option('-F', '--fixed-strings',  dest='bFixedStrings', action="store_true",
        help="""Interpret PATTERN as a list of fixed strings, separated by new-lines, any of which is to be matched.""")
    
    parser.add_option('-P', '--perl-regexp',  dest="bPerlRegexp", action="store_true",
        help="""Interpret PATTERN as a Perl regular expression.""")
        
    parser.add_option('-f', '--file', metavar='FILE', dest="strFile", type='string',
        help="""Obtain patterns from FILE, one per line.  The  empty file contains zero patterns, and therefore matches nothing.""")

    parser.add_option('-G', '--basic-regexp', dest='bBasicRegexp', action="store_true", 
        help="""Interpret  PATTERN  as  a  basic regular expression (see below). This is the default.""")

    parser.add_option('-H', '--with-filename', dest='bWithFilename', action="store_true",
        help="""Print the filename for each match.""")

    parser.add_option('-h', '--no-filename', dest="bNoFilename", action="store_true",
        help="""Suppress the prefixing of  filenames  on  output  when  multiple files are searched.""")
              
    parser.add_option('--help', dest="bHelp", action="store_true",
        help="""Output a brief help message.""")

    parser.add_option('-I', dest='bI', action="store_true",
        help="""Process  a  binary  file as if it did not contain matching data; this is equivalent to the --binary-files=without-match option.""")

    parser.add_option('-i', '--ignore-case', dest='bIgnoreCase', action="store_true",
        help="""Ignore case distinctions in both the PATTERN and the input files.""")

    parser.add_option('-L', '--files-without-match', dest='bFilesWithoutMatch', action="store_true",
        help=' '.join(["Suppress  normal  output;  instead  print the name of each input",
              "file from which no output would normally have been printed.  The",
              "scanning will stop on the first match."]))

    parser.add_option('-l', '--files-with-matches', dest="bFilesWithMatches", action="store_true",
        help=' '.join(["Suppress  normal  output;  instead  print the name of each input",
              "file from which output would normally have been printed.",
              "The scanning will stop on the first match."]))

    parser.add_option('-m', '--max-count', metavar='NUM', type='int', dest='nMaxCount',
        help=' '.join(["Stop  reading  a file after NUM matching lines.",
            "If the input is standard input from a regular file, and NUM matching lines are output, ",
            "grep ensures that the standard input is positioned to just after the last matching line before exiting, ",
            "regardless of the presence of trailing context lines.  ",
            "This enables a calling process to resume a search.  ",
            "When grep stops after NUM matching lines, it outputs any trailing context lines.",
            "When the -c or --count option is also used,  grep does not output a count greater than NUM.",
            "When the -v or --invert-match option is also used, grep stops after outputting NUM non-matching lines."]))

    parser.add_option('--mmap', dest="bMmap", action="store_true",
        help=' '.join(["If possible, use the mmap(2) system call to read input,  instead of  the default read(2) system call.",
            "In some situations, --mmap yields better performance.",
            "However, --mmap can cause undefined behavior (including core dumps) if an input file shrinks while grep is operating,",
            "or if an I/O error occurs."]))

    parser.add_option('-n', '--line-number', dest='bLineNumber', action='store_true',
        help="""Prefix each line of output with the line number within its input file.""")

    parser.add_option('-o', '--only-matching', dest='bOnlyMatching', action='store_true',
        help="""Show only the part of a matching line that matches PATTERN.""")

    parser.add_option('--label', metavar='LABEL', dest='strLabel', 
        help="""Displays input actually coming from standard input as input coming from file LABEL.  This is especially useful for  tools  like zgrep, e.g.  gzip -cd foo.gz |grep --label=foo something""")

    parser.add_option('--line-buffering', dest='bLineBuffering', action='store_true',
        help="""Use line buffering, it can be a performance penality.""")

    parser.add_option('-q', '--quiet', '--silent', dest='bQuiet', action='store_true',
        help="""Quiet;  do  not write anything to standard output.  Exit immediately with zero status if any match is found, even if  an  error was detected.  Also see the -s or --no-messages option.""")

    parser.add_option('-R', '-r', '--recursive', dest='bRecursive', action="store_true",
        help="""Read all files under each directory, recursively; this is equivalent to the -d recurse option.""")

    parser.add_option('--include', metavar='PATTERN', dest='strInclude',
        help="""Recurse in directories only searching file matching PATTERN.""")

    parser.add_option('--exclude', metavar='PATTERN', dest='strExclude',
        help="""Recurse in directories skip file matching PATTERN.""")

    parser.add_option('-s', '--no-messages', dest='bNoMessages', action="store_true",
        help=' '.join(["Suppress error messages about nonexistent or unreadable files.",
              "Portability note: unlike GNU grep, traditional grep did not conform to POSIX.2,",
              "because traditional grep lacked a -q option and its -s option behaved like GNU grep's -q option.",
              "Shell scripts intended to be portable to traditional grep should avoid both -q",
              "and -s and should redirect output to /dev/null instead."]))

    parser.add_option('-U', '--binary', dest='bBinary', action='store_true',
        help=' '.join(["Treat  the  file(s) as binary.  By default, under MS-DOS and MS-Windows, ",
            "grep guesses the file type by looking at the contents of the first 32KB read from the file.",
            "If grep decides the file is a text file, it strips the CR characters from the original file contents",
            "(to  make  regular expressions with ^ and $ work correctly).",
            "Specifying -U overrules this guesswork, causing all files to be read and passed to the matching mechanism verbatim;",
            "if the file is a text file with CR/LF pairs at the end  of each line, this will cause some regular expressions to fail.",
            "This option has no effect on platforms other than MS-DOS and  MS-Windows."]))

    parser.add_option('-u', '--unix-byte-offsets', dest='bUnixByteOffsets', action="store_true",
        help=' '.join(["Report Unix-style byte offsets.",
            "This switch causes grep to report byte offsets as if the file were  Unix-style text file,",
            "i.e. with CR characters stripped off.",
            "This will produce results identical to running grep on a Unix machine.",
            "This option has no effect unless -b option is also used; it has no effect on platforms other than MS-DOS and MS-Windows."]))

    parser.add_option('-V', '--version', dest="bVersion", action="store_true",
        help="""Print the version number of grep to standard error.  This version number should be included in all bug reports (see below).""")

    parser.add_option('-v', '--invert-match', dest="bInvertMatch", action="store_true",
        help="""Invert the sense of matching, to select non-matching lines.""")
        
    parser.add_option('-w', '--word-regexp', dest='bWordRegexp', action="store_true",
        help=' '.join(["Select only those lines containing matches that form whole words. ",
            "The test is that the matching substring must either be at the beginning of the line, ",
            "or preceded by a non-word constituent character. ",
            "Similarly, it must be either at the end of the line or followed by a non-word constituent character. ",
            "Word constituent characters are letters, digits, and the underscore."]))

    parser.add_option('-x', '--line-regexp', dest='bLineRegexp', action="store_true",
        help="""Select only those matches that exactly match the whole line.""")

    parser.add_option('-y', dest="bY", action="store_true",
        help="""Obsolete synonym for -i.""")

    parser.add_option('-Z', '--null', dest="bNull", action="store_true",
        help=' '.join(["Output a zero byte (the ASCII NUL character) instead of the character that normally follows a file name. ",
            "For example, grep -lZ outputs a zero byte after each file name instead of the usual newline. ",
            "This option makes the output unambiguous, even in the presence of file names containing unusual characters like newlines. ",
            "This option can be used with commands like find -print0, perl -0, sort -z, and xargs -0 to process arbitrary file names,",
            "even those that contain newline characters."]))


    if '_wxOptParseCallback' in globals():
        parser._wxOptParseCallback = _wxOptParseCallback
    
    (options, args) = parser.parse_args()
    
