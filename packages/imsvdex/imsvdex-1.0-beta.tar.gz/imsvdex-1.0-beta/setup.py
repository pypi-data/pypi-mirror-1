from setuptools import setup, find_packages
import sys, os

version = '1.0-beta'

setup(name='imsvdex',
      version=version,
      description="Read and write vocabularies in IMS Vocabulary Definition "
                  "Exchange format specified.",
      long_description="""\
Cite: ''The IMS Vocabulary Definition Exchange (VDEX) specification defines a 
grammar  for the exchange of value lists of various classes: collections 
often denoted "vocabulary". Specifically, VDEX defines a grammar for the 
exchange of simple machine-readable lists of values, or terms, together with 
information that may aid a human being in understanding the meaning or 
applicability of the various terms. VDEX may be used to express valid data 
for use in instances of IEEE LOM, IMS Metadata, IMS Learner Information Package 
and ADL SCORM, etc, for example. In these cases, the terms are often not human 
language words or phrases but more abstract tokens. VDEX can also express 
strictly hierarchical schemes in a compact manner while allowing for more loose 
networks of relationship to be expressed if required.'' 
(http://www.imsglobal.org/vdex/). 

This module takes the VDEX-XML objects and offers an API to them.

VDEX Version 1 Final Specification is supported.
""",
      classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ], 
      keywords='vocabulary xml vdex',
      author='Martin Raspe',
      author_email='raspe@biblhertz.it',
      url='http://svn.plone.org/svn/collective/imsvdex/',
      license='D-FSL - German Free Software License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'elementtree>=1.2.6',
          'elementtreewriter>=1.0',
      ],
      )
      
