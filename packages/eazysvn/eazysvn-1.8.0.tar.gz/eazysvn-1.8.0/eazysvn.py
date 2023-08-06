#!/usr/bin/env python
# 
# Make simple Subversion revision merges and branch switching much easier.
#
# Copyright (c) 2006--2008 Philipp von Weitershausen, Marius Gedminas
#
# This program is distributed under the terms of the GNU General Public Licence
# See the file COPYING for details.
#
# Usage: eazysvn COMMAND ARGUMENTS
#  e.g.: eazysvn help
#
# For backwards compatibility you can rename (or symlink) eazysvn to ezswitch
# or ezmerge as a shortcut for eazysvn switch/merge.
#

import os
import sys
import optparse
import popen2 # TODO: use subprocess
from xml.dom import minidom


VERSION = '1.8.0'


#
# Helpers
#

def revs(rev):
    """
    Make sense out of convenient way of mentioning revisions

    For example, the revision 43 starts at r42 and ends at r43:

      >>> revs('43')
      (42, '43')

    Sometimes it is convenient to copy and paste revision numbers
    from svn log output

      >>> revs('r43')
      (42, '43')

    Revision ranges are also supported:

      >>> revs('42-21252')
      (41, 21252)
      >>> revs('42-HEAD')
      (41, 'HEAD')

    SVN-compatible revision ranges also work

      >>> revs('41:21252')
      (41, 21252)
      >>> revs('41:HEAD')
      (41, 'HEAD')

    Even reverse diffs that undo certain revisions are supported
    correctly:

      >>> revs('42:41') # undo r42
      (42, 41)

    But not with the "simple rev" syntax

      >>> revs('42-41')
      Traceback (most recent call last):
        ...
      ValueError: empty range (42-41)

    """
    if rev.startswith('r'):
        rev = rev[1:]
    if '-' in rev:
        rev, endrev = rev.split('-')
        rev = int(rev) - 1
        if not endrev == 'HEAD':
            endrev = int(endrev)
        if rev >= endrev:
            raise ValueError('empty range (%s-%s)' % (rev + 1, endrev))
    elif ':' in rev:
        rev, endrev = rev.split(':')
        rev = int(rev)
        if not endrev == 'HEAD':
            endrev = int(endrev)
    else:
        endrev = rev
        rev = int(rev) - 1
    return rev, endrev


def svninfo(path):
    """
    Return svn information about ``path``.
    """
    stdout, stdin = popen2.popen2('svn info %s' % path)
    return stdout.read()


def svnls(url):
    """
    Return a list of files under ``url``.
    """
    stdout, stdin = popen2.popen2('svn ls %s' % url)
    return stdout.read()


def svnlog(url):
    """
    Return svn log of ``url``, stopping on branchpoints, in XML.
    """
    stdout, stdin = popen2.popen2('svn log --non-interactive --stop-on-copy'
                                  ' --xml %s' % url)
    return stdout.read()


def currentbranch(path, svninfo=svninfo):
    """
    Let's set up a dummy 'svn info' command handler:

      >>> def dummyinfo(path):
      ...     return '''\
      ... Path: .
      ... URL: http://dev.worldcookery.com/svn/bla/trunk/blergh
      ... Repository UUID: ab69c8a2-bfcb-0310-9bff-acb20127a769
      ... Revision: 1654
      ... Node Kind: directory
      ... '''

    ``currentbranch()`` takes the svn path of the current working
    directory path returns it.

      >>> currentbranch('.', svninfo=dummyinfo)
      'http://dev.worldcookery.com/svn/bla/trunk/blergh'

      >>> def dummyinfo(path):
      ...     return '''\
      ... Path: .
      ... URL: http://dev.worldcookery.com/svn/bla/branches/foobar/blergh
      ... Repository UUID: ab69c8a2-bfcb-0310-9bff-acb20127a769
      ... Revision: 1654
      ... Node Kind: directory
      ... '''

      >>> currentbranch('.', svninfo=dummyinfo)
      'http://dev.worldcookery.com/svn/bla/branches/foobar/blergh'
 
    """
    lines = svninfo(path).splitlines()
    if lines[1].startswith('URL: '):
        url = lines[1][5:]
    else:
        url = lines[2][5:]
    return url


def determinebranch(branch, path, svninfo=svninfo):
    """
    Let's set up a dummy 'svn info' command handler:

      >>> def dummyinfo(path):
      ...     return '''\
      ... Path: .
      ... URL: http://dev.worldcookery.com/svn/bla/trunk/blergh
      ... Repository UUID: ab69c8a2-bfcb-0310-9bff-acb20127a769
      ... Revision: 1654
      ... Node Kind: directory
      ... '''

    ``determinebranch()`` takes the svn path of the current working
    directory path and mangles in either trunk or a branch repository
    path.  Here's an example for turning 'trunk' into 'branches':

      >>> determinebranch('foobar', '.', svninfo=dummyinfo)
      'http://dev.worldcookery.com/svn/bla/branches/foobar/blergh'

    Of course, if the current working copy is a trunk and we specify
    trunk, it keeps the trunk:

      >>> determinebranch('trunk', '.', svninfo=dummyinfo)
      'http://dev.worldcookery.com/svn/bla/trunk/blergh'

    Here's the whole thing the other way around:

      >>> def dummyinfo(path):
      ...     return '''\
      ... Path: .
      ... URL: http://dev.worldcookery.com/svn/bla/branches/foobar/blergh
      ... Repository UUID: ab69c8a2-bfcb-0310-9bff-acb20127a769
      ... Revision: 1654
      ... Node Kind: directory
      ... '''

      >>> determinebranch('trunk', '.', svninfo=dummyinfo)
      'http://dev.worldcookery.com/svn/bla/trunk/blergh'
 
    """
    lines = svninfo(path).splitlines()
    if lines[1].startswith('URL: '):
        url = lines[1][5:]
    else:
        url = lines[2][5:]

    chunks = url.split('/')
    chunks.reverse()
    new_chunks = []

    while chunks:
        ch = chunks.pop()
        if ch in ('branch', 'branches'):
            chunks.pop()
            if branch == 'trunk':
                new_chunks.append(branch)
            else:
                new_chunks.append(ch)
                new_chunks.append(branch)
        elif ch == 'trunk' and branch != 'trunk':
            new_chunks.append('branches')
            new_chunks.append(branch)
        else:
            new_chunks.append(ch)

    return '/'.join(new_chunks)


def determinetag(tagname, path, svninfo=svninfo):
    """
    Let's set up a dummy 'svn info' command handler:

      >>> def dummyinfo(path):
      ...     return '''\
      ... Path: .
      ... URL: http://dev.worldcookery.com/svn/bla/trunk/blergh
      ... Repository UUID: ab69c8a2-bfcb-0310-9bff-acb20127a769
      ... Revision: 1654
      ... Node Kind: directory
      ... '''

    ``determinetag()`` takes the svn path of the current working
    directory path and mangles it to point to a named tag.
    Here's an example:

      >>> determinetag('foobar', '.', svninfo=dummyinfo)
      'http://dev.worldcookery.com/svn/bla/tags/foobar/blergh'

    We can do the same with branches

      >>> def dummyinfo(path):
      ...     return '''\
      ... Path: .
      ... URL: http://dev.worldcookery.com/svn/bla/branches/foobar/blergh
      ... Repository UUID: ab69c8a2-bfcb-0310-9bff-acb20127a769
      ... Revision: 1654
      ... Node Kind: directory
      ... '''

      >>> determinetag('foobaz', '.', svninfo=dummyinfo)
      'http://dev.worldcookery.com/svn/bla/tags/foobaz/blergh'
 
    """
    lines = svninfo(path).splitlines()
    if lines[1].startswith('URL: '):
        url = lines[1][5:]
    else:
        url = lines[2][5:]

    chunks = url.split('/')
    chunks.reverse()
    new_chunks = []

    while chunks:
        ch = chunks.pop()
        if ch in ('branch', 'branches'):
            chunks.pop()
            new_chunks.append('tags')
            new_chunks.append(tagname)
        elif ch == 'trunk':
            new_chunks.append('tags')
            new_chunks.append(tagname)
        else:
            new_chunks.append(ch)

    return '/'.join(new_chunks)


def listbranches(path, svninfo=svninfo, svnls=svnls):
    r"""
    Let's set up a dummy 'svn info' command handler:

      >>> def dummyinfo(path):
      ...     return '''\
      ... Path: .
      ... URL: http://dev.worldcookery.com/svn/bla/trunk/blergh
      ... Repository UUID: ab69c8a2-bfcb-0310-9bff-acb20127a769
      ... Revision: 1654
      ... Node Kind: directory
      ... '''

    and a dummy 'svn ls' as well:

      >>> def dummyls(path):
      ...     assert path == 'http://dev.worldcookery.com/svn/bla/branches'
      ...     return '''\
      ... foo/
      ... README.txt
      ... bar/
      ... baz/
      ... '''

    ``listbranches()`` takes the svn path of the current working
    directory path, finds the URL of the repository, and lists all branches
    in that repository.

      >>> listbranches('.', svninfo=dummyinfo, svnls=dummyls)
      ['foo', 'bar', 'baz']
 
    """
    url = currentbranch(path, svninfo=svninfo)
    chunks = url.split('/')

    while chunks:
        ch = chunks.pop()
        if ch in ('branch', 'branches'):
            chunks.append(ch)
            break
        elif ch == 'trunk':
            chunks.append('branches')
            break

    branches = []
    for line in svnls('/'.join(chunks)).splitlines():
        if line.endswith('/'):
            branches.append(line[:-1])
    return branches


def branchpoints(branch, svnlog=svnlog):
    r"""
    Let's set up a dummy 'svn log' command handler:

      >>> def dummylog(url):
      ...     return '''\
      ... <?xml version="1.0" encoding="utf-8"?>
      ... <log>
      ... <logentry
      ...    revision="4515">
      ... <author>mg</author>
      ... <date>2007-01-11T16:30:07.775378Z</date>
      ... <msg>Blah blah.
      ... 
      ... Blah blah.
      ... 
      ... </msg>
      ... </logentry>
      ... <logentry
      ...    revision="4504">
      ... <author>mg</author>
      ... <date>2007-01-11T16:29:32.166370Z</date>
      ... <msg>create branch</msg>
      ... </logentry>
      ... </log>
      ... '''

    ``branchpoints()`` takes the svn URL and finds the revision number of the
    branch point.

      >>> branchpoints('http://dev.worldcookery.com/svn/bla/branches/foobar',
      ...             svnlog=dummylog)
      (4504, 4515)

    """
    xml = svnlog(branch)
    try:
        dom = minidom.parseString(xml)
    except:
        sys.exit("Could not parse svn log output:\n\n" + xml)
    newest_entry = dom.getElementsByTagName('logentry')[0]
    oldest_entry = dom.getElementsByTagName('logentry')[-1]
    return (int(oldest_entry.getAttribute('revision')),
            int(newest_entry.getAttribute('revision')))


#
# Command registration
#


COMMANDS = {}
ALIASES = {}

def command(cmd, help_msg, alias=None):
    """Register a command."""
    def decorator(fn):
        COMMANDS[cmd] = fn
        if alias:
            ALIASES[alias] = fn
        fn.help_msg = help_msg
        fn.alias = alias
        return fn
    return decorator


#
# Commands
#

@command('merge', 'merge branches', alias="ezmerge")
def ezmerge(argv, progname=None):
    progname = progname or os.path.basename(argv[0])
    parser = optparse.OptionParser(
                "usage: %prog [options] [rev] source-branch [wc-path]"
                "       %prog -l\n",
                prog=progname,
                description="merge changes from Subversion branches")
    parser.add_option('-l', '--list',
                      help='list existing branches',
                      action='store_true', dest='list_branches', default=False)
    parser.add_option('-d', '--diff',
                      help='show a diff of changes on the branch',
                      action='store_true', dest='diff', default=False)
    parser.add_option('-n', '--dry-run',
                      help='do not touch any files on disk or in subversion',
                      action='store_true', dest='dry_run', default=False)
    try:
        opts, args = parser.parse_args(argv[1:])
        if not opts.list_branches:
            if len(args) < 1:
                parser.error("too few arguments, try %s --help" % progname)
            elif len(args) > 3:
                parser.error("too many arguments, try %s --help" % progname)
    except optparse.OptParseError, e:
        sys.exit(e)

    if opts.list_branches:
        # TODO: allow a different wc-path
        print '\n'.join(listbranches('.'))
        return

    if len(args) == 1:
        rev = 'ALL'
        branchname = args[0]
    else:
        rev = args[0]
        branchname = args[1]
    path = '.'
    if len(args) > 2:
        path = args[2]

    branch = determinebranch(branchname, path)
    if branchname != 'trunk' and not branchname.endswith('branch'):
        branchname += ' branch'
    if rev == 'ALL':
        beginrev, endrev = branchpoints(branch)
        if branchname == 'trunk':
            # Special case: when merging from trunk, don't look at the revision
            # when trunk began, but instead look when the current branch began
            beginrev, ignore = branchpoints(currentbranch(path))
        msg = "Merge %s" % (branchname)
    else:
        beginrev, endrev = revs(rev)
        if '-' in rev or ':' in rev:
            what = "revisions %s" % rev
        else:
            what = "revision %s" % rev
        msg = "Merge %s from %s" % (what, branchname)
    if opts.diff:
        merge_cmd = "svn diff -r %s:%s %s" % (beginrev, endrev, branch)
    else:
        merge_cmd = "svn merge -r %s:%s %s %s" % (beginrev, endrev, branch, path)
    if not opts.diff:
        print msg, "with"
        print
        print " ", merge_cmd
        print
    else:
        print msg
    log_cmd = "svn log -r %s:%s %s" % (beginrev + 1, endrev, branch)
    os.system(log_cmd)
    if opts.diff:
        print
        print " ", merge_cmd
        print
    if not opts.dry_run:
        os.system(merge_cmd)


@command('revert', 'revert checkins', alias="ezrevert")
def ezrevert(argv, progname=None):
    progname = progname or os.path.basename(argv[0])
    parser = optparse.OptionParser(
                "usage: %prog [options] rev [wc-path]",
                prog=progname,
                description="revert changes")
    parser.add_option('-n', '--dry-run',
                      help='do not touch any files on disk or in subversion',
                      action='store_true', dest='dry_run', default=False)
    try:
        opts, args = parser.parse_args(argv[1:])
        if len(args) < 1:
            parser.error("too few arguments, try %s --help" % progname)
        elif len(args) > 2:
            parser.error("too many arguments, try %s --help" % progname)
    except optparse.OptParseError, e:
        sys.exit(e)

    rev = args[0]
    path = '.'
    if len(args) > 1:
        path = args[1]

    if rev == 'ALL':
        sys.exit("I refuse to revert all checkins in a branch")
    else:
        beginrev, endrev = revs(rev)
        if '-' in rev or ':' in rev:
            what = "revisions %s" % rev
        else:
            what = "revision %s" % rev
        print "Revert %s with" % what
    print
    merge_cmd = "svn merge -r %s:%s %s" % (endrev, beginrev, path)
    print " ", merge_cmd
    print
    log_cmd = "svn log -r %s:%s %s" % (beginrev + 1, endrev, path)
    os.system(log_cmd)
    if not opts.dry_run:
        os.system(merge_cmd)


@command('switch', 'switch to a different branch', alias="ezswitch")
def ezswitch(argv, progname=None):
    progname = progname or os.path.basename(argv[0])
    parser = optparse.OptionParser(
                "usage: %prog [-n] [-c] [-m MSG] branch [wc-path]\n"
                "       %prog -l\n"
                "       %prog",
                prog=progname,
                description="Switch the working directory to a different"
                            " Subversion branch.  When run without"
                            " arguments, %prog will print the"
                            " URL of the current branch.")
    parser.add_option('-l', '--list',
                      help='list existing branches',
                      action='store_true', dest='list_branches', default=False)
    parser.add_option('-c', '--create-branch',
                      help='create the new branch before switching to it',
                      action='store_true', dest='create_branch', default=False)
    parser.add_option('-m',
                      help='commit message for --create-branch',
                      action='store', dest='message', default=None)
    parser.add_option('-n', '--dry-run',
                      help='do not touch any files on disk or in subversion',
                      action='store_true', dest='dry_run', default=False)
    try:
        opts, args = parser.parse_args(argv[1:])
        if len(args) > 2:
            parser.error("too many arguments, try %s --help" % progname)
    except optparse.OptParseError, e:
        sys.exit(e)

    path = '.'

    if opts.list_branches:
        # TODO: allow a different wc-path
        print '\n'.join(listbranches(path))
        return

    if not args:
        print currentbranch(path)
        return

    branch = args[0]
    if len(args) > 1:
        path = args[1]

    branch = determinebranch(branch, path)
    if opts.create_branch:
        cur_branch = currentbranch(path)
        cmd = "svn cp %s %s" % (cur_branch, branch)
        if opts.message:
            cmd += " -m '%s'" % opts.message
        print cmd
        if not opts.dry_run:
            os.system(cmd)

    cmd = "svn switch %s %s" % (branch, path)
    print cmd
    if not opts.dry_run:
        os.system(cmd)


@command('tag', 'make tags')
def eztag(argv, progname=None):
    progname = progname or os.path.basename(argv[0])
    parser = optparse.OptionParser(
                "usage: %prog [-n] [-m MSG] newtagname",
                prog=progname,
                description="Make a Subversion tag.")
    parser.add_option('-m',
                      help='commit message',
                      action='store', dest='message', default=None)
    parser.add_option('-n', '--dry-run',
                      help='do not make the tag, just print the command',
                      action='store_true', dest='dry_run', default=False)
    try:
        opts, args = parser.parse_args(argv[1:])
        if len(args) > 2:
            parser.error("too many arguments, try %s --help" % progname)
    except optparse.OptParseError, e:
        sys.exit(e)

    # TODO: allow a different wc-path
    path = '.'

    if len(args) < 1:
        parser.error("too few arguments, try %s --help" % progname)
    newtag = determinetag(args[0], path)

    cmd = "svn cp %s %s" % (path, newtag)
    if opts.message:
        cmd += " -m '%s'" % opts.message
    print cmd
    if not opts.dry_run:
        os.system(cmd)


@command('branchurl', 'print full URL of a branch', alias="ezbranch")
def ezbranch(argv, progname=None):
    progname = progname or os.path.basename(argv[0])
    parser = optparse.OptionParser(
                "usage: %prog branch [wc-path]\n"
                "       %prog -l\n"
                "       %prog",
                prog=progname,
                description="Print the URL of a named branch.")
    parser.add_option('-l', '--list',
                      help='list existing branches',
                      action='store_true', dest='list_branches', default=False)
    try:
        opts, args = parser.parse_args(argv[1:])
        if len(args) > 2:
            parser.error("too many arguments, try %s --help" % progname)
    except optparse.OptParseError, e:
        sys.exit(e)

    path = '.'

    if opts.list_branches:
        # TODO: allow a different wc-path
        print '\n'.join(listbranches(path))
        return

    if not args:
        print currentbranch(path)
        return

    branch = args[0]
    if len(args) > 1:
        path = args[1]

    print determinebranch(branch, path)


@command('rmbranch', 'remove branches')
def rmbranch(argv, progname=None):
    progname = progname or os.path.basename(argv[0])
    parser = optparse.OptionParser(
                "usage: %prog [-n] [-m MSG] branch\n"
                "       %prog -l\n",
                prog=progname,
                description="Remove a named Subversion branch.")
    parser.add_option('-l', '--list',
                      help='list existing branches',
                      action='store_true', dest='list_branches', default=False)
    parser.add_option('-m',
                      help='commit message',
                      action='store', dest='message', default=None)
    parser.add_option('-n', '--dry-run',
                      help='do not remove the branch, just print the command',
                      action='store_true', dest='dry_run', default=False)
    try:
        opts, args = parser.parse_args(argv[1:])
        if len(args) > 1:
            parser.error("too many arguments, try %s --help" % progname)
    except optparse.OptParseError, e:
        sys.exit(e)

    path = '.'

    if opts.list_branches:
        # TODO: allow a different wc-path
        print '\n'.join(listbranches(path))
        return

    if len(args) < 1:
        parser.error("too few arguments, try %s --help" % progname)
    branch = determinebranch(args[0], path)

    cmd = "svn rm %s" % branch
    if opts.message:
        cmd += " -m '%s'" % opts.message
    print cmd
    if not opts.dry_run:
        os.system(cmd)


@command('mvbranch', 'rename branches')
def mvbranch(argv, progname=None):
    progname = progname or os.path.basename(argv[0])
    parser = optparse.OptionParser(
                "usage: %prog [-n] [-m MSG] oldbranch newbranch\n"
                "       %prog -l\n",
                prog=progname,
                description="Rename a Subversion branch.")
    parser.add_option('-l', '--list',
                      help='list existing branches',
                      action='store_true', dest='list_branches', default=False)
    parser.add_option('-m',
                      help='commit message',
                      action='store', dest='message', default=None)
    parser.add_option('-n', '--dry-run',
                      help='do not rename the branch, just print the command',
                      action='store_true', dest='dry_run', default=False)
    try:
        opts, args = parser.parse_args(argv[1:])
        if len(args) > 2:
            parser.error("too many arguments, try %s --help" % progname)
    except optparse.OptParseError, e:
        sys.exit(e)

    path = '.'

    if opts.list_branches:
        # TODO: allow a different wc-path
        print '\n'.join(listbranches(path))
        return

    if len(args) < 2:
        parser.error("too few arguments, try %s --help" % progname)
    oldbranch = determinebranch(args[0], path)
    newbranch = determinebranch(args[1], path)

    cmd = "svn mv %s %s" % (oldbranch, newbranch)
    if opts.message:
        cmd += " -m '%s'" % opts.message
    print cmd
    if not opts.dry_run:
        os.system(cmd)


@command('branchdiff', 'show combined diff of all changes on a branch')
def branchdiff(argv, progname=None):
    progname = progname or os.path.basename(argv[0])
    parser = optparse.OptionParser(
                "usage: %prog [options] [branch [wc-path]]"
                "       %prog -l\n",
                prog=progname,
                description="show combined diff of all changes made on a branch")
    parser.add_option('-l', '--list',
                      help='list existing branches',
                      action='store_true', dest='list_branches', default=False)
    opts, args = parser.parse_args(argv[1:])
    path = '.'
    if opts.list_branches:
        print '\n'.join(listbranches(path))
        return
    if args:
        branch = args[0]
        if len(args) > 1:
            path = args[1]
        branch = determinebranch(args[0], path)
    else:
        branch = currentbranch(path)
    beginrev, endrev = branchpoints(branch)
    diff_cmd = "svn diff -r %s:%s %s" % (beginrev, endrev, branch)
    print diff_cmd
    os.system(diff_cmd)


@command('selftest', 'run self-tests')
def selftest(argv, progname=None):
    import doctest
    failures, tests = doctest.testmod()
    if not failures:
        print "All %d tests passed." % tests


@command('help', 'this help message')
def help(argv, progname=None):
    progname = os.path.basename(argv[0])
    print "usage: %s command arguments" % progname
    print "where command is one of"
    width = max(map(len, COMMANDS))
    for cmd, fn in sorted(COMMANDS.items()):
        if fn.alias:
            alias = ' (aka %s)' % fn.alias
        else:
            alias = ''
        print "  %s -- %s%s" % (cmd.ljust(width), fn.help_msg, alias)
    print "Use %s command --help for more information about commands" % progname


#
# Dispatch
#

def eazysvn(argv):
    progname = os.path.basename(argv[0])
    if len(argv) < 2 or argv[1] in ('-h', '--help'):
        return help(argv)
    cmd = argv.pop(1)
    func = COMMANDS.get(cmd)
    if func is None:
        sys.exit("Unknown command: %s." % cmd)
    progname = progname + ' ' + cmd
    return func(argv, progname=progname)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--version':
        print "eazysvn version %s" % VERSION
        sys.exit(0)
    cmd = os.path.basename(sys.argv[0])
    if cmd.endswith('.py'):
        cmd = cmd[:-len('.py')]
    func = ALIASES.get(cmd, eazysvn)
    sys.exit(func(sys.argv))


def additional_tests(): # for setup.py test
    import doctest
    return doctest.DocTestSuite()


if __name__ == '__main__':
    main()
