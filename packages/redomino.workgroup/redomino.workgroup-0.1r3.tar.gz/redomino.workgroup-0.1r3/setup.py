from setuptools import setup, find_packages
import os

version = '0.1r3'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

setup(name='redomino.workgroup',
      version=version,
      description="This product provides a special workgroup mode for the normal Plone Folder to permit the creation of local users.",
      long_description=longdesc,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Davide Moro (Redomino)',
      author_email='davide.moro@redomino.com',
      url='http://www.redomino.com/it/labs/progetti/redomino-workgroup',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['redomino'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.browserlayer',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
