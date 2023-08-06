from setuptools import setup, find_packages
import sys, os

version = '0.2.0'

setup(name='gpxtools',
      version=version,
      description="Command line tools useful to manipulate GPX files.",
      long_description = open('README.txt').read() + "\n" + open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Text Processing :: Markup :: XML'
        ],
      keywords='GPS GPX SRTM',
      author='Wojciech Lichota',
      author_email='wojciech@lichota.pl',
      url='http://lichota.pl/blog/topics/gpxtools',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'GDAL',
          'lxml',
      ],
      entry_points="""
[console_scripts]
gpx-fix-elevation = gpxtools.script:main
gpx-cleanup = gpxtools.script:main
gpx-compress = gpxtools.script:main
      """,
      )
