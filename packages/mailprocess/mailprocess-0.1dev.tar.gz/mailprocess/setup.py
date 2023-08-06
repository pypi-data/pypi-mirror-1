from setuptools import setup, find_packages

version = '0.1'

setup(name='mailprocess',
      version=version,
      description="A univseral tool for reading and processing of email",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Daniel Nouri',
      author_email='daniel.nouri@gmail.com',
      url='http://pypi.python.org/pypi/mailprocess',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=['mailman'],
      entry_points="""
      [console_scripts]
          mailprocess=mailprocess.main:main
      """,
      test_suite='nose.collector',
      )
