from setuptools import setup, find_packages

version = '0.2'

tests_require = ['collective.testcaselayer']

readme = open('README.txt')
long_description = readme.read()
readme.close()

setup(name='p4a.ploneimage',
      version=version,
      description="",
      long_description=long_description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='http://svn.plone.org/svn/plone/plone.example',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['p4a'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'p4a.common',
          'p4a.image',
      ],
      tests_require=tests_require,
      extras_require={'tests': tests_require},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
