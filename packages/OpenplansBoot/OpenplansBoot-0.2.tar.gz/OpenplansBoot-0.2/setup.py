from setuptools import setup, find_packages

version = '0.2'

setup(name='OpenplansBoot',
      version=version,
      description="Creates new Openplans site deployment setup",
      long_description=open('README.txt').read(),
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='TOPP openplans opencore open planning project openplans.org',
      author='TOPP',
      author_email='info@openplans.org',
      url='http://www.openplans.org/projects/opencore',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "tempita",
      ],
      entry_points="""
      [console_scripts]
      new_openplans_site = openplansboot.newsite:main
      """,
      )
      
