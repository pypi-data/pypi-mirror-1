from setuptools import setup, find_packages
import os

version = '1.1.4'

setup(name='operun.linkportlet',
      version=version,
      description="Display Links selected from a Link collection inside a Portlet",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
	"Intended Audience :: End Users/Desktop",
	"Intended Audience :: System Administrators",
	"License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords='Plone Portlet Links',
      author='Stefan Antonelli',
      author_email='stefan.antonelli@operun.de',
      url='http://svn.operun.de/svn/operun.linkportlet',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['operun'],
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
