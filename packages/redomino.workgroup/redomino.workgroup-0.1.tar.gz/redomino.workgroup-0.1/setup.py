from setuptools import setup, find_packages

version = '0.1'

setup(name='redomino.workgroup',
      version=version,
      description="This product provides a special workgroup mode for the normal Plone Folder to permit the creation of local users.",
      long_description="""\
These users will be only available in their workgroup and a local permission will be required to add them.
So local workgroup administrators will be allowes to add users without asking site managers.

If the workgroup folder is deleted on moved users will be deleted or moved.

Local users have the Member role only in their Folder, so you can avoid access to other areas of the portal.

This product does not provide new content types but can be applied on existing ones.
It has been developed using the ZCA and it is based on remember/membrane.
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
