from setuptools import setup, find_packages
import sys, os

version = '1.0rc1'

setup(name='p4a.audio',
      version=version,
      description="Plone4Artists audio abstraction library",
      long_description="""p4a.audio is a Python audio library for dealing
with audio files and their various means of storing/loading metadata.""",
      classifiers=[
          'Framework :: Zope3',
          'Programming Language :: Python',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Multimedia :: Sound/Audio'
          ],
      keywords='Plone4Artists',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='http://www.plone4artists.org/products/plone4artistsaudio',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['p4a'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
