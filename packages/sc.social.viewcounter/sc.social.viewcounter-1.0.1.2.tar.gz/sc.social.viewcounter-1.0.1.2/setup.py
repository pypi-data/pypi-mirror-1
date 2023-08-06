from setuptools import setup, find_packages
import os

version = open(os.path.join("sc", "social", "viewcounter", "version.txt")).read().strip()

setup(name='sc.social.viewcounter',
      version=version,
      description="Logger and reporter for page views",
      long_description=open(os.path.join("sc","social","viewcounter","README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone socialtools ranking access',
      author='Simples Consultoria',
      author_email='products@simplesconsultoria.com.br',
      url='http://www.simplesconsultoria.com.br',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['sc', 'sc.social'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'pysqlite',
          'sqlalchemy',
          'z3c.saconfig',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
