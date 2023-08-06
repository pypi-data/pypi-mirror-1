from setuptools import setup, find_packages

try:
    description = file('README.txt').read()
except IOError: 
    description = ''

version = "0.1"

setup(name='commentator',
      version=version,
      description="WSGI commenting middleware",
      long_description=description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org/hg/commentator',
      license="GPL",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
         'WebOb',	
         'Paste',
         'PasteScript',
         'genshi',
#         'CouchDB'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      commentator = commentator.example:factory
      """,
      )
      
