#!/usr/bin/env python
# Tiny script for parsing nginx cache files / debugging caching problems
#
# Marek Kroemeke 2015
# http://kroemeke.eu/

import os
import struct
import binascii
import datetime
import sys
import re
import md5
from optparse import OptionParser

# extracted from ngx_http_cache.h
NGX_HTTP_CACHE_KEY_LEN  = 16
NGX_HTTP_CACHE_ETAG_LEN = 42
NGX_HTTP_CACHE_VARY_LEN = 42

# main cache file parsing happens here
class ngx_cache:
  def __init__(self,data):
    self.version = struct.unpack('i',data[0:4])[0]
    if self.version == 3:
      self.valid_sec, self.last_modified, self.date, self.crc32, self.valid_msec,self.header_start,self.body_start = struct.unpack('iiiIHHH',data[4:26])
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
# ngx_generate_cache_path('httplocalhost/','Accept-Encoding','gzip')
# ngx_generate_cache_path('httplocalhost/')
def ngx_generate_cache_path(key,vary=False,variant=False):
  key_md5 = md5.new()
  key_md5.update(key)
  if vary and variant:
    variant_md5 = md5.new()
    variant_md5.update(key_md5.digest())
    variant_md5.update(vary.lower())
    variant_md5.update(':')
    variant_md5.update(variant)
    variant_md5.update("\r\n")
    result = binascii.hexlify(variant_md5.digest())
  else:
    result = binascii.hexlify(key_md5.digest())
  return result[-1] + '/' + result[-3:-1] + '/' + result



# pretty printer of header data
def ngx_pretty_print(header,csv=False):
  if csv:
    print ','.join([str(header.version),
                   str(datetime.datetime.fromtimestamp(header.valid_sec)),
                   str(datetime.datetime.fromtimestamp(header.last_modified)),
                   str(datetime.datetime.fromtimestamp(header.date)),
                   str(header.crc32),
                   str(header.header_start),
                   str(header.body_start),
                   str(header.etag),
                   str(header.vary_len),
                   str(header.vary),
                   binascii.hexlify(header.variant),
                   header.key]) 
  else:
    print 'version      : ' + str(header.version)
    print 'valid_sec    : ' + str(datetime.datetime.fromtimestamp(header.valid_sec))
    print 'last_modified: ' + str(datetime.datetime.fromtimestamp(header.last_modified))
    print 'date         : ' + str(datetime.datetime.fromtimestamp(header.date))
    print 'crc32        : ' + str(header.crc32)
    print 'header_start : ' + str(header.header_start)
    print 'body_start   : ' + str(header.body_start)
    print 'etag         : ' + str(header.etag)
    print 'vary_len     : ' + str(header.vary_len)
    print 'vary         : ' + str(header.vary)
    print 'variant      : ' + binascii.hexlify(header.variant)
    print 'key          : ' + header.key
    print 'headers      : \n' + header.headers




# This function walks entire cache directory structure 
def walk(cachedir):
  for path, dirs, files in os.walk(cachedir):
    for filename in files:
      try:
        fd = open(os.path.join(path, filename),'rb')
        ngx_cache_file = ngx_cache(fd.read())
        ngx_pretty_print(ngx_cache_file,csv=True)
        #print os.path.join(path, filename) + ' ' + ngx_cache_file.key + ' variant: ' + binascii.hexlify(ngx_cache_file.variant)
      except:
        print 'Error while parsing ' + os.path.join(path, filename)
        continue



def main():
  usage = "usage: %prog [options] arg\n\n\t-k httplocalhost/ -V Accept-Encoding -v gzip\n"
  parser = OptionParser(usage,version="%prog 0.2")
  parser.add_option("-C","--cachedir",dest="cachedir",help="specify a non-default cache directory",default='/cache/nginx')
  parser.add_option("-k","--key",dest="key",help="calculate cache key hash/path",default=False)
  parser.add_option("-V","--vary",dest="vary",help="use with -k, but calculate variant for this header (eg. Accept-Encoding)",default=False)
  parser.add_option("-v","--variant",dest="variant",help="use with -k and -V, this is that value of varying header",default=False)
  parser.add_option("-f","--file",dest="file",help="parse only this header file",default=False)
  (options,args) = parser.parse_args()
  # calculate hash from key with vary header
  if options.key and options.vary and options.variant:
    print ngx_generate_cache_path(options.key,options.vary,options.variant)
  # calculate has from key
  elif options.key:
    print ngx_generate_cache_path(options.key)
  # dump everything we know about this file
  elif options.file:
    file   = open(options.file,'rb') 
    header = ngx_cache(file.read())
    ngx_pretty_print(header)
  else:
    walk(options.cachedir)


if __name__ == "__main__":
  main()
