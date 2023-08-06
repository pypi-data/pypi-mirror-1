from setuptools import setup, find_packages
import sys, os

version = '1.1'

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
      include_package_data=True,
      packages=find_packages('src'),
      package_dir = {'': 'src'},      
      zip_safe=True,
      install_requires=[
          'elementtree>=1.2.6'
      ],
)
    
