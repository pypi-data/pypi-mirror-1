from setuptools import setup, find_packages

version = '0.2.5'

setup(name='mailtoplone.base',
      version=version,
      description="basic package for mailtoplone",
      long_description=file("README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Hans-Peter Locher',
      author_email='hans-peter.locher@inquant.de',
      url='https://svn.plone.org/svn/collective/mailtoplone/mailtoplone.base',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['mailtoplone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'icalendar',
          'dateutil',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
