# -*- coding: utf-8 -*-
# :tabSize=2:indentSize=2:noTabs=true:
'''
Rolelist module implements the ``rolelist`` directive,
which can be used for example as follows:

.. code-block:: rst

    Document with :file:`conf.xml` and :file:`conf.xml`.

    The files listed in document:

    .. rolelist:: file

'''
from string import Template

from docutils import io, nodes, statemachine, utils
from docutils.parsers.rst import Directive, directives, roles
from docutils.parsers.rst.directives.misc import Include
from docutils.parsers.rst.directives.tables import ListTable

from sphinx.addnodes import pending_xref

class RoleListNode(nodes.General, nodes.Element):
  '''
  Custom placeholder node that is replaced in
  :mod:`process_rolelist`
  '''
  pass

class RoleListDirective(Directive):
  '''
  IncludeShellDirective implements the directive. The class
  is registered as a directive in :func:`rusty.rolelist.setup`.

  The structure of the directive::

    .. rolelist:: name-of-role
       :template: ${text} - ${value}
       :docwide:
       :levelsup: posint
       :siblings:

  '''
  required_arguments = 1
  optional_arguments = 2
  has_content = None
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
    rolelist = RoleListNode()

    # Name of the role to hunt - store in object
    rolelist['role'] = self.arguments[0]
    # List item string template
    rolelist['template'] = self.options.get('template', '${text} (${value})')
    # Find roles from whole document, or from nested nodes
    rolelist['docwide'] = self.options.get('docwide', False)
    # Number of nodes to step up in the document tree
    rolelist['levelsup'] = self.options.get('levelsup', 0)
    # Take sibling nodes in or leave out
    rolelist['siblings'] = self.options.get('siblings', False)

    return [rolelist]


def process_rolelist(app, doctree):
  '''
  Iterates the document nodes once the doctree has
  been constructed and replaces the custom rolelist node
  with actual content (a bullet list of selected role)
  '''
  env = app.builder.env

  #source_path = doctree.attributes.get('source', 'No src')
  #print '----------------- %s ----------------' % source_path

  '''
  # For testing purposes
  for ref_node in doctree.traverse(nodes.section):
    #doc_roles.append(ref_node)
    print '-'*20
    print ref_node
    print getattr(ref_node, 'attributes', 'no att')
    print ref_node.__class__
  '''

  # Iterate through all role list nodes (likely there is only one)
  role_list_counter = 1
  role_counter = 1
  for rlist_node in doctree.traverse(RoleListNode):
    doc_roles = []
    role_list_id = nodes.make_id('rolelist %s %s' % (rlist_node['role'], role_list_counter))

    # Get the range how much to search from from doctree
    levels_up = rlist_node['levelsup']
    # Get siblings flag
    siblings = rlist_node['siblings']
    if siblings == None:
      siblings = True

    parent = rlist_node
    # Go up in the hierarchy as many times as guided in levelsup options
    for level in range(levels_up):
      new_parent = parent.parent
      # If new parent is not None
      if new_parent:
        parent = new_parent

    #print 'PARENT: %s (%s...)' % (parent.__class__, str(parent)[:30])

    # Default to root element, force if docwide flag is set in rolelist directive
    # NOTE: When option is set, it returns None (otherwise False)
    if rlist_node['docwide'] != False or parent == None:
      parent = doctree

    # Iterate through docutils literals - for example the :file: -role
    # uses literal
    for ref_node in parent.traverse(nodes.literal, ascend=False, siblings=siblings):

      # WARNING: Make sure the entries have role definition as otherwise
      # well get duplicates from other xrefs
      if hasattr(ref_node, 'attributes') and ref_node.attributes.get('role', False):
        # Create a target for the reference
        role_id = nodes.make_id('role %s %s' % (ref_node.astext(), role_counter))

        if not ref_node.get('ids', False):
          ref_node['ids'] = [role_id]
        #ref_node['ids'] = [role_id]

        doc_roles.append({
          'ids':ref_node['ids'],
          'name':ref_node.get('role', ''),
          'text':ref_node.astext(),
          'value':''
        })

        role_counter += 1


    # Iterate through all sphinx references and collect them
    for ref_node in parent.traverse(pending_xref, ascend=False, siblings=siblings):
      # Create a target for the reference
      role_id = nodes.make_id('role %s %s' % (ref_node['reftype'], role_counter))

      if not ref_node.get('ids', False):
        ref_node['ids'] = [role_id]

      #doc_roles.append(ref_node)
      # Generate text for the bullet item: either caption, but
      # if it does not exist then the actual target name

      #print 'target: %s' % ref_node.attributes.get('reftarget')
      #print 'text: %s' % ref_node.astext()

      text = ''
      if ref_node['refcaption']:
        text = ref_node.astext()


      # Create ref target
      #target = nodes.target(text='trg')
      #ref_node.append(target)
      #new_node = nodes.paragraph(text='test')

      '''
      new_ref_node = nodes.paragraph()
      new_ref_node.attributes = ref_node.attributes
      new_ref_node.append(nodes.target(text='target'))


      ref_node.replace_self(new_ref_node)
      '''
      #ref_node.replace_self(nodes.target('', 'tar', *ref_node))
      #attrs = {'refid':role_id, 'backrefs':[role_list_id]}

      #ref_node.replace_self(nodes.target('', '', *ref_node, **attrs))
      #ref_node.replace_self(nodes.reference('', '', *ref_node, **attrs))

      doc_roles.append({
        'ids':ref_node['ids'],
        'name':ref_node['reftype'],
        'text':text,
        'value':ref_node['reftarget']
      })

      role_counter += 1


    # Generate bullet list from all the
    # references that are wanted by setting the 'role' in rolelist directive
    blist = nodes.bullet_list()
    for doc_role in doc_roles:

      if rlist_node['role'] == doc_role['name']:
        # FIXME: references do not work, yet
        '''
        entry = nodes.paragraph()
        entry.append(nodes.reference(text=doc_role['text'], refid=doc_role['value']))
        '''
        s = Template('%s' % rlist_node['template'])
        text = s.safe_substitute(text=doc_role['text'], value=doc_role['value'])

        entry = nodes.paragraph()
        attrs = {'refid':' '.join(doc_role.get('ids', []))}
        entry.append(nodes.reference('', text, *[], **attrs))
        blist.append(nodes.list_item('', entry))

    # If the list was empty, write empty item
    if len(blist) <= 0:
      entry = nodes.paragraph(text=_('No entries'))
      blist.append(nodes.list_item('', entry))

    # Replace the rolelist directive placeholder with list
    rlist_node.replace_self(blist)
    doc_roles = []
    role_list_counter += 1


def setup(app):
  '''
  Extension setup, called by Sphinx
  '''
  import sphinx

  # Sphinx 5 'support'
  if '5' in sphinx.__version__.split('.'):
    app.add_directive('rolelist', RoleListDirective, 0, (0,0,0))
  else:
    app.add_directive('rolelist', RoleListDirective)

  app.add_node(RoleListNode)
  app.connect('doctree-read', process_rolelist)


