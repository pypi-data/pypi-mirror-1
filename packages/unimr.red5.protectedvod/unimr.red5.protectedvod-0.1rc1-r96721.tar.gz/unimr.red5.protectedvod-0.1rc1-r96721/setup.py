from setuptools import setup, find_packages
import os
from xml.dom import minidom

name = 'unimr.red5.protectedvod'

absolute_path = [os.path.dirname(__file__)] + name.split('.') + ['profiles', 'default', 'metadata.xml']

metadata_file = os.path.join(*absolute_path)
metadata = minidom.parse(metadata_file)
version = metadata.getElementsByTagName("version")[0].childNodes[0].nodeValue
version = str(version).strip()


setup(name=name,
      version=version,
      description="Manage, protect and present your video/audio content (FLV, MP3, etc.) with Plone but delegate the flash streaming to Red5",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Sound/Audio",
        ],
      keywords='Plone Flash FLV MP3 Zope Streaming Red5 rtmp',
      author='Andreas Gabriel',
      author_email='gabriel@hrz.uni-marburg.de',
      url='http://svn.plone.org/svn/collective/unimr.red5.protectedvod',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['unimr', 'unimr.red5'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'iw.fss',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
