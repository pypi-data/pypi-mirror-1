__version__ = '1.0'

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
INSTALL_REQUIRES = [
    'ZopeSkel',
    ]

TESTS_REQUIRE = INSTALL_REQUIRES + []

setup(name='zopeskel.doctools',
      version=__version__,
      description='Tools for documenting ZopeSkel.',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Framework :: Plone",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Documentation",
        ],
      keywords='web skeleton project Plone Zope ZopeSkel Paster GraphViz',
      author="Joel Burton, Cris Ewing, Chris Calloway",
      author_email="cbc@chriscalloway.org",
      url="",
      license="MIT",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['zopeskel'],
      zip_safe=True,
      tests_require = TESTS_REQUIRE,
      install_requires=INSTALL_REQUIRES,
      test_suite="",
      entry_points={
      'console_scripts':[
          'pastegraph=zopeskel.doctools.graph:graph',
          'pastedoc=zopeskel.doctools.html_doc:make_html',
          ]
      }
    )
