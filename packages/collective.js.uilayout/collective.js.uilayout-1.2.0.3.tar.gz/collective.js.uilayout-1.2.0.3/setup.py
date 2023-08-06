from setuptools import setup, find_packages
import os

version = '1.2.0.3'

setup(name='collective.js.uilayout',
      version=version,
      description="UI.Layout JQuery plugin integration in portal_javascript",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Plone",
        ],
      keywords='Plone, jQuery',
      author='Gerhard Weis',
      author_email='gweis@gmx.at',
      url='http://plone.org/products/collective.js.uilayout',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.js'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFCore',
          'collective.js.jqueryui'
      ],
)

