import os
from setuptools import find_packages
from setuptools import setup

NAME = 'JRedirector'
here = os.path.abspath(os.path.dirname(__file__))
package = os.path.join(here, 'Products', NAME)
_boundary = '\n' + ('-' * 60) + '\n\n'

def _read(name):
    f = open(os.path.join(package, name))
    return f.read()

setup(name='Products.%s' % NAME,
      version=_read('VERSION.txt').strip(),
      description="Simple Zope 2 redirection manager object",
      long_description=( _read('README.txt')
                       + _boundary
                       + _read('CHANGES.txt')
                       + _boundary
                       + 'Download\n========'
                       ),
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope zope2 redirector',
      author='Jens Vagelpohl',
      author_email='jens@dataflake.org',
      url='http://pypi.python.org/pypi/Products.%s' % NAME,
      license="ZPL 2.1 (http://www.zope.org/Resources/License/ZPL-2.1)",
      packages=find_packages(),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # Zope2 >= 2.8
      ],
      entry_points="""
      [zope2.initialize]
      Products.%s = Products.%s:initialize
      """ % (NAME, NAME),
      )
