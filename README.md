# ngcls
Tiny script for parsing nginx cache header files

Work in progress on understanding how nginx's cache
works. http://kroemeke.eu/blog/2015/10/01/nginx-cache-file-format/

<pre>
dft:/cache/nginx/0/00# ngcls 9eacc540a431495f5ae408412e60f000 
version       : 3
valid_sec     : 1443784216 2015-10-02 12:10:16
last_modified : 1443559345 2015-09-29 21:42:25
date          : 1443697816 2015-10-01 12:10:16
etag          : "f3016c-6bb-520e8d9f88e40"
vary_len      : 15
vary          : Accept-Encoding
variant(md5)  : 9eacc540a431495f5ae408412e60f000
key           : httpkroemeke.eu/
HEADERS       : 
HTTP/1.1 200 OK
Date: Thu, 01 Oct 2015 11:10:16 GMT
Server: Apache
Last-Modified: Tue, 29 Sep 2015 20:42:25 GMT
ETag: "f3016c-6bb-520e8d9f88e40"
Accept-Ranges: bytes
Content-Length: 1723
Vary: Accept-Encoding
Cache-Control: proxy-revalidate
Connection: close
Content-Type: text/html
</pre>
