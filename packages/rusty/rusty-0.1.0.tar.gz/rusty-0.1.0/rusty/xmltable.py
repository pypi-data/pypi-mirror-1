# -*- coding: utf-8 -*-
'''
:class:`XMLTable` is the class that you want to use from this module.
'''
__docformat__ = 'restructuredtext'
__version__ = '0.1.0'

import re
import types

try:
  from xml.etree import ElementTree as ET
except ImportError:
  from elementtree import ElementTree as ET

# Import required docutils modules
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.directives.tables import ListTable

import sphinx

from rusty import table

#---------------------------------------------------------#
class XMLTableDirective(ListTable):
  '''
  
  /usr/local/lib/python/site-packages/docutils-0.5-py2.6.egg/docutils/parsers/rst/directives/tables.py
  
  XMLTableDirective implements the new
  restructured text directive. It's purpose
  is to provide an easy-to-use XML into RST table
  transition - in a form of docutils directive.

  '''
  #required_arguments = 0
  #optional_arguments = 0
  #has_content = Tur 
  option_spec = {
    'header-rows': directives.nonnegative_int,
    'stub-columns': directives.nonnegative_int,
    'widths': directives.positive_int_list,
    'class': directives.class_option
  }

  #---------------------------------------------------------#
  def run(self):
    #Called automatically by the docutils
    # Raise an error if the directive does not have contents.
    #self.assert_has_content()

    #image_node = nodes.image(rawsource = self.block_text,
    #  **self.options)

    # Create table
    table_data = (
      ('foo', 'bar'),
      ('baz', 'fum')
    )
    
    return [nodes.inline(text='XMLTable testing...')]
    
    node = nodes.Element()
    
    #num_cols, col_widths = self.check_list_content(node)
    col_widths = (10,10)
    header_rows = self.options.get('header-rows', 0)
    stub_columns = self.options.get('stub-columns', 0)
    
    table_node = self.build_table_from_list(table_data, col_widths,
      header_rows, stub_columns)
    
    #dtable = table.Table(data)
    #text = unicode(dtable.create_table(first_row_is_header=False))
    #text = 'XMLTable testing in progress...'

    #return [nodes.inline(text='foo')] 
    #return [nodes.paragraph(text=text)]
    #return [nodes.table(rawsource=text)]
    #return [nodes.raw(text=text)]
    #return [nodes.literal_block(text=text)]
    
    return [table_node]

#---------------------------------------------------------#
class XMLTable(object):
  '''
  Query reads the data from the given XML file
  and generates the RST table from it using :mod:`table` module.
  '''
  pass


#---------------------------------------------------------#
class Query(object):
  '''
  Query provides improved XPath selector over the default
  :class:`xml.etree.ElementTree`
  
  .. IMPORTANT::
      Do ready for general consumption, yet. Instead, use
      BeatifulSoup instead.
  
  '''
  #---------------------------------------------------------#
  def __init__(self, path=None, element=None):
    '''
    Constructor of the Query.
    
    Parameters
    ----------
    path:
      Path to the file to query.
      
    element:
      ElementTree element, used when returning objects
      from :func:`query()` function
      
    .. note::
    
       Either path of elem must be given.
      
    '''
    self.attrib = {}
    self.value = None
    
    if type(element) is types.NoneType:
      self._tree = ET.parse(path)
    else:
      self._tree = element
      self.attrib = getattr(self._tree, 'attrib')
      self.value = self.value
      
  #---------------------------------------------------------#
  def __len__(self):
    '''
    Implement the internal __len__ method by counting
    the elements of the tree
    '''
    return len(self._tree)
    
  #---------------------------------------------------------#
  def __dict__(self, attribute):
    '''
    Implements the attribute selection in a dictionary style
    '''
    return self._tree.attrib[attribute]

  #---------------------------------------------------------#
  def query(self, query):
    '''
    Runs the given query to the XML tree
    '''
    query = self._parse_query(query)
    
    '''
    if not self._element:
      tree = ET.parse(self._path)
    else:
      tree = self._element
    '''
    
    #print 'query: %s' % query

    for elem in self._tree.findall(query['path']):
      attrib = query['attrib']
      if attrib:
        if attrib in elem.attrib:
          yield Query(element=elem)
        else:
          yield None
      elif elem.text:
        yield Query(element=elem)

  #---------------------------------------------------------#
  def _parse_query(self, strquery):
    '''
    Parses the given string query into dictionary.

    >>> xt = Query('/tmp/test.xml')
    >>> xt._parse_query('/foo/bar')
    'bar'
    >>> xt._parse_query('foo/bar')
    'foo/bar'

    '''
    query = {'path':'', 'attrib':None}

    # Split path and attribute definition
    splitted = re.split(r'\@(\w+)$', strquery)

    # Place the arguments in dict
    if len(splitted) > 1:
      query['path'] = splitted[0]
      query['attrib'] = splitted[1]
    else:
      query['path'] = splitted[0]

    # Since ``ElementTree`` does not support absolute
    # references, remove it from the beginning
    path = query['path']
    query['path'] = re.sub(r'^\/\w+\/', '', path)

    return query
    
def setup(app):
  '''
  Extension setup, called by Sphinx
  '''
  # Sphinx 5 support
  if '5' in sphinx.__version__.split('.'):
    app.add_directive('xmltable', XMLTableDirective, 0, (0,0,0))
  else:  
    app.add_directive('xmltable', XMLTableDirective)

    
