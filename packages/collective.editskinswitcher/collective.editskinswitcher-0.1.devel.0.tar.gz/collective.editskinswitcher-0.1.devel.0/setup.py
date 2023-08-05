from setuptools import setup, find_packages
import os

versionfile = open(os.path.join('collective', 'editskinswitcher', 'version.txt'))
version = versionfile.read().strip()
versionfile.close()

setup(name='collective.editskinswitcher',
      version=version,
      description="Switch skins",
      long_description="""\
Switch skins based on e.g. urls or a cookie.""",
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Maurits van Rees',
      author_email='m.van.rees@zestsoftware.nl',
      url="''",
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
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
