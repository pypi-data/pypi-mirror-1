# -*- coding: utf-8 -*-

import sys
import os
import re
import md5
import urllib2
import datetime
import hinagiku
import yaml
from dateutil.tz import *
from dateutil.parser import parse
from genshi.template import MarkupTemplate

class Hinagiku:
  def __init__(self, config_path=None, template_path=None, output_path=None):
    self.flag = dict()
    self.config_path = config_path or "config.yaml"
    if os.path.isfile(self.config_path):
      config = open(self.config_path).read()
      self.config = yaml.load(config)
    else:
      sys.exit("Configure file is not found.")
    self.template_path = template_path or "template.xml"
    if os.path.isfile(self.template_path):
      template = open(self.template_path)
      self.template = MarkupTemplate(template)
    else:
      sys.exit("Template file is not found")
    self.output_path = output_path or "output.xml"
    self.output = list()
    self.cache_path = "cache.yaml"
    if os.path.isfile(self.cache_path):
      cache = open(self.cache_path)
      self.cache = yaml.load(cache)
    else:
      self.cache = dict()
    self.ignore_pattern = dict()
    self.user_agent = "Hinagiku/%s" % hinagiku.__version__

  def run(self):
    self.crawl()
    self.out()

  def crawl(self):
    for page in self.config:
      d = dict()
      uri = page["check"]
      if page.get("ignore"):
        self.ignore_pattern[uri] = page["ignore"]
      date = self.get_last_modified(uri)
      d["uri"] = page.get("link") or page["check"]
      d["title"] = page["title"]
      d["author"] = page["author"]
      if date:
        d["date"] = date
      self.output.append(d)

  def out(self):
    writer = lambda file, value: open(file, "w").write(value)
    writer(self.cache_path, yaml.dump(self.cache, default_flow_style=False))
    self.output.sort(lambda x, y: cmp(x.get("date"), y.get("date")))
    self.output.reverse()
    writer(self.output_path, self.template.generate(pages=self.output).render())

  def get_last_modified(self, uri):
    d = self.cache.get(uri) or dict()
    opts = dict()
    req = urllib2.Request(uri)
    req.add_header("User-Agent", self.user_agent)
    if d.has_key("etag"):
      req.add_header("If-None-Match", d["etag"])
    if d.has_key("last_modified"):
      req.add_header("If-Modified-Since", d["last_modified"])
    try:
      page = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
      status = e.code
      d["status"] = status
    except urllib2.URLError:
      d["ststus"] = "None"
    else:
      headers = page.headers
      etag = headers.getheader("ETag")
      if etag:
        d["etag"] = etag
      last_modified = headers.getheader("Last-Modified")
      if last_modified:
        last_modified = parse(last_modified)
        last_modified = last_modified.isoformat()
        d["last_modified"] = last_modified
      else:
        body = page.read()
        if self.ignore_pattern.get(uri):
          pattern = self.ignore_pattern[uri]
          body = self.ignore_text(body, pattern)
        body = md5.new(body).hexdigest()
        if not body == d.get("body"):
          date = datetime.datetime.now(tzutc())
          date = date.isoformat()
          d["last_modified"] = date
          d["body"] = body
      d["status"] = page.code
    self.cache[uri] = d
    return d.get("last_modified")

  def ignore_text(self, body, pattern):
    pattern = re.compile(pattern)
    return pattern.sub("", body)
