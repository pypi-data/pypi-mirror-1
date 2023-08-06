from setuptools import setup, find_packages
from os.path    import dirname, join
srcdir = join(dirname(__file__), 'src')
setup(name             = 'SpiffIntegrator',
      version          = '0.2.0',
      description      = 'A package/plugin manager implemented in Python',
      long_description = \
"""
Spiff Integrator is a small but powerful package manager that was written
for adding plugin support into applications. It handles packing/unpacking,
installation/updates/removal, and dependency management and provides a bus
over which plugins may communicate.
It was designed to provide a clean API, high security and high scalability.

For documentation please refer to the `README file`_ or the tests included
with the package. You may also look at the `API documentation`_.

.. _README file: http://code.google.com/p/spiff-integrator/source/browse/trunk/README
.. _API documentation: http://docs.debain.org/spiff_integrator/index.html
""",
      author           = 'Samuel Abels',
      author_email     = 'cheeseshop.python.org@debain.org',
      license          = 'GPLv2',
      package_dir      = {'': srcdir},
      packages         = [p for p in find_packages(srcdir)],
      requires         = ['sqlalchemy'],
      keywords         = 'spiff integrator package manager dpkg install uninstall dependency',
      url              = 'http://code.google.com/p/spiff-integrator/',
      classifiers      = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ])
