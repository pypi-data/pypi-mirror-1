from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='HTTPEncode',
      version=version,
      description="Fast RPC or encoded calls between WSGI apps",
      long_description="""\
**Note**: This library is deprecated, but it is provided for systems
or libraries that still depend on pieces of it.  Further development
of this library is highly unlikely.  You are suggested instead to use
`WebOb <http://pythonpaste.org/webob/>`_ and construct requests
manually and use ``req.get_reponse(proxy)``.

This library allows you to make fast calls between cooperating WSGI
applications, with automatic fallback for non-cooperative applications
or remote applications.

Requests are sent through WSGI obeying all middleware and the WSGI
spec.  Serialization/deserialization is avoided when possible.

It can be installed from the `subversion repository
<http://svn.pythonpaste.org/Paste/HTTPEncode/trunk#egg=HTTPEncode-dev>`_
with ``easy_install HTTPEncode==dev``
""",
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Framework :: Paste',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
      ],
      keywords='wsgi json web client',
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      url='http://pythonpaste.org/httpencode/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      extras_require={
        "json": ["simplejson"],
        "lxml": ["lxml"],
        "etree": ["ElementTree"],
        "BeautifulSoup": ["BeautifulSoup"],
        },
      install_requires=[
        "Paste",
        "httplib2",
      ],

      entry_points="""
      [httpencode.format]
      name json = httpencode.json:json [json]
      application/json to python = httpencode.json:json [json]
      # I'm not terribly comfortable with this one:
      application/x-javascript to python = httpencode.json:json [json]
      text/x-json to python = httpencode.json:json [json]

      application/x-www-form-urlencoded to cgi.FieldStorage = httpencode.form:form
      multipart/form-data to cgi.FieldStorage = httpencode.form:form
      name form = httpencode.form:form

      application/x-www-form-urlencoded to python = httpencode.form:pyform
      multipart/form-data to python = httpencode.form:pyform
      name pyform = httpencode.form:form

      text/xml to lxml = httpencode.lxmlformat:xml [lxml]
      application/xml to lxml = httpencode.lxmlformat:xml [lxml]
      name lxml = httpencode.lxmlformat:xml [lxml]

      text/html to lxml = httpencode.lxmlformat:html [lxml]
      name lxml_html = httpencode.lxmlformat:html [lxml]

      text/xml to ElementTree = httpencode.etree:xml [etree]
      application/xml to ElementTree = httpencode.etree:xml [etree]
      name etree = httpencode.etree:xml [etree]

      text/html to BeautifulSoup = httpencode.bsoupfilter:bsoup [BeautifulSoup]
      name BeautifulSoup = httpencode.bsoupfilter:bsoup [BeautifulSoup]
      name bsoup = httpencode.bsoupfilter:bsoup [BeautifulSoup]
      
      """,
      )
      
