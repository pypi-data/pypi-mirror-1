from setuptools import setup, find_packages
import os

version = '1.0b1'

setup(name='collective.ATClamAV',
      version=version,
      description="A product  providing ClamAV antivirus integration for AT-based content types",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Environment :: Web Environment',
          'Framework :: Plone',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',      
        ],
      keywords='plone antivirus archetypes',
      author='G. Gozadinos',
      author_email='ggozad@qiweb.net',
      url='http://pypi.python.org/pypi/collective.ATClamAV',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
          test=[
            'zope.testing',
            'Products.PloneTestCase',
          ]
      ),
      install_requires=[
          'setuptools',
          'archetypes.schemaextender >=1.0b1'
          # -*- Extra requirements: -*-
      ],
      )
