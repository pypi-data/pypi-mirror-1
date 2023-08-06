import os
from setuptools import setup, find_packages
from xml.dom import minidom

metadata_file = os.path.join(os.path.dirname(__file__),
                             'collective', 'groupdelegation',
                             'profiles', 'default', 'metadata.xml')
metadata = minidom.parse(metadata_file)
version = metadata.getElementsByTagName("version")[0].childNodes[0].nodeValue
version = str(version).strip()

setup(name='collective.groupdelegation',
      version=version,
      description="Plone Groups Management Delegation",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Zope Plone Groups Delegation',
      author='Ingeniweb',
      author_email='support@ingeniweb.com',
      url='http://ingeniweb.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
