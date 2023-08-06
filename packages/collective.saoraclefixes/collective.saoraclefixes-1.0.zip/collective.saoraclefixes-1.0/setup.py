from setuptools import setup, find_packages

version = '1.0'

setup(name='collective.saoraclefixes',
      version=version,
      description="Fixes for the SQLAlchemy 0.4 and 0.5 Oracle driver",
      long_description=open("README.txt").read() + "\n" + 
                       open("HISTORY.txt").read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='sqlalchemy oracle reservedwords quoting bindparam',
      author='Jarn AS',
      author_email='info@jarn.com',
      url='http://svn.plone.org/svn/collective/collective.saoraclefixes',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'SQLAlchemy >= 0.4dev, < 0.6dev'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
