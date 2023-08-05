#! /usr/bin/env python
#
# Copyright (c) 2003 Richard Jones (richard@mechanicalcat.net)
# 
# $Id$

import sys, os, string, re, urlparse
import shutil, socket, errno, BaseHTTPServer
from glob import glob

def install_demo(home):
    # create the instance
    if os.path.exists(home):
        shutil.rmtree(home)
    from roundup import init, instance, password
    init.install(home, os.path.join('templates', 'classic'))
    # don't have email flying around
    os.remove(os.path.join(home, 'detectors', 'nosyreaction.py'))
    try:
        os.remove(os.path.join(home, 'detectors', 'nosyreaction.pyc'))
    except os.error, error:
        if error.errno != errno.ENOENT:
            raise
    init.write_select_db(home, 'anydbm')

    # figure basic params for server
    hostname = socket.gethostname()
    # pick a fairly odd, random port
    port = 8917
    while 1:
        print 'Trying to set up web server on port %d ...'%port,
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.connect((hostname, port))
        except socket.error, e:
            if not hasattr(e, 'args') or e.args[0] != errno.ECONNREFUSED:
                raise
            print 'should be ok.'
            break
        else:
            s.close()
            print 'already in use.'
            port += 100
    url = 'http://%s:%s/demo/'%(hostname, port)

    # write the config
    f = open(os.path.join(home, 'config.py'), 'r')
    s = f.read().replace('http://tracker.example/cgi-bin/roundup.cgi/bugs/',
        url)
    f.close()
    s = s + """
MYSQL_DBHOST = 'localhost'
MYSQL_DBUSER = 'rounduptest'
MYSQL_DBPASSWORD = 'rounduptest'
MYSQL_DBNAME = 'rounduptest'
MYSQL_DATABASE = (MYSQL_DBHOST, MYSQL_DBUSER, MYSQL_DBPASSWORD, MYSQL_DBNAME)
"""
    f = open(os.path.join(home, 'config.py'), 'w')
    f.write(s)
    f.close()

    # initialise the database
    init.initialise(home, 'admin')

    # add the "demo" user
    tracker = instance.open(home)
    db = tracker.open('admin')
    db.user.create(username='demo', password=password.Password('demo'),
        realname='Demo User', roles='User')
    db.commit()
    db.close()

def run_demo():
    ''' Run a demo server for users to play with for instant gratification.

        Sets up the web service on localhost. Disables nosy lists.
    '''
    home = os.path.abspath('demo')
    if not os.path.exists(home) or sys.argv[-1] == 'nuke':
        install_demo(home)

    f = open(os.path.join(home, 'config.py'), 'r')
    url = re.search(r'^TRACKER_WEB\s*=\s*[\'"](http.+/)[\'"]$', f.read(),
        re.M|re.I).group(1)
    f.close()
    hostname, port = urlparse.urlparse(url)[1].split(':')
    port = int(port)

    # ok, so start up the server
    from roundup.scripts.roundup_server import RoundupRequestHandler
    RoundupRequestHandler.TRACKER_HOMES = {'demo': home}
    httpd = BaseHTTPServer.HTTPServer((hostname, port), RoundupRequestHandler)
    print 'Server running - connect to:\n  %s'%url
    print '1. Log in as "demo"/"demo" or "admin"/"admin".'
    print '2. Hit Control-C to stop the server.'
    print '3. Re-start the server by running "python demo.py" again.'
    print '4. Re-initialise the server by running "python demo.py nuke".'
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print 'Keyboard Interrupt: exiting'

if __name__ == '__main__':
    run_demo()

# vim: set filetype=python ts=4 sw=4 et si
