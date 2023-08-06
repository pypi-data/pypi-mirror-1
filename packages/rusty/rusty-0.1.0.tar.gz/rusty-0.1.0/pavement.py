import os
import sys

from setuptools import command

#from paver.defaults import call_task, sh, setuputils
from paver.easy import *
from paver.misctasks import *
from paver.setuputils import setuptools, install_distutils_tasks, find_package_data
from paver import setuputils

options = environment.options

# Make distuils tasks available
install_distutils_tasks()

# Put unit test folder in path
sys.path.insert(0, str(path(__file__).dirname() / 'test' ))
sys.path.insert(0, str(path(__file__).dirname() / '.' ))

import rusty

long_description = '''
Rusty is a collection of `Sphinx <http://www.sphinx.pocoo.org>`_
extensions - namely roles and directives.

At the moment, the Rusty contains following extensions:

**rolelist**
  Generates list from the selected set of role entires, 
  written into document. This might come handy for example
  with release notes where bug entries (marked with role syntax)
  are listed automatically.

**includesh**
  Includesh (or include shell) extends the basic functionality of
  ``include`` directive: instead of just including the contents of the
  file into document, the includesh transforms the shell comments into
  documents and commands into literal blocks.
'''


# Define package
options(
    setup = Bunch(
        name = "rusty",
        version = "0.1.0",
        author = "Juha Mustonen",
        author_email = "juha,p,mustonen(a)gmail.com",
        license = 'MIT',
        description = 'A collection of Sphinx extensions',
        long_description = long_description,
        url="http://jmu.koodiorja.com/projects/rusty/",
        zip_safe=False,
        packages = ['rusty'],
        package_data=setuputils.find_package_data(
          where=".", 
          package="rusty",
          only_in_packages=False,
        ),
        #install_requires = ['BeautifulSoup>=0.3'],
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
#@needs(['paver.doctools.html'])
@cmdopts([
  ('format=', 'o', 'Format documents to convert. Supported values are: \
"html", "htmlhelp", "text" and "latex". \
Use "all" to convert all supported formats'),
  ('force', 'f', 'Re-build: Always and everything')
])
def doc():
  """Build documentation"""

  force = ''
  if hasattr(options, 'force'):
    force = '-a'  

  if not hasattr(options, 'format'):
    options.format = ['html']
  elif options.format == 'all':
    options.format = ['html', 'htmlhelp', 'text', 'pdf']

  # Convert to html
  if 'html' in options.format:
    target = 'dist/html'
    if force:
      (path(target) / '.doctrees').rmtree()
    sh('sphinx-build %s -b html doc %s' % (force, target))
 
  # Create CHM if hhp is available
  if os.name == 'nt' and 'htmlhelp' in options.format:
    sh('sphinx-build %s -b htmlhelp doc build/htmlhelp' % (force))

  # Create PDF if pdflatex is available 
  if os.name == 'posix' and path('/usr/bin/pdflatex').exists() and 'pdf' in options.format:
    sh('sphinx-build %s -b latex doc build/latex' % (force))
    sh('make --directory %s' % 'build/latex') 
    # Remove existing document 
    pdf_target = path('dist/rusty.pdf')
    if pdf_target.exists():
      pdf_target.remove()

    path('build/latex/rusty.pdf').move(str(pdf_target))
