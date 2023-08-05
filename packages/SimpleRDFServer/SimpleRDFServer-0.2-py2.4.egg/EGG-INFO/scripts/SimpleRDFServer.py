import os
import sys
import posixpath
import BaseHTTPServer
import urllib
import cgi
import shutil
import mimetypes
import xml.sax.saxutils
from StringIO import StringIO
from SimpleHTTPServer import *

class SimpleRDFRequestHandler(SimpleHTTPRequestHandler):
    """Override things to generate RDF."""
    if sys.argv[1:]:
        port = int(sys.argv[1])
    else:
        port = 8000

    myNS="http://localhost:"+str(port)

    def send_head(self):
        """
        Just like the original, but only serves custom index (does not map to index.html)
        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        self.send_header("Content-Length", str(os.fstat(f.fileno())[6]))
        self.end_headers()
        return f

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = StringIO()
	quotepath=urllib.quote(self.path)
#---Changes below -------------------------------------------------------
	f.write('<?xml version="1.0" encoding="utf-8"?>')
	#f.write('<?xml-stylesheet type="text/css" href="/rdf.css"?>\n')
	#f.write('<?xml-stylesheet type="text/xsl" href="/rdf.xsl"?>\n')
	f.write('<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/">')
        f.write('<channel rdf:about="%s">\n' % (self.myNS+quotepath))
        f.write('<title>%s</title>\n' % self.path)
        f.write('<link>%s</link>\n' % (self.myNS+quotepath))
        f.write('<description>%s</description>' % path)
        f.write('<image rdf:resource="http://xml.com/universal/images/xml_tiny.gif" />')
        f.write('<items>\n<rdf:Seq>\n')
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write('<rdf:li rdf:resource="%s" />\n'
                    % (self.myNS + urllib.quote(self.path) + urllib.quote(linkname)))
        f.write('</rdf:Seq>\n</items>\n</channel>\n')
        f.write('<image rdf:about="http://xml.com/universal/images/xml_tiny.gif">')
        f.write('<title>XML.com</title>')
        f.write('<link>http://www.xml.com/</link>')
        f.write('<url>http://xml.com/universal/images/xml_tiny.gif</url></image>')
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write('<item rdf:about="%s">\n' % ((self.myNS + urllib.quote(self.path) + urllib.quote(linkname))))
            f.write('<title>%s</title>\n' % cgi.escape(displayname))
            f.write('<link>%s</link>\n' % ((self.myNS + urllib.quote(self.path) + urllib.quote(linkname))))
            f.write('<description>%s</description>\n' % xml.sax.saxutils.escape(fullname))
            f.write('</item>')
        f.write("</rdf:RDF>\n")
#------------------------------------------------------------------------
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/xml")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f


def test(HandlerClass = SimpleRDFRequestHandler,
         ServerClass = BaseHTTPServer.HTTPServer):
    BaseHTTPServer.test(HandlerClass, ServerClass)

if __name__ == '__main__':
    test()


#winningham@gmail.com
