from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='teamrubber.snakeskin',
      version=version,
      description="A paster template for creating derivative themes.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Matthew Wilkes',
      author_email='matt.wilkes@teamrubber.com',
      url='http://www.teamrubber.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['teamrubber'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'ZopeSkel',
        'pastescript',
        'Cheetah'
      ],
      entry_points="""
        [paste.paster_create_template]
        plone3_snakeskin = teamrubber.snakeskin.snakeskin:SnakeSkin"""
      )
