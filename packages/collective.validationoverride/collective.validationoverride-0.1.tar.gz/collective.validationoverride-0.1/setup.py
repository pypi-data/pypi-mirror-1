from setuptools import setup, find_packages
import os

version = '0.1'

tests_require = ['collective.testcaselayer']

setup(name='collective.validationoverride',
      version=version,
      description="Allow AT field validatiuon to fail for users who have an override permission",
      long_description='\n'.join(
          open(os.path.join(*path)).read() for path in [
              ("src", "collective", "validationoverride", "README.txt"),
              ("docs", "HISTORY.txt"), ("docs", "TODO.txt")]),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Ross Patterson',
      author_email='me@rpatterson.net',
      url='http://pypi.python.org/pypi/collective.validationoverride',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir = {'':'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      tests_require=tests_require,
      extras_require={'tests': tests_require},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
