from setuptools import setup, find_packages
import os

version = '0.8.6a2'

setup(name='themetweaker.themeswitcher',
      version=version,
      description="A product for switching themes in Plone.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.4",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
        ],
      keywords='themeswitcher themetweaker theme switcher weblion',
      author='WebLion Group, Penn State University',
      author_email='support@weblion.psu.edu',
      url='https://weblion.psu.edu/trac/weblion/wiki/ThemeSwitcher',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['themetweaker'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.browserlayer==1.0.0',
          'z3c.unconfigure==1.0.1',
          # 'sd.common' # subversion?
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
