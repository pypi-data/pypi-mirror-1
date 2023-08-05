from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='BrightContent',
      version=version,
      description="Bright Content is Python Weblog software built from reusable components.",
      long_description="""\
`Bright Content<http://brightcontent.net>`_ is Python Weblog software built from
reusable components.
It offers many of the usual features of Weblog engines, but it's basic
opration and plug-in model is based on the WSGI standard for Python Web
components.  Many existing WSGI components can be plugged sirectly into
Bright Content in order to enhance its operation, and Bright Content
also has a set of specialized components for common Weblog needs.
 
Bright Content also builds on the `Atom Syntax, Atom
Protocol<http://en.wikipedia.org/wiki/Atom_%28standard%29>`_, and
an XML data flow.  XML is used modestly (e.g. not for configuration)
and is intended as much as possible not to get in the way.  Built-in
templates are XSLT for now, but using `Buffet
plug-ins<http://projects.dowski.com/projects/buffet>`_ other
templating systems can be easily added.

The latest version is available in a `Subversion repository
<http://svn.brightcontent.net/brightcontent/trunk#egg=brightcontent-dev>`_.
""",
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'License :: OSI Approved :: Academic Free License (AFL)',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
          'Topic :: Text Processing :: Markup :: XML',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware'
          ],
      keywords='wsgi atom blog',
      author='Uche Ogbuji and Julian Krause',
      author_email='brightcontent@brightcontent.net',
      url='http://brightcontent.net',
      license='AFL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Paste',
          'PasteScript',
          'Amara',
          'Beaker'
      ],
      entry_points="""
      [paste.app_factory]
      main = brightcontent.wsgiapp:make_app
      """,
      )
      
