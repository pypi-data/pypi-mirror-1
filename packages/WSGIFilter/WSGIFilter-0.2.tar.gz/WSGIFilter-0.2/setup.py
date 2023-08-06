from setuptools import setup, find_packages

version = '0.2'

setup(name='WSGIFilter',
      version=version,
      description="Abstract base class / framework for building output-filtering WSGI middleware",
      long_description="""\
A framework (in the form of an abstract base class) for building
output-filtering WSGI middleware.

Features:

* You can filter just some content types (e.g., text/html) with low
  overhead for unfiltered output.

* Handles issues of decoding and encoding responses using the
  `HTTPEncode <http://pythonpaste.org/httpencode/>`_ system of
  formats.

* Does all the hard stuff with WSGI output filtering.

It can be installed from the `subversion repository
<http://svn.pythonpaste.org/Paste/WSGIFilter/trunk#egg=WSGIFilter-dev>`_
with ``easy_install WSGIFilter==dev``
""",
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Framework :: Paste',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
      ],
      keywords='wsgi middleware webdev',
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      url='http://pythonpaste.org/wsgifilter/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Paste',
        'HTTPEncode',
        'webob',
      ],
      entry_points="""
      [paste.filter_app_factory]
      debug_headers = wsgifilter.proxyapp:make_debug_headers
      testing_vars = wsgifilter.examples.testingvars:TestingVars.paste_deploy_middleware
      """,
      )
      
