# -*- coding: utf-8 -*-
'''
:class:`XMLTableDirective` implements the ``xmltable`` -directive.
The implementation is based on two existing solutions:

* :class:`ListTable`, from the docutils module
* :class:`BeautifulStoneSoup`, from the BeautifulSoup module

The module introduces simple yet effective query language, that is
used to select and generate the RST-table from the XML-document.

'''
__docformat__ = 'restructuredtext'

import os
import re
import types
import logging

try:
  from xml.etree import ElementTree as ET
except ImportError:
  from elementtree import ElementTree as ET

# Import required docutils modules
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.directives.tables import ListTable
from docutils import io, nodes, statemachine, utils
from docutils.utils import SystemMessagePropagation

import sphinx

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup


logger = logging.getLogger("rusty.xmltable")

class XMLTableDirective(ListTable):
  '''
  XMLTableDirective implements the new
  restructured text directive. It's purpose
  is to provide an easy-to-use XML into RST table
  transition - in a form of docutils directive.
  '''
  #required_arguments = 0
  #optional_arguments = 0
  #has_content = Tur
  option_spec = {
    'file': directives.path,
    'header': directives.unchanged,
    'query': directives.unchanged_required,
    'widths': directives.positive_int_list,
    'class': directives.class_option,
  }

  def run(self):
    '''
    Implementes the directive:
    '''
    # Raise an error if the directive does not have contents.
    self.assert_has_content()

    # Get content and options
    file_path = self.options.get('file', None)
    query = self.options.get('query', None)
    columns = self.content

    if not file_path:
      self._report('file_path -option missing')

    if not query:
      self._report('query -option missing')

    # Transform the path suitable for processing
    file_path = self._get_directive_path(file_path)

    bt = BeautifulTable(open(file_path, 'r+b'))
    table = bt.create_table(query=query, columns=columns)

    title, messages = self.make_title()
    node = nodes.Element() # anonymous container for parsing
    self.state.nested_parse(self.content, self.content_offset, node)

    # If empty table is created
    if not table:
      self._report('The table generated from queries is empty')
      return [nodes.paragraph(text='')]

    try:
      table_data = []

      # If there is header defined, set the header-rows param and
      # append the data in row =>. build_table_from_list handles the header generation
      header = self.options.get('header', None)
      header_rows = 0
      if header:
        header_rows = 1
        table_data.append([nodes.paragraph(text=hcell.strip()) for hcell in header.split(',')])

      # Put the given data in rst elements: paragraph
      for row in table:
        table_data.append([nodes.paragraph(text=cell) for cell in row])

      # Get params from data
      num_cols = len(table_data[0])
      col_widths = self.get_column_widths(num_cols)
      stub_columns = 0

      # Sanity checks

      # Different amount of cells in first and second row (possibly header and 1 row)
      if len(table_data) > 1 and len(table_data[0]) != len(table_data[1]):
        error = self._report('Data amount mismatch: check the directive data and params')
        return [error]

      self.check_table_dimensions(table_data, header_rows, stub_columns)

    except SystemMessagePropagation, detail:
        return [detail.args[0]]

    # Generate the table node from the given list of elements
    table_node = self.build_table_from_list(
      table_data, col_widths, header_rows, stub_columns)
    table_node['classes'] += self.options.get('class', [])


    if title:
        table_node.insert(0, title)
    return [table_node] + messages


  def _report(self, msg):
      '''
      Reports about error
      '''
      message = 'Problem in %s directive: ' % self.name
      message += msg

      return self.state_machine.reporter.error(msg,
        nodes.literal_block(self.block_text, self.block_text),
        line=self.lineno)


  def _get_directive_path(self, path):
    '''
    Returns transformed path from the directive
    option/content
    '''
    source = self.state_machine.input_lines.source(
        self.lineno - self.state_machine.input_offset - 1)
    source_dir = os.path.dirname(os.path.abspath(source))
    path = os.path.normpath(os.path.join(source_dir, path))
    return utils.relative_path(None, path)


class BeautifulTable(object):
  '''
  Class generates the list based table from
  the given document, suitable for the directive.

  Class also implements the custom query format,
  is to use for the directive. Examples::

    /root-elem/sub-elem/elem   <- text value
    /root-elem/sub-elem@attr   <- attr value

  Internally, the BeautifulTable uses the BeautifulStoneSoup, from
  `BeautifulSoup`_.
  '''
  def __init__(self, fobj):
    '''
    '''
    self.file_object = fobj
    self.soup = BeautifulSoup(self.file_object)

  def create_table(self, query, columns):
    '''
    Creates a table (as a list) based on given query and columns
    '''
    rows = []

    self._debug('ITERATOR: ', query)
    for elem in self._query_path(query):
      row = []
      for column_query in columns:

        self._debug('#'*50)
        self._debug('## ITERM ELEM: ', elem.encode(), type(elem))

        field = self._query_value(column_query, elem)
        if field:
          row.append(field)
        else:
          row.append(u'')
      rows.append(row)

    return rows


  def _query_path(self, query, root=None):
    '''
    Implements the custom path query parser
    '''
    if not root:
      root = self.soup

    for child in query.split('/')[:-1]:
      new_root = getattr(root, child, None)
      if new_root:
        root = new_root

    # tag can be iterated directly
    if not root:
      raise Exception('No root')

    listing = root.findAll(name=query.split('/')[-1])
    self._debug('RETURN ROOT: ', root, type(root))
    return listing


  def _query_value(self, query, root=None):
    '''
    Implements the custom value query parser
    '''
    assert root, 'root is none'

    if not root:
      root = self.soup

    # Split the query in parts:
    # take the root elements, but not the last one
    root_parts = query.split('.')[:-1]
    query = query.split('.')[-1]

    # Iterate until new root is found
    for part in root_parts:

      # NOTE: getattr cannot be used due the reserved names
      # for the object
      new_root = root.find(part)

      self._debug('----------> new root: %s, %s' % (new_root, type(new_root)))

      if new_root:
        root = new_root

    # Attribute handling
    attr = None
    if u'@' in query:
      query, attr = query.split(u'@', 1)

    # Special keyword: self
    if u'self' != query:
      self._debug('## QROOT: ', root, type(root))
      self._debug('## QUERY: ', query)

      # NOTE: getattr cannot be used due the reserved names for the functions
      # and attributes.
      if getattr(root, query, None):
        new_root = root.find(query)
        if new_root:
          self._debug('## NEW QROOT:', root, type(new_root))
          root = new_root

    else:
      self._debug('>> SELF')
      self._debug('## QUERY: ', query)


    self._debug('## FINAL ROOT: ', root, type(root))

    if not root:
      return u''

    # Return attribute value
    if attr and hasattr(root, 'get'):
      return root.get(attr, u'')

    # Return string value of the element
    if root.string:
      return root.string

    # Return string value of the subelements
    string = u''
    if getattr(root, query, None) or query == u'self':
      for sub in root.findAll(recursive=True):
        if sub.string:
          string += u'%s ' % sub.string

    self._debug('>> STRING:', string)

    return string


  def _debug(self, *args):
    '''
    Debug function for internal usage
    '''
    return

    for arg in args:
      print ''.join(str(arg).splitlines()),
    print ''


def setup(app):
  '''
  Extension setup, called by Sphinx
  '''
  # Sphinx 5 support
  if '5' in sphinx.__version__.split('.'):
    app.add_directive('xmltable', XMLTableDirective, 0, (0,0,0))
  else:
    app.add_directive('xmltable', XMLTableDirective)


