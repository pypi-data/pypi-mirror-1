# $Id: escapes.py,v 1.1.1.1 2006/01/12 20:54:39 classic Exp $
# escapes.py - string escaping functions for Myghty
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
# Original Perl code and documentation copyright (c) 1998-2003 by Jonathan Swartz. 
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#


import re, cgi, urllib, htmlentitydefs, StringIO

xml_escapes = {
    '&' : '&amp;',
    '>' : '&gt;', 
    '<' : '&lt;', 
    '"' : '&#34;',   # also &quot; in html-only
    "'" : '&#39;'    # also &apos; in html-only    
}

def html_escape(string):
    return cgi.escape(string, True)

def xml_escape(string):
    return re.sub(r'([&<"\'>])', lambda m: xml_escapes[m.group()], string)

def url_escape(string):
    # convert into a list of octets
    string = string.encode("utf8")
    return urllib.quote_plus(string)

def url_unescape(string):
    return urllib.unquote_plus(string)
    
    
def html_entities_escape(string):
    buf = StringIO.StringIO()
    for c in unicode(string):
        try:
            buf.write("&" + htmlentitydefs.codepoint2name[c] + ";")
        except KeyError:
            buf.write(c)
            
    return buf.getvalue().encode("ASCII", "ignore")

    

