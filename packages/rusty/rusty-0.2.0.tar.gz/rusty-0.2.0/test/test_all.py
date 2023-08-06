# -*- coding: utf-8 -*-
# :tabSize=2:indentSize=2:noTabs=true:
import random
import unittest
import os
import tempfile
import difflib
from pprint import pprint

from BeautifulSoup import BeautifulStoneSoup

from rusty import xmltable, includesh

class XMLTableTestCase(unittest.TestCase):
  '''
  Unittest class for :class:`XMLTable`
  '''
  def setUp(self):
    doc = os.path.join(os.path.dirname(__file__), 'data/document.xml')
    self.xt = xmltable.Query(path=doc)

  def test_attrib(self):
    # Existing attribute
    self.assertQueryLen(self.xt.query('/root/items/item@name'), 1)

    # Non-existing attribute
    self.assertQueryLen(self.xt.query('/root/items/item@hur'), 0)

  def test_absolute(self):

    for q in self.xt.query('/root/items'):
      print '-'*50
      for item in q.query('item@name'):
        if item:
          print '[name] %s' % item['name']
          print '#'*50

    self.assertQueryLen(self.xt.query('/root/items/item'), 2)
    self.assertQueryLen(self.xt.query('root/items/item'), 0)
    self.assertQueryLen(self.xt.query('/items/item'), 0)

  def assertQueryLen(self, qiterator, length):
    self.assertEqual(len(list(qiterator)), length)


class XMLTableTestCase(unittest.TestCase):
  '''
  Unittest class for :class:`XMLTable`
  '''
  def setUp(self):
    '''
    Create required initializations
    '''
    doc = os.path.join(os.path.dirname(__file__), 'data/document.xml')
    self.bs = BeautifulStoneSoup(file(doc))

  def test_select(self):
    '''
    '''
    item = self.bs.root.items.find('item', attrs = {'name':'hur'})
    self.assertEqual(str(item.string), 'value2')


class ShellConverterTestCase(unittest.TestCase):
  '''
  Runs test on shell converter
  '''
  def setUp(self):
    '''
    Test initialization
    '''
    spath = os.path.join(os.path.dirname(__file__), 'data/script.sh')
    cpath = os.path.join(os.path.dirname(__file__), 'data/script.rst')

    tfd, tpath = tempfile.mkstemp(prefix='rustytest-')

    self.source = open(spath, 'r+b')
    self.target = open(tpath, 'w+b')
    self.comp = open(cpath, 'r+b')

    self.sc = includesh.ShellConverter(spath)

  def tearDown(self):
    '''
    '''
    self.source.close()
    self.target.close()
    self.comp.close()

  def test_convert(self):
    '''
    Tests the ``to_rst`` method
    '''
    output_path = self.sc.to_rst()
    print output_path

    fromlines = open(output_path, 'U').readlines()
    tolines = open(self.comp.name, 'U').readlines()

    for line in fromlines:
      print line.replace('\n',  '')

    #diff = difflib.unified_diff(fromlines, tolines)
    # TODO: find out a better way to check results
    #pprint(list(diff))

class IncludeShellTestCase(unittest.TestCase):
  '''
  Runs test on includeshell directive tests
  '''
  def setUp(self):
    '''
    Test initialization
    '''
    self.dir = os.path.dirname(__file__)
    doc_path = os.path.join(self.dir, 'data/includesh.rst')

    self.tmp_dir = tempfile.mkdtemp(prefix='rustytest-')

    self.doc = open(doc_path, 'r+b')

  def tearDown(self):
    '''
    '''
    self.doc.close()

  def test_convert(self):
    # TODO: Find a pythonic way to do this
    dpath = os.path.join(self.dir, 'data/')
    cpath = os.path.join(self.dir, '../doc/')

    params = '-b html -c %s -Dsource=%s -Dmaster_doc=includesh' % (cpath, dpath)
    command = 'sphinx-build %s %s %s' % (params, dpath, self.tmp_dir)

    #print command

    os.system(command)

    # Read output
    output_path = os.path.join(self.tmp_dir, 'includesh.html')

    for line in open(output_path).readlines():
      print line.replace('\n', '')


def suite():
  # Return suite to setuptools
  #suite = unittest.TestLoader().loadTestsFromTestCase(XMLTableTestCase)
  suite = unittest.TestLoader().loadTestsFromTestCase(ShellConverterTestCase)
  suite = unittest.TestLoader().loadTestsFromTestCase(IncludeShellTestCase)

  #print suite
  return suite

if __name__ == '__main__':
    unittest.main()

