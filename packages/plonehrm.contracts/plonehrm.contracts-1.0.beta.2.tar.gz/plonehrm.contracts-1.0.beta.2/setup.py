from setuptools import setup, find_packages
import os.path

versionfile = os.path.join('plonehrm', 'contracts', 'version.txt')
version = open(versionfile).read().strip()

setup(name='plonehrm.contracts',
      version=version,
      description="",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Zest Software',
      author_email='',
      url='http://zestsoftware.nl',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plonehrm'],
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
