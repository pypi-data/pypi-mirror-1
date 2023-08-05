from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='Mocky',
      version=version,
      description="Mocky is a class that helps you create mock objects for "
      "use in doctests.",
      long_description=open(os.path.join('mocky', 'mocky.py')).read(),
      classifiers=['Topic :: Software Development :: Testing'],
      keywords='test doctest mock',
      author='Daniel Nouri',
      author_email='daniel.nouri@gmail.com',
      url='http://cheeseshop.python.org/pypi/Mocky',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
      ],
      entry_points="""
      """,
      )
