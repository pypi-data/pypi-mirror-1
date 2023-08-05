#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
# (c) 2007 Andreas Kostyrka
#
"""Verfügbarkeit eines Users setzen."""

import urllib2, errors, urllib, datetime, sys
from pulp.config import main as pulpconfig

def setAvailability(username, password, datum, avail, vorort):
    assert 0 <= avail <= 100
    assert 0 <= vorort <= 100
    # Create an OpenerDirector with support for Basic HTTP Authentication...
    auth_handler = urllib2.HTTPBasicAuthHandler()
    auth_handler.add_password('Freiberufler Bereich', 'www.gulp.de', username, password)
    myweb = urllib2.build_opener(auth_handler)

    lreq = myweb.open('https://www.gulp.de/edit/GulpEdit.exe/GPWD')
    login = lreq.read()

    prefix = "/edit/GulpEdit.exe/QSAVAILABLE?"

    pos = login.find(prefix)
    if pos == -1:
        raise errors.RemoteChangedError("Login page changed layout! Error: [LPCL1]")
    epos = login.find('"', pos)
    if epos == -1:
        raise errors.RemoteChangedError("Login page changed layout! Error: [LPCL2]")
    action = "https://www.gulp.de" + login[pos:epos]
    data = dict(availabledat=str(datum),
                prozavailable=str(avail),
                prozvorort=str(vorort))
    result = myweb.open(action, urllib.urlencode(data))
    return "Ihr Verf&uuml;gbarkeit wurde gespeichert." in result.read()

def parser():
    import optparse
    p = optparse.OptionParser(usage="usage: %prog avail [options] datum")
    p.add_option("--username",
                 default=pulpconfig.get("pulp", "username", default=None),
                 help="GULP Username, notwendig")
    p.add_option("--password",
                 default=pulpconfig.get("pulp", "password", default=None),
                 help="GULP Passwort, notwendig")
    p.add_option("--avail",
                 type="int",
                 default=100,
                 help=u"Prozent Verfügbarkeit, default=100%")
    p.add_option("--vorort",
                 type="int",
                 default=100,
                 help=u"Prozent Verfügbarkeit, default=100%")
    return p
    
def main():
    p = parser()
    opt, args = p.parse_args()
    if len(args) != 1 or opt.username is None or opt.password is None:
        p.print_help()
        raise SystemExit(2)
    try:
        date = datetime.datetime.strptime(args[0], "%d.%m.%Y").date()
    except ValueError:
        print >>sys.stderr, "Bitte Datum im Format DD.MM.JJJJ angeben."
        p.print_help()
        raise SystemExit(2)
        
    res = setAvailability(opt.username, opt.password, date.strftime("%d.%m.%Y"), opt.avail, opt.vorort)
    if not res:
        print u"Verfügbarkeit nicht gesetzt!"
        raise SystemExit(3)

if __name__ == '__main__':
    import sys
    print setAvailability(*(sys.argv[1:4] + [int(sys.argv[4]), int(sys.argv[5])]))

    
