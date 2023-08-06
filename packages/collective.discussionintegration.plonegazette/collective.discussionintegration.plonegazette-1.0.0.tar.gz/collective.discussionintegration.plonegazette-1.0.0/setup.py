from setuptools import setup, find_packages
import os

version = '1.0.0'

setup(name='collective.discussionintegration.plonegazette',
      version=version,
      description="Makes possible the creation of the PloneGazette content types if there is an installation of plone.app.discussion in your instance",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='RedTurtle Tecnology',
      author_email='federica.delia@redturtle.net',
      url='http://svn.plone.org/svn/collective/collective.discussionintegration.plonegazette',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.discussionintegration'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.discussion',
          'Products.PloneGazette',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
