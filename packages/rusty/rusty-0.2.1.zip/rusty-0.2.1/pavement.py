import os
import sys

from setuptools import command
from docutils.utils import SystemMessage

from sphinx import __version__
from sphinx.builders import BUILTIN_BUILDERS
from sphinx.errors import SphinxError
from sphinx.application import Sphinx
from sphinx.util import Tee, format_exception_cut_frames, save_traceback
from sphinx.util.console import darkred, nocolor, color_terminal

#from paver.defaults import call_task, sh, setuputils
from paver.easy import *
from paver.misctasks import *
from paver.setuputils import setuptools, install_distutils_tasks, find_package_data
from paver import setuputils

options = environment.options

# Make distuils tasks available
install_distutils_tasks()

# Put unit test folder in path
sys.path.insert(0, str(os.path.abspath(path(__file__).dirname() / 'test' )))
sys.path.insert(0, str(os.path.abspath(path(__file__).dirname() / '.' )))

import rusty

# Define package
options(
    setup = Bunch(
        name = "rusty",
        version = rusty.__version__,
        author = rusty.__author__,
        author_email = rusty.__email__,
        license = rusty.__license__,
        description = 'A collection of Sphinx extensions',
        long_description = rusty.__doc__,
        url = 'http://jmu.koodiorja.com/projects/rusty/',
        download_url = 'http://pypi.python.org/pypi/rusty/',
        zip_safe = False,
        packages = ['', 'rusty'],
        package_data = setuputils.find_package_data(
          where=".",
          package="rusty",
          only_in_packages=False,
        ),
        extras_require = {
          'xmltable':['BeautifulSoup>=0.3'],
        },
        test_suite='test_all.suite',
        classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Documentation',
          'Topic :: Utilities',
        ],
        platforms='any',
    ),
    sphinx=Bunch(
        builddir="build",
        docroot="doc"
    ),

)

@task
@needs(['generate_setup', 'minilib', 'setuptools.command.sdist'])
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass

@task
@needs(['setuptools.command.bdist_egg'])
def package():
    """One command to rule them all"""
    egg = path('./rusty.egg-info')
    call_task('bdist_egg')

    # Build documentation
    doc()
    egg.rmtree()

@task
def default():
    package()

@task
@cmdopts([
  ('format=', 'o', 'Format documents to convert. Supported values are: \
"html", "htmlhelp", "text" and "latex". \
Use "all" to convert all supported formats'),
  ('force', 'f', 'Re-build: Always and everything')
])
def doc():
  """Build documentation"""

  force = False
  if hasattr(options, 'force'):
    force = True

  if not hasattr(options, 'format'):
    options.format = ['html']
  elif options.format == 'all':
    options.format = ['html', 'htmlhelp', 'text', 'pdf']

  # Make sure dist folder exists
  dist = path('dist')
  if not dist.exists():
    dist.mkdir()

  # Convert to html
  if 'html' in options.format:
    target = u'dist/html'
    build_doc('doc', target, force=force)

  # Create CHM if hhp is available
  if os.name == 'nt' and 'htmlhelp' in options.format:
    target = u'./build/htmlhelp'
    build_doc('doc', target, buildername='htmlhelp', force=force)
    sh(u'hhc %s/rusty.hhp' % target, ignore_error=True)
    chm = path(target + '/rusty.chm')
    chm.copy('./dist/')
    chm.remove()

  # Create PDF if pdflatex is available
  if os.name == 'posix' and path('/usr/bin/pdflatex').exists() and 'pdf' in options.format:
    # Build the documentation
    build_doc('doc', u'build/latex', buildername='latex', force=force)
    sh('make --directory %s' % 'build/latex')
    # Remove existing document
    pdf_target = path('dist/rusty.pdf')
    if pdf_target.exists():
      pdf_target.remove()

    path('build/latex/rusty.pdf').move(unicode(pdf_target))

  # Create PDF with rst2pdf if reqs are met
  # let fail if rst2pdf is not available
  if 'pdf' in BUILTIN_BUILDERS:
    build_doc('doc', u'dist', buildername='pdf', force=force)

@task
@cmdopts([
  ('doc=', 'd', 'Document to convert without extension: \
By default all the test documents are built'),
])
def test():
  """Runs the unit tests"""
  target_path = path('dist/test')
  if not target_path.exists():
    target_path.makedirs()
  target = unicode(target_path)
  unused_docs = ['']
  src_dir = 'test'

  #src_dir = 'test2'

  build_doc(src_dir, target, force=True)

@task
def check():
  """Check links"""
  build_doc('doc', 'dist', buildername='linkcheck')

def build_doc(srcdir, outdir, confdir=None, buildername='html', force=False):
  '''
  Build document with sphinx
  '''
  if not confdir:
    confdir = srcdir

  confdir = os.path.abspath(confdir)
  srcdir = os.path.abspath(srcdir)

  # Make sure the output dir exists
  odir = path(outdir)
  odir.makedirs()

  all_files = None
  filenames = []
  warningiserror = use_pdb = False
  freshenv = force
  status = sys.stdout
  warning = sys.stderr
  error = sys.stderr
  warnfile = None
  confoverrides = {}
  htmlcontext = {}
  tags = []

  # There seems to be some differences in path joins in windows and linux?
  if os.name != 'nt':
    outdir = str(outdir)
  doctreedir = path.join(outdir, '.doctrees')

  try:
    app = Sphinx(srcdir, confdir, outdir, doctreedir, buildername,
                 confoverrides, status, warning, freshenv,
                 warningiserror, tags)
    app.build(all_files, filenames)
    return app.statuscode
  except KeyboardInterrupt:
    if use_pdb:
      import pdb
      print >>error, darkred('Interrupted while building, '
                             'starting debugger:')
      traceback.print_exc()
      pdb.post_mortem(sys.exc_info()[2])
      return 1
  except Exception, err:
    if use_pdb:
      import pdb
      print >>error, darkred('Exception occurred while building, '
                                   'starting debugger:')
      traceback.print_exc()
      pdb.post_mortem(sys.exc_info()[2])
    else:
      if isinstance(err, SystemMessage):
        print >>error, darkred('reST markup error:')
        print >>error, err.args[0].encode('ascii', 'backslashreplace')
      elif isinstance(err, SphinxError):
        print >>error, darkred('%s:' % err.category)
        print >>error, err
      else:
        print >>error, darkred('Exception occurred:')
        print >>error, format_exception_cut_frames().rstrip()
  return 1


@task
def dpi():
  """Changes the PNG images DPI to given value"""
  srcdir = path('doc')

  import Image

  for imgpath in srcdir.walkfiles('*.png'):
    print 'Processing image: %s ...' % imgpath
    img = Image.open(str(imgpath))
    img.save('%s.png' % imgpath.stripext(), 'PNG', dpi=(120, 120))


