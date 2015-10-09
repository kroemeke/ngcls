#!/usr/bin/env python
# POC
# Tiny script for parsing nginx cache files
# POC
# Marek Kroemeke

import os
import struct
import binascii
import datetime
import sys
import re
import md5
from optparse import OptionParser

# ngx_http_cache.h
NGX_HTTP_CACHE_KEY_LEN  = 16
NGX_HTTP_CACHE_ETAG_LEN = 42
NGX_HTTP_CACHE_VARY_LEN = 42


class ngx_cache:
  def __init__(self,data):
    self.version = struct.unpack('i',data[0:4])[0]
    if self.version == 3:
      ( self.valid_sec,         self.last_modified,         self.date,         self.crc32,         self.valid_msec,         self.header_start ,        self.body_start ) = struct.unpack('iiiIHHHB',data[4:27])

      self.etag          = data[27:27+NGX_HTTP_CACHE_ETAG_LEN]
      self.vary_len      = struct.unpack('B',data[27+NGX_HTTP_CACHE_ETAG_LEN])[0]
      self.vary          = data[27+NGX_HTTP_CACHE_ETAG_LEN+1:\
                              27+NGX_HTTP_CACHE_ETAG_LEN+1+NGX_HTTP_CACHE_VARY_LEN]
      self.variant       = data[27+NGX_HTTP_CACHE_ETAG_LEN+1+NGX_HTTP_CACHE_VARY_LEN:\
                             27+NGX_HTTP_CACHE_ETAG_LEN+1+NGX_HTTP_CACHE_VARY_LEN+NGX_HTTP_CACHE_KEY_LEN]
      self.raw_response  = data[27+NGX_HTTP_CACHE_ETAG_LEN+1+NGX_HTTP_CACHE_VARY_LEN+NGX_HTTP_CACHE_KEY_LEN:]
      self.key           = self.raw_response.splitlines()[1][5:]
      self.headers       = data[self.header_start:self.body_start]
    else:
      raise ValueError
  def body(self):
    return data[27+NGX_HTTP_CACHE_ETAG_LEN+1+NGX_HTTP_CACHE_VARY_LEN+\
                NGX_HTTP_CACHE_KEY_LEN:][self.body_start:]
 

# This function can generate cache file path 
def ngx_generate_cache_path(key,vary,variant):
  key_md5 = md5.new()
  key_md5.update(key)
  variant_md5 = md5.new()
  variant_md5.update(key_md5.digest())
  variant_md5.update(vary.lower())
  variant_md5.update(':')
  variant_md5.update(variant)
  variant_md5.update("\r\n")
  result = binascii.hexlify(variant_md5.digest())
  return result[-1] + '/' + result[-3:-1] + '/' + result


#file = open(sys.argv[1],'rb')
#h = file.read()
#
#foo = ngx_cache(h)
#print 'version       : ' + str(foo.version)
#print 'valid_sec     : ' + str(foo.valid_sec) + ' ' + str(datetime.datetime.fromtimestamp(foo.valid_sec))
#print 'last_modified : ' + str(foo.last_modified) + ' ' + str(datetime.datetime.fromtimestamp(foo.last_modified))
#print 'date          : ' + str(foo.date) + ' ' + str(datetime.datetime.fromtimestamp(foo.date))
#print 'etag          : ' + foo.etag
#print 'vary_len      : ' + str(foo.vary_len)
#print 'vary          : ' + foo.vary
#print 'variant(md5)  : ' + binascii.hexlify(foo.variant)
#print 'key           : ' + foo.key
#print 'HEADERS       : ' 
#print foo.headers

def walk(cachedir):
  for path, dirs, files in os.walk(cachedir):
    for filename in files:
      try:
        fd = open(os.path.join(path, filename),'rb')
        ngx_cache_file = ngx_cache(fd.read())
        print os.path.join(path, filename) + ' ' + ngx_cache_file.key + ' variant: ' + binascii.hexlify(ngx_cache_file.variant)
      except:
        continue

def main():
  usage = "usage: %prog [options] arg\n\n\tIF YOU HAVE HUGE CACHE - BE CAREFUL (load++)\n"
  parser = OptionParser(usage,version="%prog 0.2")
  parser.add_option("-C","--cachedir",dest="cachedir",help="specify a non-default cache directory",default='/cache/nginx')
  (options,args) = parser.parse_args()
  walk(options.cachedir)


if __name__ == "__main__":
  main()
