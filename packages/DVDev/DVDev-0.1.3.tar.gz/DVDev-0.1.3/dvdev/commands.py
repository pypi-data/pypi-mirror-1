# DVDev - Distributed Versioned Development - tools for Open Source Software
# Copyright (C) 2009  Douglas Mayle

# This file is part of DVDev.

# DVDev is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# DVDev is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with DVDev.  If not, see <http://www.gnu.org/licenses/>.

# The minimum number of modules necessary for a reload monitor
import os
import sys
import signal
# We'll use the yamltrak embedded argparse because it has some bug fixes.
from yamltrak.argparse import ArgumentParser

# We'll preload the mercurial modules to speed things up for the server
# processes, even if it's not strictly necessary for the monitor.
from mercurial import hg, ui, util, commands
from mercurial.error import RepoError

def build_repo_tree(root=os.getcwd(), maxdepth=2, firstrun=True):
    """Build a tree structure that represents the loaded repositories."""
    if maxdepth < 1 or not os.path.isdir(root):
        return
    # Check to see if the current directory is a repo.  If so, use that.  If
    # we've already run once, than we can reject any candidate directories
    # without a .hg subdir.  We do this speed optimization because mercurial
    # looks at every parent directory of the current one.  On second run, we
    # know that our parent is not a repo, so this directory would have to be
    # the root of the repo (containing a .hg subdir) to be considered.
    if not firstrun:
        if not '.hg' in os.listdir(root):
            return [build_repo_tree(subpath, maxdepth-1, False) for subpath in os.listdir(root)]
    
    myui = ui.ui()
    try:
        repo = hg.repository(myui, root)
    except (RepoError, util.Abort):
        # I'm feeling lazy, so I think I'm gonna do this recursively with a
        # maxdepth. For each subdirectory of the current, check to see if it's
        # a repo.
        return [build_repo_tree(subpath, maxdepth-1, False) for subpath in os.listdir(root)]

    return os.path.abspath(root)


def flatten(lst):
    """\
    Temp function to flatten the nested lists. At some point, the repos will be
    in dictionaries that mirror the directory's tree structure."""
    output = []
    try:
        if not isinstance(lst, basestring):
            for elem in lst:
                output += flatten(elem)
        else:
            return [lst]
        return output
    except TypeError:
        return [lst]

def launch_and_watch_child(args):
    if hasattr(os, 'fork'):
        # OS X Spits out ugly warnings if you import the webbrowser module
        # after forking.  Since we're going to fork, I'll preimport webbrowser.
        import webbrowser

        # Nice and easy...
        child = os.fork()
        if child == 0:
            return None, child
        childpid, exit_code = os.waitpid(child, 0)

        # Because of the way waitpid functions, we have to shift right by eight
        # to get the kind of exit code we expect.
        return exit_code >> 8, child

    from subprocess import Popen
    child = Popen(args)
    exit_code = child.wait()
    return exit_code, child.pid

def _server_args(args, nolaunch=False):
    if hasattr(os, 'fork'):
        # We care about the in memory arguments
        args.fragile = True
        args.debug = False
        if nolaunch:
            args.nolaunch = True
        return

    # We have to much around with the actual arguments to pass down.
    import sys

    my_python = sys.executable
    # On windows, we may have to fix this up if there is a space somewhere
    # in the path.  I'm inclined to just escape the space, and hope that
    # works.  PasteScript command uses win32api.GetShortPathName to find
    # the FAT16 equivalent filename.  I hope we can avoid that mess.
    if sys.platform == 'win32' and ' ' in my_python:
        my_python = my_python.replace(' ', '\\ ')

    server_args = [my_python] + sys.argv

    # We don't want the server process to become a reload monitor.
    if '--debug' in server_args:
        server_args.remove('--debug')
    if '-d' in server_args:
        server_args.remove('-d')

    # Setup the server process to quit out on any changes.
    if '-f' not in server_args and '--fragile' not in server_args:
        server_args.append('--fragile')

    if nolaunch:
        if '-n' not in server_args and '--nolaunch' not in server_args:
            server_args.append('--nolaunch')
    return server_args

def main():
    parser = ArgumentParser(description="DVDev: Distributed Versioned Development")

    parser.add_argument(
        'repositories', metavar='repository', type=str, nargs='*',
        default=[os.getcwd()],
        help='List of repositories to serve. If left blank, DVDev will search '
        'the current and subdirectories for existing repositories.')

    parser.add_argument(
        '-d', '--debug', action='store_true', default=False,
        help='Start dvdev in debugging mode.  This causes dvdev to monitor '
        'it\'s own source files and reload if they have changed.  Normally, '
        'only DVDev developers will ever have need of this functionality.')

    parser.add_argument(
        '-f', '--fragile', action='store_true', default=False,
        help='INTERNAL USE ONLY.  When specified, start a thread that watches '
        'DVDev\'s source files.  If any change, then quit this process.')

    parser.add_argument(
        '-c', '--create', action='store_true', default=False,
        help='For any directories passed in on the command line (or the '
        'current directory, if none), initialize them as a repository if they '
        'do not already contain one.')

    parser.add_argument(
        '-n', '--nolaunch', action='store_true', default=False,
        help='Don\'t launch a web browser after starting the http server.')

    parser.add_argument(
        '-p', '--port', type=int, default=4000,
        help='The port to serve on (by default: 4000).  If this port is in '
        'use, dvdev will try to randomly select an open port.')

    parser.add_argument(
        '-i', '--ip', default='0.0.0.0',
        help='The IP address to listen on. Defaults to 0.0.0.0, which means '
        'all IPv4 addresses')

    args = parser.parse_args()

    # We're gonna implement magic reload functionality, as seen in paster
    # serve. (Thanks, Ian Bicking, for the code and the explanation of what to
    # do.)

    # When this command is called with --debug, it does no actual serving.  It
    # opens a new process with a special flag that will tell DVDev to launch in
    # 'fragile mode'.  This means that it will call paste.reload.install(),
    # which starts a thread that kills the process if any of it's files change.

    # Meanwhile, back at the ranch (this process) we'll watch to see if our
    # subprocess dies and simply launch it again.  At the same time, we'll
    # watch for a Ctrl-C so that the user can interrupt us (and by extension,
    # the server.)

    if args.debug:

        nolaunch = args.nolaunch
        while True:
            child = None
            try:
                try:
                    print "Launching server process"
                    exit_code, child = launch_and_watch_child(_server_args(args, nolaunch))
                    if not child:
                        break

                    # We only let nolaunch be False on the first subprocess launch.
                    # After that, we never want to launch a webbrowser.
                    nolaunch = True
                except (SystemExit, KeyboardInterrupt):
                    "^C Pressed, shutting down server"
                    return
            finally:
                if child and hasattr(os, 'kill'):
                    # Apparantly, windows will litter processes in the case of
                    # catastrophic failure.
                    try:
                        os.kill(child, signal.SIGTERM)
                    except (OSError, IOError):
                        pass
            if exit_code != 3:
                # The child exited non-normally, so we will too.
                return exit_code


    if args.fragile:
        # This simple form does not work in jython, so I should fix that, since
        # the code is already written into paste.serve
        from paste import reloader
        # Do we need to allow a way to slow this down?  Defaults to checking
        # once per second.
        reloader.install()
        # If we ever add a config file, we need to add that to the watch list
        # like this:
        # reloader.watch_file(my_config_file)

    for index, repository in enumerate(args.repositories):
        if os.path.exists(repository):
            continue
        # Maybe this is a repository URL that mercurial recognizes?
        myui = ui.ui()
        myui.pushbuffer()

        from urllib2 import URLError
        try:
            commands.clone(myui, repository)
        except (RepoError, URLError):
            if args.create:
                try:
                    os.makedirs(repository)
                    try:
                        commands.init(myui, repository)
                        continue
                    except:
                        os.unlink(repository)
                except IOError:
                    pass
            print "Bad repository: %s" % repository
            import sys
            sys.exit(1)

        destination = myui.popbuffer().split('\n')[0]
        destination = destination.split('destination directory: ')[1]

        if not os.path.exists(destination):
            print "Successfully cloned repository %s but unable to read "\
            "local copy at %s" % (repository, destination)
            import sys
            sys.exit(1)
        print "Cloned repository %s in local directory %s" % (repository, destination)

        # Update our repository list with the new local copy
        args.repositories[index] = destination

    if args.create:
        all_repos = []
        for repo in args.repositories:
            found_repos = flatten(build_repo_tree(repo))
            if not found_repos:
                # Initialize
                myui = ui.ui()
                commands.init(myui, repo)
            else:
                all_repos += found_repos
    else:
        all_repos = filter(None, flatten([build_repo_tree(repo) for repo in args.repositories]))
    print "All repositories: %r" % all_repos
    config = {
        'use': 'egg:DVDev',
        'full_stack': 'true',
        'static_files': 'true',

        'reporoot': os.getcwd(),
        'cache_dir': os.path.join(os.getcwd(), 'data'),
        'beaker.session.key': 'dvdev',
        'beaker.session.secret': 'somesecret',

        'repo': ' '.join(all_repos),
        'project_home': 'issues',
        'who.log_level': 'debug',
        'who.log_file': 'stdout',
        'workspace': os.path.join(os.getcwd(), 'workspace'),
    }
    from dvdev.config.middleware import make_app
    app = make_app({'debug':(args.debug or args.fragile) and 'true' or 'false'}, **config)

    import webbrowser
    def webhelper(url):
        """\
        Curry the webbrowser.open method so that we can cancel it with a
        threaded timer."""
        def _launch_closure():
            webbrowser.open(url)
        return _launch_closure

    # Paste's httpserver doesn't return once it's started serving (which is
    # pretty normal).  The only problem is that we don't know if it
    # successfully captured the port unless it didn't return.  We don't want to
    # open the user's webbrowser unless we're successfully serving, so it's
    # sort of a chicken and egg problem.  We'll start a timer with a half
    # second delay (forever in computer time) in another thread.  If the server
    # returns, we'll cancel the timer, and try again.
    if not args.nolaunch:
        from threading import Timer
        safelaunch = Timer(0.7, webhelper('http://%s:%d/' % (args.ip, args.port)))
        safelaunch.start()

    import socket
    from paste.httpserver import serve
    try:
        serve(app, host=args.ip, port=args.port)
    except socket.error, e:
        safelaunch.cancel()
        print "Unable to serve on port %d : Error message was: %s" % (args.port, e[1])

if __name__ == '__main__':
    main()
