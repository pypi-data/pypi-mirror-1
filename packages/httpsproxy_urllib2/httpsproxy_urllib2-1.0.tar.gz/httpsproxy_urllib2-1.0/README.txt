Python 2.5 urllib2 patched to use CONNECT for https proxies
-----------------------------------------------------------

This package contains the python 2.5 urllib2 and httplib modules patched to 
correctly use the CONNECT method to establish a connection to a HTTPS server
over a proxy server. The urllib2 module has also been made compatible with
python 2.4 (hashlib replaced with sha and md5 modules)

* The patch was downloaded from http://bugs.python.org/issue1424152
* urllib2.py is r62464 from the python2.5 maintenance branch
* httplib.py is r60748 from the python2.5 maintenance branch
