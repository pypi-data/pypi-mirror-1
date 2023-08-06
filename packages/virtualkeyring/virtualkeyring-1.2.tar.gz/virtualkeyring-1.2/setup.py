from setuptools import setup, find_packages
import sys, os

version = '1.2'

setup(name='virtualkeyring',
      version=version,
      description="Strong domain-specific passwords generator",
      long_description=file("README.txt").read(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Information Technology',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          ],
      keywords='hash sha1 password generator keyring master',
      author='Olivier Grisel',
      author_email='olivier.grisel@ensta.org',
      url='http://oliviergrisel.name/virtualkeyring',
      license='GPLv3',
      py_modules = ['virtualkeyring'],
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points={
        'console_scripts': ['vkr = virtualkeyring:main'],
        'setuptools.installation': [
            'eggsecutable = virtualkeyring:main'],
      },
      test_suite="tests.test_suite",
     )
