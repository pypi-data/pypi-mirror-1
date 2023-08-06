from setuptools import setup, find_packages
import os

version = '1.0.1'

setup(name='redturtle.fss',
      version=version,
      description="Simply apply FileSystemStorage strategies (iw.fss) to basic Plone content types.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='iw fss plone storage file image',
      author='RedTurtle Technology',
      author_email='info@redturtle.net',
      url='https://code.redturtle.it/svn/redturtle/redturtle.fss',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['redturtle'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
