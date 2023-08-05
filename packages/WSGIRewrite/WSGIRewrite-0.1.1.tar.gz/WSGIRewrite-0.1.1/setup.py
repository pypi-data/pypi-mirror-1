RELEASE = True

from setuptools import setup, find_packages
import sys, os

classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
"""

version = '0.1.1'

setup(name='WSGIRewrite',
      version=version,
      description="Path rewriter WSGI middleware with mod_rewrite compatible rules",
      long_description='''\
WSGIRewrite is a path rewriter WSGI middleware that uses the same syntax as the (in)famous ``mod_rewrite`` module for Apache.

The latest version is available in a `Subversion repository <http://wsgirewrite.googlecode.com/svn/trunk/wsgirewrite#egg=WSGIRewrite-dev>`_.
''',
      classifiers=filter(None, classifiers.split("\n")),
      keywords='wsgi rewrite middleware mod_rewrite',
      author='Roberto De Almeida',
      author_email='roberto@dealmeida.net',
      url='http://taoetc.org/93',
      download_url = "http://cheeseshop.python.org/packages/source/W/WSGIRewrite/WSGIRewrite-%s.tar.gz" % version,
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      test_suite = 'nose.collector',
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          "Paste",
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.filter_app_factory]
      main = wsgirewrite.rewrite:make_filter
      """,
      )
     
