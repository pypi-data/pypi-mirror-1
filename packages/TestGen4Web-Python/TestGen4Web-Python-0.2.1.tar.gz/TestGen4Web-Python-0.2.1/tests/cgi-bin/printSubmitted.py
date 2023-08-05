#!/usr/bin/env python

import os
from cgi import FieldStorage
form = FieldStorage()

print "Content-Type: text/html\n"
print """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" 
   "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">"""
print "<html><head><title>Simple CGI: Print Submitted</title></head>\n"
print "<body>\n"
for key in form.keys():
    #if key != 'referrer':
    print "<p>For form field [%s], the value [%s] was obtained.<br /></p>" % (
            key, form.getvalue(key))

referrer = form.getvalue('referrer')
if referrer:
    print "<p><br/></p>\n"
    print "<p>"
    print '<a href="%s">Back to form</a>' % referrer
    print "...</p>\n"
    print "<p><br/></p>"
print "</body></html>\n"

