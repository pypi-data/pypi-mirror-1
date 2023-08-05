from setuptools import setup, find_packages

version = '0.6.2'

setup(name='Beaker',
      version=version,
      description="Session (and caching soon) WSGI Middleware",
      long_description="""\
Beaker is a simple WSGI middleware to use the Myghty Container API

MyghtyUtils contains a very robust Container API for storing data using various
backend. Beakeruses those APIs to implement common web application wrappers,
like sessions and caching, in WSGI middleware. Currently the only middleware
implemented is that for sessions but more is coming soon.

The latest version is available in a `Subversion repository
<http://beaker.groovie.org/svn/trunk/Beaker#egg=Beaker-dev>`_.
""",
      classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Environment :: Web Environment',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python',
      'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      keywords='wsgi myghty session web middleware',
      author='Julian Krause, Ben Bangart',
      author_email='thecrypto@thecrypto.org',
      url='http://beaker.groovie.org',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      zip_safe=False,
      install_requires=[
          'MyghtyUtils',
      ],
      entry_points="""
          [paste.filter_factory]
          beaker_session = beaker.session:session_filter_factory
          [paste.filter_app_factory]
          beaker_session = beaker.session:session_filter_app_factory
      """,
)
