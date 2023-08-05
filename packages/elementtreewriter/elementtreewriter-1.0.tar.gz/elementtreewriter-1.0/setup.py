from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='elementtreewriter',
      version=version,
      description="XML writer for elementtree with sane namespace support.",
      long_description="""\
This is an alternative for the standard XMLWriter of elementtree. If you need
a better namespace handling - with sane prefixes -  go with this version.

""",
      classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Development Status :: 5 - Production/Stable',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: XML',
      ], 
      keywords='xml elementtree',
      author='Martin Raspe, Jens Klein',
      author_email='hertzhaft@biblhertz.it, jens@bluedynamics.com',
      url='',
      license='D-FSL - German Free Software License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'elementtree>=1.2.6'
      ],
)
    
