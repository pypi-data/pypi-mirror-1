from setuptools import setup, find_packages

version = '0.2.1'

setup(name='genshi_view',
      version=version,
      description="paste template for a view using webob + genshi",
      long_description="""\
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org/hg/genshi_view',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[ 'PasteScript' ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.paster_create_template]
      genshi_view = genshi_view:GenshiViewTemplate
      """,
      )
      
