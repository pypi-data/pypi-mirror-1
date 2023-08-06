from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='TemplateTemplate',
      version=version,
      description="paste template for a paste template",
      long_description="""\
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='template',
      author='Jeff Hammel',
      author_email='jhammel@openplans.org',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[ 'PasteScript', ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.paster_create_template]
      template = templatetemplate:PasteScriptTemplateTemplate
      """,
      )
      
