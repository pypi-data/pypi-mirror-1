from __future__ import with_statement, absolute_import

import os, sys, cgi, cgitb, StringIO
import subnetviz.network, subnetviz.format
import subnetviz.format.html as html

# FIXME: This quick-and-dirty CGI program is not very RESTful--it
# should be accepting a representation of a labelled network in the
# URI, not in a POSTed form document.  This current design makes
# saving and sharing results impossible.  Although URIs don't have a
# limit to their length, Apache and MSIE both limit URIs to about 2 or
# 4KB, which is too little for encoding some networks, even if the
# encoded form is compressed.  Therefore, we'd have to make this CGI
# script stateful (e.g. SQL-based) in order to represent labelled
# networks within 2KB, and that's just a drag.

def main ():
    cgitb.enable ()
    fields = cgi.FieldStorage ()
    in_s = fields["ip_table"].value if fields.has_key ("ip_table") else EXAMPLE
    addrs = subnetviz.network.read_addresses (StringIO.StringIO (in_s))
    net = subnetviz.network.network_tree (addrs)
    net = subnetviz.format.prune_tree (net)
    net.offset = net.depth = 0
    subnetviz.format.annotate (net)
    table = html.build_table (net)
    out_f = sys.stdout
    out_f.write ("Content-Type: text/html\r\n")
    out_f.write ("\r\n")
    out_f.write ("<html><head>")
    out_f.write ("<title>%s</title>" %
                (html.html_encode_text (html.page_title (net)),))
    out_f.write ("<link rel='stylesheet' href='style.css'>")
    out_f.write ("</head>")
    out_f.write ("<body>")
    skip_root = net.label is None and len (net.children) > 0
    html.print_table (table, out_f, html.format_net, skip_root)
    out_f.write ("<hr>")
    out_f.write ("<form action='%s' method='POST'>" % ("",))
    out_f.write ("<div><textarea name='ip_table' cols='100' rows='25'>")
    out_f.write (html.html_encode_text (in_s))
    out_f.write ("</textarea></div>")
    for para_s in subnetviz.network.input_format_description.split ("\n\n"):
        out_f.write ("<p>%s</p>" % (html.html_encode_text (para_s),))
    out_f.write ("<div><input type='submit' value='Show IP Tree'></div>")
    out_f.write ("</form></body></html>")

EXAMPLE = \
"""2002:c6ca:19fb::/48             thoughtcrime.us IPv6 address space
  2002:c6ca:19fb::/64           6to4 tunnel address PTP
    2002:c6ca:19fb::1           Apogiffa
  2002:c6ca:19fb:1::/64         Public
    2002:c6ca:19fb:1::1         Apogiffa
    2002:c6ca:19fb:1::2         Reserved for wireless AP
    2002:c6ca:19fb:1::3         Oomingmak
  2002:c6ca:19fb:40::/58        Apogiffa-connected PTPs
    2002:c6ca:19fb:40::/64      Utopia Planitia PTP
      2002:c6ca:19fb:40::1      Apogiffa
    2002:c6ca:19fb:41::/64      Spitfire PTP
      2002:c6ca:19fb:41::1      Apogiffa
  2002:c6ca:19fb:800::/53       Turing subnets
    2002:c6ca:19fb:800::/64     Turing PTP
      2002:c6ca:19fb:800::1     Apogiffa
      2002:c6ca:19fb:800::2     Turing
    2002:c6ca:19fb:801::/64     Blue Lines PTP
      2002:c6ca:19fb:801::1     Turing
      2002:c6ca:19fb:801::2     Blue Lines
    2002:c6ca:19fb:802::/64     Dialogues PTP
      2002:c6ca:19fb:802::1     Turing
    2002:c6ca:19fb:803::/64     Ophelia PTP
      2002:c6ca:19fb:803::1     Turing
    2002:c6ca:19fb:804::/64     Synthetic Forms PTP
      2002:c6ca:19fb:804::1     Turing
    2002:c6ca:19fb:805::/64     Bombat PTP
      2002:c6ca:19fb:805::1     Turing
    2002:c6ca:19fb:806::/64     Wet Blanket PTP
      2002:c6ca:19fb:806::1     Turing
    2002:c6ca:19fb:807::/64     Rhythm of Time PTP
      2002:c6ca:19fb:807::1     Turing
    2002:c6ca:19fb:808::/64     Elation Station PTP
      2002:c6ca:19fb:808::1     Turing
    2002:c6ca:19fb:809::/64     Substance PTP
      2002:c6ca:19fb:809::1     Turing
      2002:c6ca:19fb:809::2     Substance (public nameserver)
      2002:c6ca:19fb:809::3     Substance (private nameserver)
    2002:c6ca:19fb:80a::/64     Soft Power PTP
      2002:c6ca:19fb:80a::1     Turing
    2002:c6ca:19fb:80b::/64     Number 41 PTP
      2002:c6ca:19fb:80b::1     Turing
    2002:c6ca:19fb:80c::/64     Jagged Little Pill PTP
      2002:c6ca:19fb:80c::1     Turing
    2002:c6ca:19fb:80d::/64     Lazy Calm PTP
      2002:c6ca:19fb:80d::1     Turing
    2002:c6ca:19fb:80e::/64     Gemini PTP
      2002:c6ca:19fb:80e::1     Turing
    2002:c6ca:19fb:80f::/64     The War Won PTP
      2002:c6ca:19fb:80f::1     Turing
    2002:c6ca:19fb:811::/64     Lush-3 PTP
      2002:c6ca:19fb:811::1     Turing
  2002:c6ca:19fb:8000::/49      (Reserved)
"""
if __name__ == "__main__":
    sys.exit (main ())
