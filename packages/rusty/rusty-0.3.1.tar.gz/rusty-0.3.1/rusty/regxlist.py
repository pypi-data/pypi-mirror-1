# -*- coding: utf-8 -*-
# :tabSize=2:indentSize=2:noTabs=true:
'''
Regxlist module implements the ``regxlist`` directive,
which creates a list of entries that matches with the regular expression rule,
found from the document:

.. code-block:: rst

    Fixes in this release:

    .. regxlist:: Fixed #\d+:.*
       :template:

'''
from string import Template
import re

from docutils import io, nodes, statemachine, utils
from docutils.parsers.rst import Directive, directives, roles
from docutils.parsers.rst.directives.misc import Include
from docutils.parsers.rst.directives.tables import ListTable

from sphinx.addnodes import pending_xref

class RegXListNode(nodes.General, nodes.Element):
  '''
  Custom placeholder node that is replaced in
  :mod:`process_regxlist`
  '''
  pass

class RegXListDirective(Directive):
  '''
  Implements the directive. The class
  is registered as a directive in :func:`rusty.regxlist.setup`.

  The structure of the directive::

    .. regxlelist:: regexp-rule
       :template: ${text} - ${value}
       :docwide:
       :levelsup: posint
       :siblings:

  '''
  required_arguments = 1
  final_argument_whitespace = True
  optional_arguments = 0
  has_content = True
  node_class = None
  option_spec = {
    'template':directives.unchanged_required,
    'docwide':directives.flag,
    'levelsup':directives.positive_int,
    'siblings':directives.flag,
  }

  def run(self):
    '''
    Implements the directive. In this case, it only
    stores the given argument and options into custom :class:`RoleListNode`
    object - which are taken from there in :func:`process_rolelist`.
    '''
    rolelist = RegXListNode()

    # Name of the role to hunt - store in object
    rolelist['regexp'] = ' '.join(self.arguments)
    # List item string template
    rolelist['template'] = self.options.get('template', '${0}')
    # Find roles from whole document, or from nested nodes
    rolelist['docwide'] = self.options.get('docwide', False)
    # Number of nodes to step up in the document tree
    rolelist['levelsup'] = self.options.get('levelsup', 0)
    # Take sibling nodes in or leave out
    rolelist['siblings'] = self.options.get('siblings', False)

    return [rolelist]


def process_regxlist(app, doctree):
  '''
  Iterates the document nodes once the doctree has
  been constructed and replaces the custom regxlist node
  with actual content (a bullet list of selected entries)
  '''
  env = app.builder.env

  # Iterate through all role list nodes (likely there is only one)
  role_list_counter = 1
  role_counter = 1
  for reglist_node in doctree.traverse(RegXListNode):
    entries = []

    # Get the output template
    template = reglist_node['template']

    # Get the range how much to search from from doctree
    levels_up = reglist_node['levelsup']
    # Get siblings flag
    siblings = reglist_node['siblings']
    if siblings == None:
      siblings = True

    parent = reglist_node

    # Go up in the hierarchy as many times as guided in levelsup options
    for level in range(levels_up):
      new_parent = parent.parent
      # If new parent is not None
      if new_parent:
        parent = new_parent

    #print 'PARENT: %s (%s...)' % (parent.__class__, str(parent)[:30])

    # Default to root element, force if docwide flag is set in rolelist directive
    # NOTE: When option is set, it returns None (otherwise False)
    if reglist_node['docwide'] != False or parent == None:
      parent = doctree

    # Retrieve and compile the regular expression rule
    regc = re.compile(reglist_node['regexp'], re.IGNORECASE)

    # Iterate through all sphinx references and collect them
    for para in parent.traverse(nodes.paragraph, ascend=False, siblings=siblings):

      # Do the regxp search for the paragraph text
      text = para.astext()
      match = regc.search(text)

      # Iterate the matches
      for match in regc.finditer(text):

        # Convert tuple into a dictionary, by setting the index as a key
        group_tuple = match.groups()
        groups = dict([[str(list(group_tuple).index(value)), value] for value in group_tuple ])
        # Convert the unicode keys to string - as Template requires us to do so
        gdict = dict([[str(key), value] for key,value in match.groupdict().items()])
        # Update to dictionary
        groups.update(gdict)

        if groups:
          #print groups

          # TODO: Add support for numeric placeholders - they are not supported
          # by Template, unfortunatelly.
          temp = DirectiveTemplate(template)

          #for key,value in groups.items():
          #  substitute = {key:match.group()}
          text = temp.safe_substitute(**groups)

          entries.append(text)


    # Generate bullet list from the entries
    blist = nodes.bullet_list()
    for entry in entries:

      # FIXME: references do not work, yet

      list_entry = nodes.paragraph(text=entry)
      #attrs = {}
      #list_entry.append(nodes.reference('', entry, *[], **attrs))
      blist.append(nodes.list_item('', list_entry))

    # If the list was empty, write empty item
    if len(blist) <= 0:
      list_entry = nodes.paragraph(text=_('No entries'))
      blist.append(nodes.list_item('', list_entry))

    # Replace the rolelist directive placeholder with list
    reglist_node.replace_self(blist)
    entries = []


class DirectiveTemplate(Template):
  '''
  Customized version of the Template to
  allow numeric variables
  '''
  idpattern = '([0-9]|[_a-z]|[_a-z0-9])+'


def setup(app):
  '''
  Extension setup, called by Sphinx
  '''
  import sphinx

  # Sphinx 5 'support'
  if '5' in sphinx.__version__.split('.'):
    app.add_directive('regxlist', RegXListDirective, 0, (0,0,0))
  else:
    app.add_directive('regxlist', RegXListDirective)

  app.add_node(RegXListNode)
  app.connect('doctree-read', process_regxlist)


