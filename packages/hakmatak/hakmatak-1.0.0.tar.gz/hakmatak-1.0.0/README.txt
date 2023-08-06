                             Hakmatak README

Hakmatak is a python implementation of the Webification (w10n) specification.

One basic idea of Webification is to make inner components of a data store
(composite file, database, etc.) directly addressable and accessible
via well-defined and meaningful URLs. A short tech note of w10n
is available as ./doc/w10n.txt. To learn more about w10n, please visit
http://w10n.org.

Hakmatak is usually installed on a web server to provide w10n service
via Web Server Gateway Interface (WSGI) or Common Gateway Interface (CGI).
It can also be used as a standalone library or a command line tool.
To install and configure Hakmatak, please read ./INSTALL.txt.

By design, Hakmatak is extensible for handling complex store types.
To extend Hakmatak, please read ./doc/dev.txt.
A list of available extensions is maintained at http://hakmatak.org.
