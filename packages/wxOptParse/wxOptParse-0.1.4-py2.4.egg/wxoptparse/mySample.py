#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

import wxoptparse
import optparse, sys, subprocess

parser = optparse.OptionParser()
parser.add_option('-t', '--list', dest='list', action="store_true", 
     help='list the contents of an archive')
parser.add_option('-x', '--extract', '--get', dest='extract', action="store_true", 
     help='extract files from an archive')
parser.add_option('-c', '--create', dest='create', action="store_true", 
     help='create a new archive')
parser.add_option('-d', '--diff', '--compare', dest='diff', action="store_true", 
     help='find differences between archive and file system')
parser.add_option('-r', '--append', dest='append', action="store_true", 
     help='append files to the end of an archive')
parser.add_option('-u', '--update', dest='update', action="store_true", 
     help='only append files newer than copy in archive')
parser.add_option('-A', '--catenate', dest='catenate', action="store_true", 
     help='append tar files to an archive')
parser.add_option('--concatenate', dest='concatenate', action="store_true", 
     help='same as -A')
parser.add_option('--delete', dest='delete', action="store_true", 
     help='delete from the archive (not on mag tapes!)  Operation modifiers:')
parser.add_option('-W', '--verify', dest='verify', action="store_true", 
     help='attempt to verify the archive after writing it')
parser.add_option('--remove-files', dest='remove_files', action="store_true", 
     help='remove files after adding them to the archive')
parser.add_option('-k', '--keep-old-files', dest='keep_old_files', action="store_true", 
     help='don\'t replace existing files when extracting')
parser.add_option('--keep-newer-files', dest='keep_newer_files', action="store_true", 
     help='don\'t replace existing files that are newer than their archive copies')
parser.add_option('--overwrite', dest='overwrite', action="store_true", 
     help='overwrite existing files when extracting')
parser.add_option('--no-overwrite-dir', dest='no_overwrite_dir', action="store_true", 
     help='preserve metadata of existing directories')
parser.add_option('-U', '--unlink-first', dest='unlink_first', action="store_true", 
     help='remove each file prior to extracting over it')
parser.add_option('--recursive-unlink', dest='recursive_unlink', action="store_true", 
     help='empty hierarchies prior to extracting directory')
parser.add_option('-S', '--sparse', dest='sparse', action="store_true", 
     help='handle sparse files efficiently')
parser.add_option('-O', '--to-stdout', dest='to_stdout', action="store_true", 
     help='extract files to standard output')
parser.add_option('-G', '--incremental', dest='incremental', action="store_true", 
     help='handle old GNU-format incremental backup -g, --listed-incremental=FILE handle new GNU-format incremental backup')
parser.add_option('--ignore-failed-read', dest='ignore_failed_read', action="store_true", 
     help='do not exit with nonzero on unreadable files')
parser.add_option('--occurrence[', metavar='NUM]', dest='occurrence[', 
     help='process only the NUMth occurrence of each file in the archive. This option is valid only in conjunction with one of the subcommands --delete,')
parser.add_option('--diff,', dest='diff,', action="store_true", 
     help='--extract or --list and when a list of files is given either on the command line or via -T option. NUM defaults to 1.  Handling of file attributes:')
parser.add_option('--owner', metavar='NAME', dest='owner', 
     help='force NAME as owner for added files')
parser.add_option('--group', metavar='NAME', dest='group', 
     help='force NAME as group for added files')
parser.add_option('--mode', metavar='CHANGES', dest='mode', 
     help='force (symbolic) mode CHANGES for added files')
parser.add_option('--atime-preserve', dest='atime_preserve', action="store_true", 
     help='don\'t change access times on dumped files')
parser.add_option('-m', '--modification-time', dest='modification_time', action="store_true", 
     help='don\'t extract file modified time')
parser.add_option('--same-owner', dest='same_owner', action="store_true", 
     help='try extracting files with the same ownership')
parser.add_option('--no-same-owner', dest='no_same_owner', action="store_true", 
     help='extract files as yourself')
parser.add_option('--numeric-owner', dest='numeric_owner', action="store_true", 
     help='always use numbers for user/group names')
parser.add_option('-p', '--same-permissions', dest='same_permissions', action="store_true", 
     help='extract permissions information')
parser.add_option('--no-same-permissions', dest='no_same_permissions', action="store_true", 
     help='do not extract permissions information')
parser.add_option('--preserve-permissions', dest='preserve_permissions', action="store_true", 
     help='same as -p')
parser.add_option('-s', '--same-order', dest='same_order', action="store_true", 
     help='sort names to extract to match archive')
parser.add_option('--preserve-order', dest='preserve_order', action="store_true", 
     help='same as -s')
parser.add_option('--preserve', dest='preserve', action="store_true", 
     help='same as both -p and -s  Device selection and switching:')
parser.add_option('-f', '--file', metavar='ARCHIVE', dest='file', 
     help='use archive file or device ARCHIVE')
parser.add_option('--force-local', dest='force_local', action="store_true", 
     help='archive file is local even if has a colon')
parser.add_option('--rmt-command', metavar='COMMAND', dest='rmt_command', 
     help='use given rmt COMMAND instead of /etc/rmt')
parser.add_option('--rsh-command', metavar='COMMAND', dest='rsh_command', 
     help='use remote COMMAND instead of rsh -[0-7][lmh]                    specify drive and density')
parser.add_option('-M', '--multi-volume', dest='multi_volume', action="store_true", 
     help='create/list/extract multi-volume archive')
parser.add_option('-L', '--tape-length', metavar='NUM', dest='tape_length', 
     help='change tape after writing NUM x 1024 bytes')
parser.add_option('-F', '--info-script', metavar='FILE', dest='info_script', 
     help='run script at end of each tape (implies -M)')
parser.add_option('--new-volume-script', metavar='FILE', dest='new_volume_script', 
     help='same as -F FILE')
parser.add_option('--volno-file', metavar='FILE', dest='volno_file', 
     help='use/update the volume number in FILE  Device blocking:')
parser.add_option('-b', '--blocking-factor', metavar='BLOCKS', dest='blocking_factor', 
     help='BLOCKS x 512 bytes per record')
parser.add_option('--record-size', metavar='SIZE', dest='record_size', 
     help='SIZE bytes per record, multiple of 512')
parser.add_option('-i', '--ignore-zeros', dest='ignore_zeros', action="store_true", 
     help='ignore zeroed blocks in archive (means EOF)')
parser.add_option('-B', '--read-full-records', dest='read_full_records', action="store_true", 
     help='reblock as we read (for 4.2BSD pipes)  Archive format selection:')
parser.add_option('--format', metavar='FMTNAME', dest='format', 
     help='create archive of the given format. FMTNAME is one of the following: v7        old V7 tar format oldgnu    GNU format as per tar <= 1.12 gnu       GNU tar 1.13 format ustar     POSIX 1003.1-1988 (ustar) format posix     POSIX 1003.1-2001 (pax) format')
parser.add_option('--old-archive,', dest='old_archive,', action="store_true", 
     help='--portability   same as --format=v7')
parser.add_option('--posix', dest='posix', action="store_true", 
     help='same as --format=posix')
parser.add_option('--pax-option', dest='pax_option', action="store_true", 
     help='keyword[[:]=value][,keyword[[:]=value], ...] control pax keywords')
parser.add_option('-V', '--label', metavar='NAME', dest='label', 
     help='create archive with volume name NAME PATTERN                at list/extract time, a globbing PATTERN')
parser.add_option('-j', '--bzip2', dest='bzip2', action="store_true", 
     help='filter the archive through bzip2')
parser.add_option('-z', '--gzip', '--ungzip', dest='gzip', action="store_true", 
     help='filter the archive through gzip')
parser.add_option('-Z', '--compress', '--uncompress', dest='compress', action="store_true", 
     help='filter the archive through compress')
parser.add_option('--use-compress-program', metavar='PROG', dest='use_compress_program', 
     help='filter through PROG (must accept -d)  Local file selection:')
parser.add_option('-C', '--directory', metavar='DIR', dest='directory', 
     help='change to directory DIR')
parser.add_option('-T', '--files-from', metavar='NAME', dest='files_from', 
     help='get names to extract or create from file NAME')
parser.add_option('--null', dest='null', action="store_true", 
     help='-T reads null-terminated names, disable -C')
parser.add_option('--exclude', metavar='PATTERN', dest='exclude', 
     help='exclude files, given as a PATTERN')
parser.add_option('-X', '--exclude-from', metavar='FILE', dest='exclude_from', 
     help='exclude patterns listed in FILE')
parser.add_option('--anchored', dest='anchored', action="store_true", 
     help='exclude patterns match file name start (default)')
parser.add_option('--no-anchored', dest='no_anchored', action="store_true", 
     help='exclude patterns match after any /')
parser.add_option('--ignore-case', dest='ignore_case', action="store_true", 
     help='exclusion ignores case')
parser.add_option('--no-ignore-case', dest='no_ignore_case', action="store_true", 
     help='exclusion is case sensitive (default)')
parser.add_option('--wildcards', dest='wildcards', action="store_true", 
     help='exclude patterns use wildcards (default)')
parser.add_option('--no-wildcards', dest='no_wildcards', action="store_true", 
     help='exclude patterns are plain strings')
parser.add_option('--wildcards-match-slash', dest='wildcards_match_slash', action="store_true", 
     help='exclude pattern wildcards match \'/\' (default)')
parser.add_option('--no-wildcards-match-slash', dest='no_wildcards_match_slash', action="store_true", 
     help='exclude pattern wildcards do not match \'/\'')
parser.add_option('-P', '--absolute-names', dest='absolute_names', action="store_true", 
     help='don\'t strip leading `/\'s from file names')
parser.add_option('--dereference', dest='dereference', action="store_true", 
     help='dump instead the files symlinks point to')
parser.add_option('--no-recursion', dest='no_recursion', action="store_true", 
     help='avoid descending automatically in directories')
parser.add_option('-l', '--one-file-system', dest='one_file_system', action="store_true", 
     help='stay in local file system when creating archive')
parser.add_option('-K', '--starting-file', metavar='NAME', dest='starting_file', 
     help='begin at file NAME in the archive')
parser.add_option('--strip-path', metavar='NUM', dest='strip_path', 
     help='strip NUM leading components from file names before extraction')
parser.add_option('-N', '--newer', metavar='DATE-OR-FILE', dest='newer', 
     help='only store files newer than DATE-OR-FILE')
parser.add_option('--newer-mtime', metavar='DATE', dest='newer_mtime', 
     help='compare date and time when data changed only')
parser.add_option('--after-date', metavar='DATE', dest='after_date', 
     help='same as -N')
parser.add_option('--backup[', metavar='CONTROL]', dest='backup[', 
     help='backup before removal, choose version control')
parser.add_option('--suffix', metavar='SUFFIX', dest='suffix', 
     help='backup before removal, override usual suffix  Informative output:')
parser.add_option('--version', dest='version', action="store_true", 
     help='print tar program version number, then exit')
parser.add_option('-v', '--verbose', dest='verbose', action="store_true", 
     help='verbosely list files processed')
parser.add_option('--checkpoint', dest='checkpoint', action="store_true", 
     help='print directory names while reading the archive')
parser.add_option('--check-links', dest='check_links', action="store_true", 
     help='print a message if not all links are dumped')
parser.add_option('--totals', dest='totals', action="store_true", 
     help='print total bytes written while creating archive')
parser.add_option('--index-file', metavar='FILE', dest='index_file', 
     help='send verbose output to FILE')
parser.add_option('--utc', dest='utc', action="store_true", 
     help='print file modification dates in UTC')
parser.add_option('-R', '--block-number', dest='block_number', action="store_true", 
     help='show block number within archive with each message')
parser.add_option('-w', '--interactive', dest='interactive', action="store_true", 
     help='ask for confirmation for every action')
parser.add_option('--confirmation', dest='confirmation', action="store_true", 
     help='same as -w  Compatibility options: -o                                 when creating, same as --old-archive when extracting, same as --no-same-owner  The backup suffix is `~\', unless set with --suffix or SIMPLE_BACKUP_SUFFIX. The version control may be set with --backup or VERSION_CONTROL, values are:  t, numbered     make numbered backups nil, existing   numbered if numbered backups exist, simple otherwise never, simple   always make simple backups  ARCHIVE may be FILE, HOST:FILE or USER@HOST:FILE; DATE may be a textual date or a file name starting with `/\' or `.\', in which case the file\'s date is used. *This* `tar\' defaults to `--format=gnu -f- -b20\'.  Report bugs to <bug-tar@gnu.org>. ')
(options, args) = parser.parse_args()
sys.argv[0] = 'tar'
print sys.argv
try:
    retcode = subprocess.call("%s" % (" ".join(sys.argv)), shell=True)
    if retcode < 0:
        print >>sys.stderr, "Child was terminated by signal", -retcode
    else:
        print >>sys.stderr, "Child returned", retcode
except OSError, e:
    print >>sys.stderr, "Execution failed:", e
