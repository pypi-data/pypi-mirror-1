# -*- coding: utf-8 -*-
'''
This module provides the ``includesh`` directive. It is implemented by
:class:`IncludeShellDirective` class.
'''
import os
import re
import types
import tempfile

# Import required docutils modules
from docutils import io, nodes, statemachine, utils
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.directives.misc import Include
from docutils.parsers.rst.directives.tables import ListTable

import sphinx


#---------------------------------------------------------#
class IncludeShellDirective(Include):
  '''
  IncludeShellDirective implements the directive. The class
  is registered as a directive in :func:`rusty.includesh.setup`
  '''
  required_arguments = 1
  optional_arguments = 0
  has_content = None
  node_class = None
  option_spec = {
    'comment': directives.unchanged,
    'encoding': directives.encoding,
    'start-after': directives.unchanged_required,
    'end-before': directives.unchanged_required
  }

  #---------------------------------------------------------#
  def run(self):
    '''
    Called automatically by the docutils.
    '''
    comment_char = self.options.get('comment', '#')

    # Take the current inclusion file, read it and save in
    # temporary location where the actual ``Include`` directive
    # can read it

    # This part is taken from docutils
    if not self.state.document.settings.file_insertion_enabled:
      raise self.warning('"%s" directive disabled.' % self.name)

    source = self.state_machine.input_lines.source(
      self.lineno - self.state_machine.input_offset - 1)

    source_dir = os.path.dirname(os.path.abspath(source))
    path = directives.path(self.arguments[0])

    if path.startswith('<') and path.endswith('>'):
      path = os.path.join(self.standard_include_path, path[1:-1])

    path = os.path.normpath(os.path.join(source_dir, path))
    path = utils.relative_path(None, path)
    encoding = self.options.get(
      'encoding', self.state.document.settings.input_encoding)

    try:
      self.state.document.settings.record_dependencies.add(path)
      include_file = open(path, 'r+b')
    except IOError, error:
      raise self.severe('Problems with "%s" directive path:\n%s: %s.'
                        % (self.name, error.__class__.__name__, error))

    try:
      include_text = include_file.read()
    except UnicodeError, error:
      raise self.severe(
        'Problem with "%s" directive:\n%s: %s'
        % (self.name, error.__class__.__name__, error))

    # Do not allow literal option to be given (it is supported by include)
    if 'literal' in self.options:
      del self.options['literal']

    # TODO: Add start-after, end-before support

    shellco = ShellConverter(
      script_path=path,
      encoding=encoding,
      comment_character='#',
    )
    # Replace the original file with the converted path
    self.arguments[0] = shellco.to_rst()

    return Include.run(self)


class ShellConverter(object):
  '''
  Converts shell script into another format - restructured documentation
  format in this case.

  >>> sc = ShellConverter(script_path='/tmp/script.sh', comment_character='#')
  >>> sc.to_rst(target_path='/tmp/script.output.rst')
  '''
  def __init__(self, script_path, encoding='utf-8', comment_character='#'):
    '''
    Initialization

    script_path
      Path to shell script

    encoding
      Encoding of the script source, utf-8 by default

    comment_character
      Character or string that notes the comment in shell script. The comment
      strings are expected to be in RST format and will be turned in to normal
      text. Default: #
    '''
    if not os.path.exists(script_path):
      raise Exception('Given script file %s cannot be found' % script_path)

    self.script_path = script_path
    self.comment_character = comment_character
    #self.comment_re = re.compile(r'^%s%s+' % (comment_character, comment_character))

  def to_rst(self, target_path=None):
    '''
    Does the conversion and saves the result in ``target_document_path``

    target_path
      Path where to save the converted document. If not given, a temp file is
      created and path is returned back

    .. NOTE::
       Delete the target file manually after no longer needed.
    '''
    if not target_path:
      tfd, target_path = tempfile.mkstemp(prefix='rusty-')

    source = open(self.script_path, 'r+b')
    target = open(target_path, 'w+b')

    in_para = False
    in_com = False

    # Iterate source document lines
    for line in source.readlines():

      # Skip shebang
      if line.startswith('#!'):
        pass

      # Comment line > RST
      elif line.startswith(self.comment_character):
        in_com = False

        # If double comment, skip
        if not line.startswith(self.comment_character*2):

          # FIXME: More advanced indent handling needed?
          entry = line.replace(self.comment_character, '', 1)[1:]

          # Handle new paragraph
          if not in_para:
            target.write('\n')
            in_para = True

          target.write('\n%s ' % entry.replace('\n', ''))

      # Command line > SHELL
      else:
        in_para = False
        # If empty start new literal block

        if not in_com and line.strip():
          entry = '.. code-block:: bash'
          target.write('\n\n%s\n\n' % entry)
          target.write('   %s' % line)
          in_com = True
        else:
          target.write('   %s' % line)

    return target_path


def setup(app):
  '''
  Extension setup, called by Sphinx
  '''
  # Sphinx 5 support
  if '5' in sphinx.__version__.split('.'):
    app.add_directive('includesh', IncludeShellDirective, 0, (0,0,0))
  else:
    app.add_directive('includesh', IncludeShellDirective)
