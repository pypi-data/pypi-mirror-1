from setuptools import setup, find_packages
import os.path

versionfile = os.path.join('xm', 'theme', 'version.txt')
version = open(versionfile).read().strip()

setup(name='xm.theme',
      version=version,
      description="Theme for eXtremeManagement",
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
      keywords='web zope plone theme',
      author='Zest Software',
      author_email='info@zestsoftware.nl',
      url='http://zestsoftware.nl',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['xm'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Products.eXtremeManagement>=2.0alpha3',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
