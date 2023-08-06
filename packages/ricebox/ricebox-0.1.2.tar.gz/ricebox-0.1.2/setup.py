from setuptools import setup, find_packages
import sys, os

version = '0.1.2'

setup(name='ricebox',
      version=version,
      description="Grabs the daily special from the rice box in bristol.",
      long_description="""\
Scrapes the Rice Box's website and returns the current daily special.""",
      classifiers=["Environment :: Console",
                   "Intended Audience :: Other Audience",
                   "Natural Language :: English",
                   "Topic :: Other/Nonlisted Topic"], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='rice box chinese',
      author='Alan Hoey',
      author_email='alan.hoey@teamrubber.com',
      url='http://freespace.virgin.net/kuanwai.law/page3.html',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
	  'setuptools',
          # -*- Extra requirements: -*-      
      ],
      entry_points={
      'console_scripts': [
                  'special = ricebox.special:get',
              ],
      },
      )
