from setuptools import setup, find_packages
import sys, os

# read the description from the file
try:
    description = file(os.path.join(os.path.dirname(__file__), 'README.txt')).read()
except:
    description = '' 

version = "0.2"

setup(name='CAPTCHAmiddleware',
      version=version,
      description="put CAPTCHAs on forms",
      long_description=description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org/hg',
      license="GPL",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
         'lxmlmiddleware',
         'skimpygimpy'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      example-captcha = captchamiddleware.example:factory
      """,
      )
      
