#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

# RPX - Reverse ProXy accelerator
# Copyright (C) 2009 Pilot Systems
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, os, time, urllib, syslog, signal, pwd

class _custom_urlopener(urllib.FancyURLopener):
    version = "RPX/1.0"
    def http_error_default(self, url, fp, errcode, errmsg, headers):
        return errcode
urllib._urlopener = _custom_urlopener()

def log(what, explanation=""):
    print "%s %-8s %s"%(time.strftime('%Y/%m/%d %H:%M:%S'), what, explanation)
    sys.stdout.flush()

def alarmhandler(a,b):
    log("TIMEOUT")

def rpx(apachelogfile, docroot, docfile, backend, backendtimeout, rpxlogfile):
 
    if rpxlogfile:
        sys.stdout = open(rpxlogfile,"a")
    if not os.path.isdir(docroot):
        os.mkdir(docroot)
    f = open(apachelogfile)
    while f.readline(): # go to the end of the file
        pass
    while True: # now, wait for new data
        line = f.readline()
        if line=='': # no new data, sleep a little bit and try again
            time.sleep(1)
            continue
        ip, user, svctime, method, status, uri, qstring = line.split("\t")
        # do not cache POST requests
        if method=="POST":
            log("POST", uri)
            continue
        # do not cache requests with a QUERY_STRING
        if qstring.startswith('?'): 
            log("QSTRING", uri)
            continue
        cachedir = docroot + uri
        # prevent attempts to get out of the cache
        if "/../" in cachedir:
            log("DOTDOT", uri)
            continue
        cachefile = cachedir + "/" + docfile
        tmpfile = cachefile + ".tmp"
        htaccess = cachedir + "/.htaccess"
        if os.path.isfile(cachefile): # check if we should refresh the file
            if isfresh(uri, time.time()-os.stat(cachefile).st_mtime):
                log("FRESH",uri)
                continue
            log("STALE",uri)
        else:
            log("MISS",uri)
        if not os.path.isdir(cachedir):
            os.makedirs(cachedir)
        log("FETCHING",uri)
        signal.alarm(backendtimeout)
        req = urllib.urlopen(backend+uri)
        if type(req)==type(0):
            log("EB%s"%req, uri)
            signal.alarm(0)
            continue
        hta = open(htaccess,"w")
        hta.write("ForceType %s\n"%req.info().type)
        hta.close()
        htd = open(tmpfile,"w")
        htd.write(req.read())
        htd.close()
        os.rename(tmpfile, cachefile)
        signal.alarm(0)
        log("FETCHED",uri)
        
def isfresh(uri, age):
    return age<300

if __name__=='__main__':
    execfile(sys.argv[1])
    syslog.openlog('rpx[%s]'%os.path.basename(sys.argv[1]))
    signal.signal(signal.SIGALRM, alarmhandler)
    if rpxlogfile:
        sys.stdout = open(rpxlogfile, "a")
    if rpxuser:
        uid = pwd.getpwnam(rpxuser).pw_uid
        gid = pwd.getpwnam(rpxuser).pw_gid
        if rpxlogfile:
            os.chown(rpxlogfile, uid, gid)
        os.setgid(gid)
        os.setuid(uid)
    while True:
        try:
            log("STARTING")
            rpx(apachelogfile,docroot,docfile,backend, backendtimeout, rpxlogfile)
        except KeyboardInterrupt:
            log("CTRL-C")
            sys.exit(0)
        except Exception, e:
            print e
            log("ERROR",str(e))
            syslog.syslog(syslog.LOG_ERR, str(e))
            log("SLEEPING")
            time.sleep(60)

