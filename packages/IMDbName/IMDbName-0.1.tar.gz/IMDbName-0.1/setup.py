from ez_setup import use_setuptools

use_setuptools()
from setuptools import setup, find_packages

setup(name='IMDbName',
      version='0.1',
      description='A script for renaming movies using the IMDb database',
      long_description=open('README').read()+'\n'+open('CHANGES').read(),
      author='Jimmy Theis',
      author_email='jimmy@jetheis.com',
      url='https://svn.jetheis.com/public/IMDbName/trunk',
      license='GPLv3',
      keywords='script imdb movie rename database',
      packages=find_packages(exclude=''),
      package_data={},
      install_requires=['IMDbPY>=4.3'],
      entry_points="""
      [console_scripts]
      imdbname = imdbname.imdbname:main
      """)
