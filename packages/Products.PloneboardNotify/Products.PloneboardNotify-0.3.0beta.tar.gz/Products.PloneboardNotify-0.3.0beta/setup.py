from setuptools import setup, find_packages
import os

version = '0.3.0'

setup(name='Products.PloneboardNotify',
      version=version,
      description="A configurable product that rely on Zope 3 events, for sending emails when new message is added on Ploneboard forum",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='ploneboard forum event notify',
      author='keul',
      author_email='luca.fabbri@redturtle.net',
      url='http://svn.plone.org/svn/collective/Products.PloneboardNotify',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          #'Products.Ploneboard',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [distutils.setup_keywords]
      paster_plugins = setuptools.dist:assert_string_list

      [egg_info.writers]
      paster_plugins.txt = setuptools.command.egg_info:write_arg
      """,
      paster_plugins = ["ZopeSkel"],
      )
