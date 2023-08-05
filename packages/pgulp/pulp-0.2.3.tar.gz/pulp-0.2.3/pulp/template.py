#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
# (c) 2007 Andreas Kostyrka
#
"""Verfügbarkeit eines Users setzen."""

import urllib2, errors, urllib, datetime, sys, fnmatch, operator
from pulp.config import main as pulpconfig

def extractData(data, start, end, optional=False, label=None):
    if label is None:
        label = "Unexpected Page change: %r/%r" % (start, end)
    spos = data.find(start)
    if spos == -1:
        if optional:
            return (None, None)
        else:
            raise errors.RemoteChangedError(label + "(start missing)")
    epos = data.find(end, spos)
    if epos == -1:
        if optional:
            return (None, None)
        else:
            raise errors.RemoteChangedError(label + "(end missing)")
    spos += len(start)
    return (spos, epos)

def extractAll(data, start, end):
    res = []
    while data:
        spos, epos = extractData(data, start, end, optional=True)
        if spos is None:
            break
        res.append(data[spos:epos])
        data = data[(epos + len(end)):]
    return res

def lookupData(data, key):
    res = []
    for name, value in data:
        if value == key:
            return [(name, value), ]
        if fnmatch.fnmatch(name.upper(), key.upper()):
            res.append((name, value))
    return res

def singletonOrList(result, label):
    if not result:
        print >>sys.stderr, "No data for %s" % (label, )
        raise SystemExit(3)
    if len(result) == 1:
        return result[0][1]
    else:
        width = max(len(i) for i in result)
        for name, value in result:
            print >>sys.stderr, "%s:%*s:%s" % (label, width, value, name)
        raise SystemExit(3)

def getFormdata(username, password):
    res = dict()
    # Create an OpenerDirector with support for Basic HTTP Authentication...
    auth_handler = urllib2.HTTPBasicAuthHandler()
    auth_handler.add_password('Freiberufler Bereich', 'www.gulp.de', username, password)
    myweb = urllib2.build_opener(auth_handler)

    lreq = myweb.open('https://www.gulp.de/edit/GulpEdit.exe/GETWORDEXPORT')
    login = lreq.read()
    open("/tmp/login.html", "w").write(login)

    prefix = "/edit/GulpEdit.exe/showexportprofil?"

    pos = login.find(prefix)
    if pos == -1:
        raise errors.RemoteChangedError("Profile export page changed layout! Error: [PEPCL1]")
    epos = login.find('"', pos)
    if epos == -1:
        raise errors.RemoteChangedError("Profile exporgt page changed layout! Error: [PEPCL2]")
    res['action'] = "https://www.gulp.de" + login[pos:epos]
    cids, cide = extractData(login, '<select name="cid" id="cid">', '</select>')
    cid = login[cids:cide].strip()
    cid_list = [tuple(reversed(x.replace(" selected", "").split('">'))) for x in extractAll(cid, '<option value="', '</option>') if not x.startswith('0">')]
    res['cid'] = cid_list

    mids, mide = extractData(login, '<select name="mid" id="mid">', '</select>')
    mid = login[mids:mide].strip()
    mid_list = [tuple(reversed(x.replace(" selected", "").split('">'))) for x in extractAll(mid, '<option value="', '</option>')]
    res['mid'] = mid_list

    return res

def downloadProfil(username, password, mid, cid, showName, showMoney):
    data = dict(cid=cid, mid=mid)
    if showName:
        data["showName"] = "1"
    if not showMoney:
        data["noMoney"] = "1"
    auth_handler = urllib2.HTTPBasicAuthHandler()
    auth_handler.add_password('Freiberufler Bereich', 'www.gulp.de', username, password)
    myweb = urllib2.build_opener(auth_handler)
    fdata = getFormdata(username, password)
    datas = urllib.urlencode(data)
    res = myweb.open(fdata['action'], datas)
    return res.read()

def parser():
    import optparse
    p = optparse.OptionParser(usage="usage: %prog template [options] >profil.doc [nur für zahlende members]")
    p.add_option("--username",
                 default=pulpconfig.get("pulp", "username", default=None),
                 help="GULP Username, notwendig")
    p.add_option("--password",
                 default=pulpconfig.get("pulp", "password", default=None),
                 help="GULP Passwort, notwendig")
    p.add_option("--list",
                 action="store_true",
                 default=False,
                 help=u"Verfügbare Templates listen")
    p.add_option("--template",
                 default=None,
                 help=u"Template verwenden, integer oder glob pattern.")
    p.add_option("--language",
                 default=None,
                 help=u"Sprache, integer oder glob pattern.")
    p.add_option("--showname",
                 action="store_true",
                 default=False,
                 help=u"Namen (falls möglich) exportieren")
    p.add_option("--showmoney",
                 action="store_true",
                 default=False,
                 help=u"Stundensatz (falls möglich) exportieren")
    return p
    
def main():
    p = parser()
    opt, args = p.parse_args()
    if len(args) != 0 or opt.username is None or opt.password is None:
        p.print_help()
        raise SystemExit(2)
    data = getFormdata(opt.username, opt.password)
    if opt.list:
        width = max(len(i) for i in data['cid'])
        for name, value in sorted(data['cid'], key=operator.itemgetter(0)):
            print "template:%*s:%s" % (width, value, name)
        width = max(len(i) for i in data['mid'])
        for name, value in data['mid']:
            print "language:%*s:%s" % (width, value, name)
    else:
        mid = None
        if opt.language is None:
            mid = data['mid'][0][1]
        else:
            mid = singletonOrList(lookupData(data['mid'], opt.language), 'language')
        if opt.template is None:
            cid = -1
        else:
            cid = singletonOrList(lookupData(data['cid'], opt.template), 'template')
        sys.stdout.write(downloadProfil(opt.username, opt.password, mid, cid, opt.showname, opt.showmoney))
        

if __name__ == '__main__':
    import sys
    print getFormdata(*sys.argv[1:])

    
