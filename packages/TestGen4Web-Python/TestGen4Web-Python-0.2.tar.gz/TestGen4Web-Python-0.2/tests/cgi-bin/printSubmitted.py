#!/usr/bin/env python

from cgi import FieldStorage
form = FieldStorage()

print "Content-Type: text/html\n"
print "<html><head><title>Simple CGI: Print Submitted</title></head>\n"
print "<body>\n"
for key in form.keys():
    print "For form field [%s], the value [%s] was obtained.<br />" % (
        key, form.getvalue(key))
print "</body></html>\n"

