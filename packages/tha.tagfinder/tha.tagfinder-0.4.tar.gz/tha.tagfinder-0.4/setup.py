from setuptools import setup, find_packages
import os.path

version = '0.4'

long_description = '\n\n'.join([
    open('README.txt').read(),
    open(os.path.join('src', 'tha', 'tagfinder', 'USAGE.txt')).read(),
    open('TODO.txt').read(),
    open('CHANGES.txt').read(),
    ])

setup(name='tha.tagfinder',
      version=version,
      description="",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[],
      keywords=[],
      author='Reinout van Rees, The Health Agency',
      author_email='techniek@thehealthagency.com',
      url='http://www.thehealthagency.com',
      license='',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['tha'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # Add extra requirements here
                        ],
      extras_require = {
          'test': ['z3c.testsetup>=0.3'],
          },
      entry_points={
          'console_scripts': [
          ]},
      )
