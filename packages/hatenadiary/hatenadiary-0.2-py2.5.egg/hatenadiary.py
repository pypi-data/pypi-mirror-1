#!/usr/bin/env python
# -*- coding: utf-8 -*-
# http://d.hatena.ne.jp/keyword/%a4%cf%a4%c6%a4%ca%a5%c0%a5%a4%a5%a2%a5%ea%a1%bcAtomPub

import base64
import random
import urllib
import httplib
import re
import datetime
from urlparse import urlsplit
from xml.dom import minidom

try:
  from hashlib import sha1 as sha
  def sha_(args):
    return sha(args)
except:
  import sha
  def sha_(args):
    return sha.new(args)

class _JST(datetime.tzinfo):
  def utcoffset(self, dt):
    return datetime.timedelta(hours=9)
  
  def dst(self, dt):
    return datetime.timedelta(0)

  def tzname(self, dt):
    return '+09:00'

class _WSSE :
  def __init__(self, userid, passwd):
    self.userid = userid
    self.passwd = passwd

  def get_nonce(self):
    private = str(random.random())
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y-%m-%dT%H:%M:%SZ')
    return '%s %s' % (timestamp, sha_('%s:%s' % (timestamp, private)).hexdigest())

  def get_wsse(self):
    nonce = self.get_nonce()
    base64_encoded_nonce = base64.encodestring(nonce).replace('\n', '')
    now = datetime.datetime.now()
    post_creation_time = now.strftime('%Y-%m-%dT%H:%M:%SZ')
    password_digest = base64.encodestring(sha_(nonce + post_creation_time + self.passwd).digest()).replace('\n', '')
    return 'UsernameToken Username="%s", PasswordDigest="%s", Created="%s", Nonce="%s"' \
           % (self.userid, password_digest, post_creation_time, base64_encoded_nonce)

class HatenaDiary:

  def __init__(self, userid, passwd):
    self.userid = userid
    self.passwd = passwd
    self.url = 'http://d.hatena.ne.jp/%s/atom/' % userid
        
  def post(self, title, text, date=datetime.datetime.now(), isDraft=False):
    url = self.url + 'draft' if isDraft else self.url + 'blog'
    entry = self._convert_entry(title, text, date)
    return self._parse_entry(minidom.parse(self._open('POST',url,entry)))

  def put(self, url, title, text, date=datetime.datetime.now()):
    entry = self._convert_entry(title, text, date)
    return self._parse_entry(minidom.parse(self._open('PUT',url,entry)))

  def _get(self, pager=0, isDraft=False):
    url = self.url + 'draft' if isDraft else self.url + 'blog'
    if pager:
      url = url + '?page=%s' % pager
    return self._open('GET', url)

  def get(self, pager=0, isDraft=False):
    data = []
    return self._parse_entry(minidom.parse(self._get(pager,isDraft)))

  def _service(self):
    return self._open('GET', self.url)
    
  def service(self):
    dom = minidom.parse(self._service())
    data = {}
    for node in dom.getElementsByTagName('collection'):
      href = node.getAttribute('href') 
      key = href.split('/atom/')[1]
      data[key] = {}
      data[key]['url'] = href
      title = self._get_node_value(node,'atom:title')
      data[key]['title'] = title
    return data
    
  def delete(self,url):
    return self._open('DELETE',url)

  def publish(self,url):
    dom = minidom.parse(self._open('PUT',url,header={'X-HATENA-PUBLISH':1}))
    return self._parse_entry(dom)

  def _parseRFC3339(self, string):
    value = re.findall(r'(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+)([\+-])(\d+):(\d+)',string)[0]
    if len(value) != 9:
      return None
    date_ = datetime.datetime(*map((lambda x: int(x)),value[0:6]))
    if value[6] == '+' and value[7] == '09':
      date_ =  date_.replace(tzinfo=_JST())
    return date_

  def _convert_entry(self, title, text, date):
    if isinstance(title, unicode): title = title.encode("utf-8")
    if isinstance(text, unicode): text = text.encode("utf-8")
    if not date.tzinfo:
      date.replace(tzinfo=_JST())
    date_ = date.strftime('%Y-%m-%dT%H:%M:%S%Z')
    entry = '''<?xml version="1.0" encoding="utf-8"?>
    <entry xmlns="http://purl.org/atom/ns#">
    <title><![CDATA[%s]]></title>
    <content type="text/plain"><![CDATA[%s]]></content>
    <updated>%s</updated>
    </entry>
    ''' % (title, text, date_)
    return entry

  def _parse_entry(self, dom):
    data = []
    for node in dom.getElementsByTagName('entry'):
      url = node.getElementsByTagName('link')[0].getAttribute('href')
      published = self._parseRFC3339(self._get_node_value(node, 'published'))
      updated = self._parseRFC3339(self._get_node_value(node, 'updated'))
      title = self._get_node_value(node,'title')
      content = self._get_node_value(node,'content')
      hatena_syntax = self._get_node_value(node,'hatena:syntax')
      data.append({'url':url,
              'published':published,
              'updated':updated,
              'title':title,
              'content':content,
              'hatena:syntax':hatena_syntax})
    return data

  def _get_node_value(self,dom,tag_name):
    node = dom.getElementsByTagName(tag_name)
    if node and node[0].firstChild:
      return node[0].firstChild.nodeValue
    return None

    
  def _open(self, method, url, body=None,header=None):
    header_info = {'X-WSSE': _WSSE(self.userid, self.passwd).get_wsse(),
                   'User-Agent': 'yoshiori\'s test(yoshiori@gmail.com'}
    if header:
      header_info = dict(header_info,**header)
      
    host, path, query = urlsplit(url)[1:4]
    conn = httplib.HTTPConnection(host)
    path = path if query else path + '?' + query
    conn.request(method,path,body,header_info)
    r = conn.getresponse()
    if not (200 <= r.status < 300):
      raise Exception('status = ' + str(r.status),
                      'msg = ' + r.msg,
                      'body = ' + r.read())
    return r
        
if __name__ == '__main__':
  pass

