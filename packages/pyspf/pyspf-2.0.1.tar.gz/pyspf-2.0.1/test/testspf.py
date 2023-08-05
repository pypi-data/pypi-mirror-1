# Author: Stuart D. Gathman <stuart@bmsi.com>
# Copyright 2006 Business Management Systems, Inc.

# This module is free software, and you may redistribute it and/or modify
# it under the same terms as Python itself, so long as this copyright message
# and disclaimer are retained in their original form.

# Run SPF test cases in the YAML format specified by the SPF council.

import unittest
import socket
import sys
import spf
import csv
import re
try:
  import yaml
except:
  print "yaml can be found at http://pyyaml.org/"
  print "Tested with PYYAML 3.04"
  raise

zonedata = {}
RE_IP4 = re.compile(r'\.'.join(
	[r'(?:\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])']*4)+'$')

def DNSLookup(name,qtype,strict=True):
  try:
    #print name
    timeout = True

    # emulate pydns-2.3.0 label processing
    a = []
    for label in name.split('.'):
      if label:
        if len(label) > 63:
          raise spf.TempError,'DNS label too long'
        a.append(label)
    name = '.'.join(a)

    for i in zonedata[name.lower()]:
      if i == 'TIMEOUT':
        if timeout:
	  raise spf.TempError,'DNS timeout'
	return
      t,v = i
      if t == qtype:
        timeout = False
      if v == 'TIMEOUT':
        if t == qtype:
	  raise spf.TempError,'DNS timeout'
	continue
      # keep test zonedata human readable, but translate to simulate pydns
      if t == 'AAAA':
	v = spf.inet_pton(v)
      yield ((name,t),v)
  except KeyError:
    if name.startswith('error.'):
      raise spf.TempError,'DNS timeout'

spf.DNSLookup = DNSLookup

class SPFTest(object):
  def __init__(self,testid,scenario,data={}):
    self.id = testid
    self.scenario = scenario
    self.explanation = None
    self.spec = None
    self.comment = []
    if 'result' not in data:
      print testid,'missing result'
    for k,v in data.items():
      setattr(self,k,v)
    if type(self.comment) is str:
      self.comment = self.comment.splitlines()

def getrdata(r):
  "Unpack rdata given as list of maps to list of tuples."
  txt = []	# generated TXT records
  gen = True
  for m in r:
    try:
      for i in m.items():
        t,v = i
        if t == 'TXT':
	  gen = False # no generated TXT records
	elif t == 'SPF' and gen:
	  txt.append(('TXT',v))
	if v != 'NONE':
	  yield i
    except:
      yield m
  if gen:
    for i in txt:
      yield i

class SPFScenario(object):
  def __init__(self,filename=None,data={}):
    self.id = None
    self.filename = filename
    self.comment = []
    self.zonedata = {}
    self.tests = {}
    if data:
      self.zonedata= dict([
        (d.lower(), list(getrdata(r))) for d,r in data['zonedata'].items()
      ])
      for t,v in data['tests'].items():
        self.tests[t] = SPFTest(t,self,v)
      if 'id' in data:
	self.id = data['id']
      if 'comment' in data:
        self.comment = data['comment'].splitlines()

  def addDNS(self,name,val):
    self.zonedata.setdefault(name,[]).append(val)

  def addTest(self,test):
    self.tests[test.id] = test

def loadYAML(fname):
  "Load testcases in YAML format.  Return map of SPFTests by name."
  fp = open(fname,'rb')
  tests = {}
  for s in yaml.safe_load_all(fp):
    scenario = SPFScenario(fname,data=s)
    for k,v in scenario.tests.items():
      tests[k] = v
  return tests

def loadBind(fname):
  "Load testcases in BIND format.  Return list of SPFTest"
  tests = {}
  scenario = SPFScenario(fname)
  comments = []
  lastdomain = None
  fp = open(fname,'rb')
  for a in csv.reader(fp,delimiter=' ',skipinitialspace=True):
    if not a:
      scenario = SPFScenario(fname)
      continue
    name = a[0].strip()
    if name.startswith('#') or name.startswith(';'):
      cmt = ' '.join(a)[1:].strip()
      comments.append(cmt)
      continue
    cmd = a[1].upper()
    if cmd == 'IN':
#example.com IN SPF "v=spf1 mx/26 exists:%{l}.%{d}.%{i}.spf.example.net -all"
      t = a[2].upper()
      if not name:
        name = lastdomain
      elif name.endswith('.'):
	name = name[:-1]
      lastdomain = name
      if t == 'MX':
	v = t,(int(a[3]),a[4].rstrip('.'))
      else:
	v = t,a[3]
      scenario.addDNS(name,v)
      if comments:
	scenario.comment += comments
	comments = []
    elif cmd == 'TEST':
      if not name:
        name = lastdomain
      else:
	lastdomain = name
      if name not in tests:
	tests[name] = test = SPFTest(name,scenario)
      else:
	test = tests[name]
      scenario.addTest(test)
      if comments:
	test.comment += comments
	comments = []
      t = a[2].lower()
      if RE_IP4.match(t):
        # fail TEST 1.2.3.4 lyme.eater@example.co.uk mail.example.net
	test.host,test.mailfrom,test.helo,test.result = a[2:6]
      elif t == 'mail-from':
        test.mailfrom = a[3]
      else:
        setattr(test,t,a[3])
  fp.close()
  return tests.values()

oldresults = { 'unknown': 'permerror', 'error': 'temperror' }

verbose = 0

class SPFTestCase(unittest.TestCase):

  def runTest(self,tests):
    global zonedata
    passed,failed = 0,0
    for t in tests:
      zonedata = t.scenario.zonedata
      q = spf.query(i=t.host, s=t.mailfrom, h=t.helo)
      q.set_default_explanation('DEFAULT')
      res,code,exp = q.check()
      if res in oldresults:
        res = oldresults[res]
      ok = True
      if res != t.result and res not in t.result:
        if verbose: print t.result,'!=',res
	ok = False
      elif res != t.result and res != t.result[0]:
        print "WARN: %s in %s, %s: %s preferred to %s" % (
		t.id,t.scenario.filename,t.spec,t.result[0],res)
      if t.explanation is not None and t.explanation != exp:
        if verbose: print t.explanation,'!=',exp
        ok = False
      if ok:
	passed += 1
      else:
	failed += 1
	print "%s in %s failed, %s" % (t.id,t.scenario.filename,t.spec)
	if verbose and not t.explanation: print exp
	if verbose > 1: print t.scenario.zonedata
    if failed:
      print "%d passed" % passed,"%d failed" % failed

  #def testMacro(self):
  #  self.runTests(loadBind('test/macro.dat'))

  #def testMailzone(self):
  #  self.runTests(loadBind('otest.dat'))

  def testYAML(self):
    self.runTest(loadYAML('test.yml').values())

  def testRFC(self):
    self.runTest(loadYAML('rfc4408-tests.yml').values())

def suite(): return unittest.makeSuite(SPFTestCase,'test')

if __name__ == '__main__':
  tc = None
  for i in sys.argv[1:]:
    if i == '-v':
      verbose += 1
      continue
    if not tc:
      tc = SPFTestCase()
      t = loadYAML('rfc4408-tests.yml')
    tc.runTest([t[i]])
  if not tc:
    unittest.main()
