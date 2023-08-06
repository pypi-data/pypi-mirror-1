from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='kss.plugin.cns',
      version=version,
      description="Various KSS plugins",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='kss',
      author='Matous Hora',
      author_email='matous.hora@dms4u.cz',
      url='http://svn.plone.org/svn/collective/kss.plugin.cns',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['kss', 'kss.plugin'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'kss.core',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
