# -*- coding: utf-8 -*-
import os
import logging

# Import required docutils modules
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.directives.tables import ListTable
from docutils import io, nodes, statemachine, utils, frontend
from docutils.nodes import literal_block
from docutils.utils import Reporter, SystemMessagePropagation


class Messenger(Reporter):
  def __init__(self, src='rusty.xyz'):
    settings = frontend.OptionParser().get_default_values()

    settings.report_level = 1

    Reporter.__init__(self,
      src,
      settings.report_level,
      settings.halt_level,
      stream=settings.warning_stream,
      debug=settings.debug,
      encoding=settings.error_encoding,
      error_handler=settings.error_encoding_error_handler
    )

    self.log = logging.getLogger(src)

  def debug(self, *msgs):
    #return super(Messenger, self).debug(msg)
    pass

  def info(self, *msgs):
    #return super(Messenger, self).info(msg)
    pass

  def warning(self, *msgs):
    #super(Messenger, self).warning(msg)
    return literal_block(text=self._prepare(msgs))

  def error(self, *msgs):
    #super(Messenger, self).error(msg)
    text = self._prepare(msgs)
    #self.log.error(text)
    return literal_block(text=text)

  def _prepare(self, *msgs):
    return ' '.join([unicode(msg) for msg in msgs])


class DirectiveTemplate(Directive):
  '''
  Template intended for directive development, providing
  few handy functions
  '''

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

