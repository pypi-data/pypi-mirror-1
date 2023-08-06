from setuptools import setup, find_packages
import os

version = '1.0b3'

setup(name='collective.portlet.workflowsteps',
      version=version,
      description="A Plone portlet for showing 'next steps' in a workflow. May include rich text tied to the workflow state and transitions with descriptions.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone portlet workflow',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://pypi.python.org/pypi//collective.portlet.workflowsteps',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.portlets',
          'plone.portlets',
          'zope.app.publisher',
          'zope.schema',
          'zope.formlib',
          'plone.app.form',
          'Products.CMFCore',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
