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


It can also calculate hash for specific key, including hash for response with Vary header and 
specific variant in request : 


<pre>
dft:/home/nixon# ./ngcls.py -k httpwww.kroemeke.eu/css/kroemeke.css.old -V Accept-Encoding -v some_random_string 
6/5e/bf51c4f92daec8c80551241f43d265e6
dft:/home/nixon# ls -lash /cache/nginx/6/5e/bf51c4f92daec8c80551241f43d265e6
ls: cannot access /cache/nginx/6/5e/bf51c4f92daec8c80551241f43d265e6: No such file or directory
dft:/home/nixon# curl -H 'Accept-Encoding: some_random_string' http://www.kroemeke.eu/css/kroemeke.css.old -s -o /dev/null
dft:/home/nixon# ls -lash /cache/nginx/6/5e/bf51c4f92daec8c80551241f43d265e6
4.0K -rw------- 1 nginx nginx 1.3K Oct  9 15:59 /cache/nginx/6/5e/bf51c4f92daec8c80551241f43d265e6
dft:/home/nixon# ./ngcls.py -f /cache/nginx/6/5e/bf51c4f92daec8c80551241f43d265e6
version      : 3
valid_sec    : 2015-10-10 15:59:12
last_modified: 2014-02-18 17:48:10
date         : 2015-10-09 15:59:12
crc32        : 2683930437
header_start : 175
body_start   : 448
etag         : "154c004-32c-4f2b1e01d6a80"
vary_len     : 15
vary         : Accept-Encoding
variant      : bf51c4f92daec8c80551241f43d265e6
key          : httpwww.kroemeke.eu/css/kroemeke.css.old
headers      : 
HTTP/1.1 200 OK
Date: Fri, 09 Oct 2015 14:59:12 GMT
Server: Apache
Last-Modified: Tue, 18 Feb 2014 17:48:10 GMT
ETag: "154c004-32c-4f2b1e01d6a80"
Accept-Ranges: bytes
Content-Length: 812
Vary: Accept-Encoding
Connection: close
Content-Type: application/x-trash


dft:/home/nixon# 
</pre>
