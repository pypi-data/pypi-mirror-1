#! /usr/bin/env python2
#
# Copyright (c) 2002 ekit.com Inc (http://www.ekit-inc.com/)
#
# See the README for full license details.
# 
# $Id: CGIInterface.py,v 1.4 2008/08/14 06:46:53 richard Exp $

import sys, os, cgi

from PerformanceTest import PerformanceTest

class CGIOptions:
    entries = (
        ('repeat', 1),
        ('threads', 4),
        ('username', None),
        ('password', None),
    )
    def __init__(self, form):
        for entry, default in self.entries:
            if entry in ('repeat', 'threads'):
                setattr(self, entry, int(form.getvalue(entry, default)))
            else:
                setattr(self, entry, form.getvalue(entry, default))

        if self.threads < 0: self.threads = 1
        if self.threads > 10: self.threads = 10
        if self.repeat < 0: self.repeat = 1
        if self.repeat > 10: self.repeat = 10


HEADER = '''<html>
<head><title>%s</title></head>
<body><h1>%s</h1>
'''
FOOTER = '\n</body></html>\n'
FORM = '''<form method="GET">
URL: <input size="40" name="url" value="%s"><br>
Repeats: <select name="repeat">
<option selected>1
<option>2
<option>3
<option>4
<option>5
<option>6
<option>7
<option>8
<option>9
<option>10
</select>
<br>
Threads: <select name="threads">
<option>1
<option>2
<option>3
<option selected>4
<option>5
<option>6
<option>7
<option>8
<option>9
<option>10
</select>
<br>
<input type="submit" value="Go">
</form>'''

def main():
    import cgitb
    out = sys.stdout
    err = sys.stderr
    try:
        if sys.platform == "win32":
            import os, msvcrt
            msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
        sys.stderr = sys.stdout
        realmain()
    except KeyboardInterrupt, SystemExit:
        raise
    except:
        sys.stdout, sys.stderr = out, err
        out.write('Content-Type: text/html\n\n')
        cgitb.handler()
    sys.stdout.flush()

def realmain():
    print "Content-Type: text/html\n"

    form = cgi.FieldStorage()
    options = CGIOptions(form)

    url = form.getvalue('url', '')
    if not url:
        print HEADER%('Performance measurement', 'Performance measurement')
        print FORM%''
    else:
        print HEADER%(url, url)
        test = PerformanceTest(options)
        test.GET(url)
        display_result(options, url, test)
        print '<hr>'
        print FORM%cgi.escape(url)
    print FOOTER

def display_result(options, furl, test):
    vres = []
    initial = 1
    for run in test.results:
        absstart = run[0][1]
        i = 0
        for url, start, first, end, status in run:
            if initial:
                this = [0, 0, 0, 0, url]
                vres.append(this)
            else:
                this = vres[i]
            if end is not None and first is not None:
                this[1] += start-absstart
                this[2] += first-start
                this[3] += end-start
            else:
                this[0] += 1
            i += 1
        initial = 0
    rlen = len(test.results)
    for res in vres:
        ok = rlen-res[0]
        if ok:
            res[1] /= ok
            res[2] /= ok
            res[3] /= ok

    ave_t = test.tot_t/test.n
    print '''
Number of runs: %s<br>
Number of threads: %s<br>
Total time: %.2f<br>
Note: results are an average if more than one run is performed.
<table border=1>
 <tr><th>bad</th><th>start</th><th>first</th><th>end</th><th>url</th></tr>
'''%(test.n, options.threads, ave_t)
    for ok, start, first, end, url in vres:
        if len(url) > 55:
            url = url[:10] + ' ... ' + url[-40:]
        print ''' <tr>
  <td>%d</td><td>%.2f</td><td>%.2f</td><td>%.2f</td><td>%s</td>
 </tr>'''%(ok, start, first, end, url)
    print '</table>'

if __name__ == '__main__':
    main()

#
# $Log: CGIInterface.py,v $
# Revision 1.4  2008/08/14 06:46:53  richard
# fixes
#
# Revision 1.3  2008/08/14 06:35:43  richard
# bug fix
#
# Revision 1.2  2002/08/27 23:37:38  richard
# Fixes and updates.
#
# Revision 1.1  2002/06/11 07:14:40  richard
# initial
#
#
# vim: set filetype=python ts=4 sw=4 et si
