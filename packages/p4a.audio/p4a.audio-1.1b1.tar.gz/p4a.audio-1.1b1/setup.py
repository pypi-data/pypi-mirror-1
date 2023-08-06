from setuptools import setup, find_packages

version = '1.1b1'

readme = open('README.txt')
long_description = readme.read()
readme.close()

setup(name='p4a.audio',
      version=version,
      description="Plone4Artists audio abstraction library",
      long_description=long_description,
      classifiers=[
          'Framework :: Zope2',
          'Framework :: Zope3',
          'Framework :: Plone',
          'Programming Language :: Python',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Multimedia :: Sound/Audio',
          ],
      keywords='Plone4Artists audio mp3 ogg podcasting podcast id3 music',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='http://www.plone4artists.org/products/plone4artistsaudio',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['p4a'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'p4a.subtyper',
          'p4a.common>=1.0',
          'p4a.z2utils>=1.0',
          'p4a.fileimage>=1.0',
      ],
      )
