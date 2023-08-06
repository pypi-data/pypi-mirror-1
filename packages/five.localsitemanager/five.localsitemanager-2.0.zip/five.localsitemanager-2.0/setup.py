"""Setup for five.localsitemanager package
"""
from setuptools import setup

version = '2.0'

setup(name='five.localsitemanager',
      version=version,
      url='http://pypi.python.org/pypi/five.localsitemanager',
      license='ZPL 2.1',
      description='Local site manager implementation for Zope 2',
      author='Rocky Burt and Contributors',
      author_email='zope-cmf@zope.org',
      long_description=open("README.txt").read() + "\n" + 
                       open("INSTALL.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
          'Environment :: Web Environment',
          'Framework :: Zope2',
          'License :: OSI Approved :: Zope Public License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP :: Site Management',
      ],
      keywords='zope zope2 five sitemanager',
      packages=['five', 'five.localsitemanager'],
      package_dir = {'': 'src'},
      namespace_packages=['five',],
      include_package_data = True,
      extras_require=dict(
          test=['zope.testing']
          ),
      install_requires=[
        'Acquisition',
        'Zope2 >= 2.12.dev',
        'ZODB3',
        'setuptools',
        'zope.component',
        'zope.event',
        'zope.interface',
        'zope.location',
        'zope.lifecycleevent >= 3.5.2',
        'zope.site',
        'zope.traversing',
      ],
      zip_safe = False,
      )
