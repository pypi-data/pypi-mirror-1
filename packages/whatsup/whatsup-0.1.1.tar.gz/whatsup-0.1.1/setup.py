from setuptools import setup, find_packages

try:
    description = file('README.txt').read()
except IOError:
    description = ''

version = "0.1.1"

setup(name='whatsup',
      version=version,
      description="Outage Escalation Tool and Site Contact Info",
      long_description=description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Chris Patterson and Jeff Hammel',
      author_email='jhammel@openplans.org',
      url='https://projects.openplans.org/whatsup', 
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
         'martINI'
      ],
      dependency_links = [ 'https://svn.openplans.org/svn/standalone/martINI#egg=martINI' ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = whatsup.factory:factory
      """,
      )
      
