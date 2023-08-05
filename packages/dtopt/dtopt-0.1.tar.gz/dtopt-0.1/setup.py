from setuptools import setup, find_packages
import sys, os

version = '0.1'

index_txt = os.path.join(os.path.dirname(__file__), 'docs', 'index.txt')
long_desc = '\n'.join(open(index_txt).readlines()[2:])

setup(name='dtopt',
      version=version,
      description="Add options to doctest examples while they are running",
      long_description=long_desc,
      classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Testing",
      ],
      keywords='doctest',
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      url='http://pypi.python.org/pypi/dtopt/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      )
