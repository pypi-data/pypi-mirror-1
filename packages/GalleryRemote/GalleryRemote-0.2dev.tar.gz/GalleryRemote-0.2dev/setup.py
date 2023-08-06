from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='GalleryRemote',
      version=version,
      description="Implementation of the Gallery Remote protocol in Python.",
      long_description="""\
Implementation of the Gallery Remote protocol in Python.""",
      classifiers=['Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Topic :: Multimedia :: Graphics'],
      keywords='gallery gallery2 remote images pictures albums',
      author='Brent Woodruff',
      author_email='brent@fprimex.com',
      url='http://www.fprimex.com/programming/galleryremote',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
