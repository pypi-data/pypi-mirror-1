from setuptools import setup, find_packages
from os.path    import dirname, join
srcdir = join(dirname(__file__), 'src')
setup(name             = 'SpiffWarehouse',
      version          = '0.2.0',
      description      = 'A library for storing revisioned files',
      long_description = \
"""
Spiff Warehouse is a library that stores revisioned files in a database
and provides an API for getting a diff between documents (if the
document format is supported).
""",
      author           = 'Samuel Abels',
      author_email     = 'cheeseshop.python.org@debain.org',
      license          = 'GPLv2',
      package_dir      = {'': srcdir},
      packages         = [p for p in find_packages(srcdir)],
      keywords         = 'spiff warehouse object storage revisioning',
      url              = 'http://code.google.com/p/spiff-warehouse/',
      classifiers      = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ])
